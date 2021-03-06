# Copyright 2011-2012 James McCauley
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
An L2 learning switch.

It is derived from one written live for an SDN crash course.
It is somwhat similar to NOX's pyswitch in that it installs
exact-match rules for each flow.
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpid_to_str
from pox.lib.util import str_to_bool
import time
from pox.lib.addresses import IPAddr
from pox.lib.addresses import EthAddr

log = core.getLogger()

# We don't want to flood immediately when a switch connects.
# Can be overriden on commandline.
_flood_delay = 0

# A set of ports to block
block_ports_dynamic = set() 	#synamic firewall which we can choose when we want to run the program
block_ports_static = []		#static port that we can choose in the code to block

class LearningSwitch (object):
  """
  The learning switch "brain" associated with a single OpenFlow switch.

  When we see a packet, we'd like to output it on a port which will
  eventually lead to the destination.  To accomplish this, we build a
  table that maps addresses to ports.

  We populate the table by observing traffic.  When we see a packet
  from some source coming from some port, we know that source is out
  that port.

  When we want to forward traffic, we look up the desintation in our
  table.  If we don't know the port, we simply send the message out
  all ports except the one it came in on.  (In the presence of loops,
  this is bad!).

  In short, our algorithm looks like this:

  For each packet from the switch:
  1) Use source address and switch port to update address/port table
  2) Is transparent = False and either Ethertype is LLDP or the packet's
     destination address is a Bridge Filtered address?
     Yes:
        2a) Drop packet -- don't forward link-local traffic (LLDP, 802.1x)
            DONE
  3) Is destination multicast?
     Yes:
        3a) Flood the packet
            DONE
  4) Port for destination address in our address/port table?
     No:
        4a) Flood the packet
            DONE
  5) Is output port the same as input port?
     Yes:
        5a) Drop packet and similar ones for a while
  6) Install flow table entry in the switch so that this
     flow goes out the appopriate port
     6a) Send the packet out appropriate port
  """
  def __init__ (self, connection, transparent):
    # Switch we'll be adding L2 learning switch capabilities to
    self.connection = connection
    self.transparent = transparent

    # Our table
    self.macToPort = {}

    # We want to hear PacketIn messages, so we listen
    # to the connection
    connection.addListeners(self)

    # We just use this to know when to log a helpful message
    self.hold_down_expired = _flood_delay == 0

    #log.debug("Initializing LearningSwitch, transparent=%s",
    #          str(self.transparent))

    #This function can check for specific ip as destination.
  def flow_checker (self, event, packet, port):
    eth_packet = event.parsed
    ip_packet = eth_packet.find('ipv4')
  
    if ip_packet is None:
	    msg = of.ofp_flow_mod()
	    msg.match = of.ofp_match.from_packet(packet, event.port)
	    msg.idle_timeout = 10
	    msg.hard_timeout = 30
	    msg.actions.append(of.ofp_action_output(port = port))
	    msg.data = event.ofp # 6a
	    self.connection.send(msg)
	    return
    tcpp = event.parsed.find('tcp') 

    srcip = (ip_packet.srcip).toStr()
    dstip = (ip_packet.dstip).toStr()
    protocol = ip_packet.protocol
    if protocol == 1: #icmp
	    print("icmp")
	    self.send_ofmod_forward(_called_from = 'packet_in',
                              conn = event.connection,
                              nw_src = srcip,
                              nw_dst = dstip,
                              nw_proto = protocol,
                              tp_src = '-1',
                              tp_dst = '-1',
                              fport = of.OFPP_ALL,
                              duration = [0,0],
                              buffer_id = event.ofp.buffer_id )
            print 'icmp rule is inserted!'
	    return

    if dstip == '10.0.2.2' and event.dpid==3:
	    """           		 
	    msg = of.ofp_flow_mod()
	    msg.match = of.ofp_match.from_packet(packet, event.port)
	    msg.idle_timeout = 10
	    msg.hard_timeout = 30
	    msg.actions.append(of.ofp_action_output(port = port))
	    msg.data = event.ofp # 6a
	    self.connection.send(msg)
	    print ("hello1")
	    print(packet.dst)
	    """
	    
	    msg = of.ofp_flow_mod()
	    msg.priority = 42
	    msg.match.dl_type = 0x800
	    msg.match.dl_dst = EthAddr('00:00:00:01:02:00')
	    msg.actions.append(of.ofp_action_output(port = 2))
	    self.connection.send(msg)
	    
	    print("============================== 1")
	    return
    if dstip == '10.0.2.2' and event.dpid==2:
	    """
	    msg = of.ofp_flow_mod()
	    msg.match = of.ofp_match.from_packet(packet, event.port)
	    msg.idle_timeout = 10
	    msg.hard_timeout = 30
	    msg.actions.append(of.ofp_action_output(port = port))
	    msg.data = event.ofp # 6a
	    self.connection.send(msg)
	    print ("hello2")
	    print(packet.dst)
	    """
	    
	    msg = of.ofp_flow_mod()
	    msg.priority = 42
	    msg.match.dl_type = 0x800
	    msg.match.nw_dst = IPAddr('10.0.2.3')
	    msg.match.dl_dst = EthAddr('00:00:00:01:02:03')
	    msg.actions.append(of.ofp_action_output(port = 3))
	    self.connection.send(msg)
	    
	    print("============================== 2")
	    return
    if dstip == '10.0.2.2' and event.dpid==1 and packet.src != "10.0.2.0":
	    """
	    msg = of.ofp_flow_mod()
	    msg.match = of.ofp_match.from_packet(packet, event.port)
	    msg.idle_timeout = 10
	    msg.hard_timeout = 30
	    msg.actions.append(of.ofp_action_output(port = port))
	    msg.data = event.ofp # 6a
	    self.connection.send(msg)
	    print ("hello3")
	    print(packet.dst)
	    """
            
	    msg = of.ofp_flow_mod()
	    msg.priority = 42
	    msg.match.dl_type = 0x800
	    msg.match.dl_dst = EthAddr('00:00:00:01:02:00')
	    msg.actions.append(of.ofp_action_output(port = 1))
	    self.connection.send(msg)
	    return
    msg = of.ofp_flow_mod()
    msg.match = of.ofp_match.from_packet(packet, event.port)
    msg.idle_timeout = 10
    msg.hard_timeout = 30
    msg.actions.append(of.ofp_action_output(port = port))
    msg.data = event.ofp # 6a
    self.connection.send(msg)

  def send_ofmod_forward(self, _called_from, conn, nw_src, nw_dst, nw_proto, tp_src,
                         tp_dst, fport, duration, buffer_id = None):
    msg = of.ofp_flow_mod()
    #msg.match = of.ofp_match.from_packet(packet)
    msg.priority = 0x7000
    #msg.match = of.ofp_match(dl_type = pkt.ethernet.IP_TYPE, nw_proto = pkt.ipv4.UDP_PROTOCOL, nw_dst=IPAddr(nw_dst))
    msg.match.dl_type = 0x800 # Ethertype / length (e.g. 0x0800 = IPv4)
    msg.match.nw_src = IPAddr(nw_src)
    msg.match.nw_dst = IPAddr(nw_dst)
    msg.match.nw_proto = int(nw_proto) #17:UDP, 6:TCP
    if tp_src != '-1':
      msg.match.tp_src = int(tp_src)
    if tp_dst != '-1':
      msg.match.tp_dst = int(tp_dst)
    msg.idle_timeout = duration[0]
    msg.hard_timeout = duration[1]
    #print "event.ofp.buffer_id: ", event.ofp.buffer_id
    if _called_from == 'packet_in':
      msg.buffer_id = buffer_id
    msg.actions.append(of.ofp_action_output(port = fport))
    conn.send(msg)
    print '\nsend_ofmod_forward to sw_dpid=%s' % conn.dpid
    print 'wcs: src_ip=%s, dst_ip=%s, nw_proto=%s, tp_src=%s, tp_dst=%s' % (nw_src,nw_dst,nw_proto,tp_src,tp_dst)
    print 'acts: fport=%s\n' % fport


  def _handle_PacketIn (self, event):
	    """
	    Handle packet in messages from the switch to implement above algorithm.
	    """

	    packet = event.parsed



	    def flood (message = None):
	      """ Floods the packet """
	      msg = of.ofp_packet_out()
	      if time.time() - self.connection.connect_time >= _flood_delay:
		# Only flood if we've been connected for a little while...

		if self.hold_down_expired is False:
		  # Oh yes it is!
		  self.hold_down_expired = True
		  log.info("%s: Flood hold-down expired -- flooding",
		      dpid_to_str(event.dpid))

		if message is not None: log.debug(message)
		#log.debug("%i: flood %s -> %s", event.dpid,packet.src,packet.dst)
		# OFPP_FLOOD is optional; on some switches you may need to change
		# this to OFPP_ALL.
		msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
	      else:
		pass
		#log.info("Holding down flood for %s", dpid_to_str(event.dpid))
	      msg.data = event.ofp
	      msg.in_port = event.port
	      self.connection.send(msg)

	    def drop (duration = None):
	      """
	      Drops this packet and optionally installs a flow to continue
	      dropping similar ones for a while
	      """
	      if duration is not None:
		if not isinstance(duration, tuple):
		  duration = (duration,duration)
		msg = of.ofp_flow_mod()
		msg.match = of.ofp_match.from_packet(packet)
		msg.idle_timeout = duration[0]
		msg.hard_timeout = duration[1]
		msg.buffer_id = event.ofp.buffer_id
		self.connection.send(msg)
	      elif event.ofp.buffer_id is not None:
		msg = of.ofp_packet_out()
		msg.buffer_id = event.ofp.buffer_id
		msg.in_port = event.port
		self.connection.send(msg)

	    #This function can check for specific ip as destination.
	    def flow_checker (self, event):
	      eth_packet = event.parsed
	      ip_packet = eth_packet.find('ipv4')
	  
	      if ip_packet is None:
		#print '_handle_PacketIn:: doesnt have ip_payload; eth_packet=%s' % eth_packet
		return
	      srcip = (ip_packet.srcip).toStr()
	      dstip = (ip_packet.dstip).toStr()
	      protocol = ip_packet.protocol
	      #print '_handle_PacketIn:: rxed from sw_dpid=%s; srcip=%s, dstip=%s, protocol=%s' % 						(event.connection.dpid,srcip,dstip,protocol)
	      if protocol == 1: #icmp
		    #print 'rxed icmp_packet=%s' % ip_packet.payload
		    print("icmp")

	      #print "srcip= %s, dstip= %s" % (srcip, dstip)
	      if dstip == '10.0.2.2':
		    print ("hello")


	    self.macToPort[packet.src] = event.port # 1

	    if not self.transparent: # 2
	      if packet.type == packet.LLDP_TYPE or packet.dst.isBridgeFiltered():
		drop() # 2a
		return

	    if packet.dst.is_multicast:
	      flood() # 3a
	    else:
	      if packet.dst not in self.macToPort: # 4
		flood("Port for %s unknown -- flooding" % (packet.dst,)) # 4a
	      else:
		port = self.macToPort[packet.dst]
		if port == event.port: # 5
		  # 5a
		  log.warning("Same port for packet from %s -> %s on %s.%s.  Drop."
		      % (packet.src, packet.dst, dpid_to_str(event.dpid), port))
		  drop(10)
		  return
		# 6
		log.debug("installing flow for %s.%i -> %s.%i" %
		          (packet.src, event.port, packet.dst, port))
		msg = of.ofp_flow_mod()
		msg.match = of.ofp_match.from_packet(packet, event.port)
		msg.idle_timeout = 10
		msg.hard_timeout = 30
		msg.actions.append(of.ofp_action_output(port = port))
		msg.data = event.ofp # 6a
		self.connection.send(msg)
		#self.flow_checker(event, packet, port)
		


class l2_learning (object):
  """
  Waits for OpenFlow switches to connect and makes them learning switches.
  """
  def __init__ (self, transparent):
    core.openflow.addListeners(self)
    self.transparent = transparent

  def _handle_ConnectionUp (self, event):
    log.debug("Connection %s" % (event.connection,))
    print "Switch %s has come up." % event.dpid
    LearningSwitch(event.connection, self.transparent)

  def _handle_ConnectionDown (self, event):
    print "Switch %s is Down" % event.dpid




   
#The functiopn to block the defined ports
def block_handler (event):
  # Handles packet events and kills the ones with a blocked port number
  tcpp = event.parsed.find('tcp')
  if not tcpp: return # Not TCP
  if tcpp.srcport in block_ports_dynamic or tcpp.dstport in block_ports_dynamic:
    # Halt the event, stopping l2_learning from seeing it
    # (and installing a table entry for it)
    core.getLogger("blocker").debug("Blocked TCP %s <-> %s", tcpp.srcport, tcpp.dstport)
    event.halt = True
  if tcpp.srcport in block_ports_static or tcpp.dstport in block_ports_static:
    # Halt the event, stopping l2_learning from seeing it
    # (and installing a table entry for it)
    core.getLogger("blocker").debug("Blocked TCP %s <-> %s", tcpp.srcport, tcpp.dstport)
    event.halt = True



def launch (transparent=False, hold_down=_flood_delay, ports = ''):
  """
  Starts an L2 learning switch.
  """
  block_ports_dynamic.update(int(x) for x in ports.replace(",", " ").split())
  try:
    global _flood_delay
    _flood_delay = int(str(hold_down), 10)
    assert _flood_delay >= 0
  except:
    raise RuntimeError("Expected hold-down to be a number")

  core.registerNew(l2_learning, str_to_bool(transparent))
  core.openflow.addListenerByName("PacketIn", block_handler)
