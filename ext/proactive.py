from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpid_to_str
from pox.lib.util import str_to_bool
import time
from pox.lib.addresses import IPAddr
from pox.lib.addresses import EthAddr

log = core.getLogger()
table = {}

class Simples (object):
  def __init__ (self, connection):
    self.connection = connection
    connection.addListeners(self)

  def _handle_PacketIn (self, event):
	eth_packet = event.parsed
	ip_packet = eth_packet.find('ipv4')
	if ip_packet is None:
		return
	protocol = ip_packet.protocol
	if protocol == 1: #icmp
		packet_in = event.ofp # The actual ofp_packet_in message.

		msg = of.ofp_packet_out()
		msg.buffer_id = event.ofp.buffer_id
		msg.in_port = packet_in.in_port

		# Add an action to send to the specified port
		action = of.ofp_action_output(port = of.OFPP_FLOOD)
		msg.actions.append(action)
	        # Send message to switch
        	self.connection.send(msg)
		return
	
       
  def _handle_ConnectionUp (self, event):
    #self._install(event.connection.dpid,1,(2,3))
    #self._install(event.connection.dpid,2,(1,3))
    #self._install(event.connection.dpid,3,(1,2))
    #self._my_install(event.connection.dpid,1,3,50023)
    #self._my_install_change2(event.connection.dpid,4,1,50023)
    if event.dpid == 2:
	    
	    self._my_install_change_new(switch = event.connection.dpid,
				    out_port = 1, 
				    srcport = 50023,
				    ipaddr = '10.0.2.3',
				    macaddr = '00:00:00:01:02:03')
	    
	    self._my_install_change_new2(switch = event.connection.dpid, 
				     out_port = 4, 
				     dstport = 50023,
				     ipaddr = '10.0.2.4',
				     macaddr = '00:00:00:01:02:04')
	    
  def _my_install_change_new(self,switch,out_port,srcport,ipaddr,macaddr):
  	    msg = of.ofp_flow_mod()
            match = of.ofp_match()
            match.in_port = None
	    match.dl_type = 0x0800
	    match.nw_proto = 6
	    match.nw_src = "10.0.2.4"
	    match.nw_dst = "10.0.2.1"
	    match.tp_src = srcport
            msg.match = match
            msg.idle_timeout = 0
            msg.hard_timeout = 0
	    msg.actions.append(of.ofp_action_nw_addr(nw_addr = IPAddr(ipaddr), type=6))  #type={6:mod_nw_src, 7:mod_nw_dst}
	    msg.actions.append(of.ofp_action_dl_addr(dl_addr = EthAddr(macaddr), type=4))#type={4:mod_dl_src, 5:mod_dl_dst}
            msg.actions.append(of.ofp_action_output(port = out_port))
            core.openflow.sendToDPID(switch,msg)


  def _my_install_change_new2(self,switch,out_port,dstport,ipaddr,macaddr):
  	    msg = of.ofp_flow_mod()
            match = of.ofp_match()
            match.in_port = None
	    match.dl_type = 0x0800
	    match.nw_proto = 6
	    match.nw_src = "10.0.2.1"
	    match.nw_dst = "10.0.2.3"
	    match.tp_dst = dstport
            msg.match = match
            msg.idle_timeout = 0
            msg.hard_timeout = 0
	    msg.actions.append(of.ofp_action_nw_addr(nw_addr = IPAddr(ipaddr), type=7))  #type={6:mod_nw_src, 7:mod_nw_dst}
	    msg.actions.append(of.ofp_action_dl_addr(dl_addr = EthAddr(macaddr), type=5))#type={4:mod_dl_src, 5:mod_dl_dst}
            msg.actions.append(of.ofp_action_output(port = out_port))
            core.openflow.sendToDPID(switch,msg)

  """
  This function is used for rule installation on the switches.
  inputs to this function
  switch = switch number that we want to install the rule
  host_send = host that want to send the data
  host_receiver = host that we want to send data to
  host_forward = host that actually data forwarded to it
  port_connection = port number that we want to use for connection
   
  def _my_rule_installation(self, switch, host_send, host_receiver, host_forward, port_connection):
	    self._my_install_change(switch = event.connection.dpid,
	 			    in_port = 1, 
				    out_port = 4, 
				    dstport = 50023,
				    ipaddr = '10.0.2.4',
				    macaddr = '00:00:00:01:02:04')
	    self._my_install_change2(switch = event.connection.dpid,
				     in_port = 4, 
				     out_port = 1, 
				     srcport = 50023,
				     ipaddr = '10.0.2.3',
				     macaddr = '00:00:00:01:02:03')
	
  """
def launch ():
    def start_switch (event):
        Simples(event.connection)
    
    core.openflow.addListenerByName("ConnectionUp", start_switch)


    #core.registerNew(Simples)
