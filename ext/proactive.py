from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpid_to_str
from pox.lib.util import str_to_bool
import time
from pox.lib.addresses import IPAddr
from pox.lib.addresses import EthAddr
import csv
import sys
import pox.lib.packet as pkt




log = core.getLogger()
table = {}

states = [0,0,0,0]

class Simples (object):
  def __init__ (self, connection):
    self.connection = connection
    connection.addListeners(self)

  def _handle_PacketIn (self, event):
	packet = event.parsed
	eth_packet = event.parsed
	ip_packet = eth_packet.find('ipv4')
	if ip_packet is None:
		return
	protocol = ip_packet.protocol
	if protocol == 1: #icmp
		
		print (event.connection.dpid)
		"""
		print (ip_packet.srcip)
		print (ip_packet.dstip)
		print (ip_packet.tos)
		print (ip_packet.id)
		print (ip_packet.flags)
		print (ip_packet.frag)
		print (ip_packet.ttl)
		print (ip_packet.protocol)
		print (ip_packet.csum)
		packet_in = event.ofp # The actual ofp_packet_in message.
		msg = of.ofp_packet_out()
		msg.buffer_id = event.ofp.buffer_id
		msg.in_port = packet_in.in_port

		# Add an action to send to the specified port
		action = of.ofp_action_output(port = of.OFPP_FLOOD)
		msg.actions.append(action)
	        # Send message to switch
        	self.connection.send(msg)
		"""
	        icmp = pkt.icmp()
	        icmp.type = pkt.TYPE_ECHO_REPLY
    	        icmp.payload = packet.find("icmp").payload

	        # Make the IP packet around it
	        ipp = pkt.ipv4()
	        ipp.protocol = ipp.ICMP_PROTOCOL
	        ipp.srcip = packet.find("ipv4").dstip
	        ipp.dstip = packet.find("ipv4").srcip

	        # Ethernet around that...
	        e = pkt.ethernet()
	        e.src = packet.dst
	        e.dst = packet.src
	        e.type = e.IP_TYPE

	        # Hook them up...
	        ipp.payload = icmp
	        e.payload = ipp

	        # Send it back to the input port
	        msg = of.ofp_packet_out()
	        msg.actions.append(of.ofp_action_output(port = of.OFPP_IN_PORT))
	        msg.data = e.pack()
	        msg.in_port = event.port
	        event.connection.send(msg)

	        #log.debug("%s pinged %s", ipp.dstip, ipp.srcip)
		#deleting rules test
		if (ip_packet.srcip == IPAddr("10.0.2.1")):
		  	    msg = of.ofp_flow_mod(command=of.OFPFC_DELETE)
			    match = of.ofp_match()
			    match.in_port = None
			    match.dl_type = 0x0800
			    match.nw_proto = 6
			    match.nw_src = IPAddr("10.0.2.0")
			    match.nw_dst = IPAddr("10.0.2.1")
			    match.tp_src = 50023
			    msg.match = match
			    msg.idle_timeout = 0
			    msg.hard_timeout = 0
			    event.connection.send(msg)

		  	    msg = of.ofp_flow_mod(command=of.OFPFC_DELETE)
			    match = of.ofp_match()
			    match.in_port = None
			    match.dl_type = 0x0800
			    match.nw_proto = 6
			    match.nw_src = IPAddr("10.0.2.1")
			    match.nw_dst = IPAddr("10.0.2.2")
			    match.tp_dst = 50023
			    msg.match = match
			    msg.idle_timeout = 0
			    msg.hard_timeout = 0
			    event.connection.send(msg)
			    	
		return
	
       
  def _handle_ConnectionUp (self, event):
	
	with open('/home/ubuntu/pox/ext/rules.csv', 'rb') as csvfile:
		rules = csv.reader(csvfile, delimiter=';', quotechar='|')
		for row in rules:
			if event.dpid == int (row[0]):
			    self._my_rule_installation(switch = row[0], 
							host_send = row[1], 
							host_receive = row[2], 
							host_forward = row[3],
							port_connection = int(row[4]))				
	


	with open('/home/ubuntu/pox/ext/generalrules.csv', 'rb') as csvfile:
		generalrules = csv.reader(csvfile, delimiter=';', quotechar='|')
		for row in generalrules:
			if event.dpid == int (row[0]):
			    self._my_rule_installation_general(switch = row[0], 
							   host_send = row[1], 
							   host_receive = row[2], 
							   host_forward = row[3],
							   port_connection = None)
	
	
	    
  def _my_install_change_new(self,switch,out_port,srcport,src_ip,dst_ip,new_ipaddr,new_macaddr):
  	    msg = of.ofp_flow_mod()
            match = of.ofp_match()
            match.in_port = None
	    match.dl_type = 0x0800
	    match.nw_proto = 6
	    match.nw_src = src_ip
	    match.nw_dst = dst_ip
	    match.tp_src = srcport
            msg.match = match
            msg.idle_timeout = 0
            msg.hard_timeout = 0
	    msg.actions.append(of.ofp_action_nw_addr(nw_addr = IPAddr(new_ipaddr), type=6))  #type={6:mod_nw_src, 7:mod_nw_dst}
	    msg.actions.append(of.ofp_action_dl_addr(dl_addr = EthAddr(new_macaddr), type=4))#type={4:mod_dl_src, 5:mod_dl_dst}
            msg.actions.append(of.ofp_action_output(port = out_port))
            core.openflow.sendToDPID(switch,msg)


  def _my_install_change_new2(self,switch,out_port,dstport,src_ip,dst_ip,new_ipaddr,new_macaddr):
  	    msg = of.ofp_flow_mod()
            match = of.ofp_match()
            match.in_port = None
	    match.dl_type = 0x0800
	    match.nw_proto = 6
	    match.nw_src = src_ip
	    match.nw_dst = dst_ip
	    match.tp_dst = dstport
            msg.match = match
            msg.idle_timeout = 0
            msg.hard_timeout = 0
	    msg.actions.append(of.ofp_action_nw_addr(nw_addr = IPAddr(new_ipaddr), type=7))  #type={6:mod_nw_src, 7:mod_nw_dst}
	    msg.actions.append(of.ofp_action_dl_addr(dl_addr = EthAddr(new_macaddr), type=5))#type={4:mod_dl_src, 5:mod_dl_dst}
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
  """
  def _my_rule_installation(self, switch, host_send, host_receive, host_forward, port_connection):
	with open('/home/ubuntu/pox/ext/staticmapping.csv', 'rb') as csvfile:
		mapping = csv.reader(csvfile, delimiter=';', quotechar='|')
		for row in mapping:
			if row[0] == host_send :
				ip_host_send = row[1]
				mac_host_send = row[2]
				switch_host_send = int (row[3])
				switch_port_host_send = int (row[4])
			if row[0] == host_receive :
				ip_host_receive = row[1]
				mac_host_receive = row[2]
				switch_host_receive = int (row[3])
				switch_port_host_receive = int (row[4])
			if row[0] == host_forward :
				ip_host_forward = row[1]
				mac_host_forward = row[2]
				switch_host_forward = int (row[3])
				switch_port_host_forward = int (row[4])




	with open('/home/ubuntu/pox/ext/port_forwarding.csv', 'rb') as csvfile:
		port_handling = csv.reader(csvfile, delimiter=';', quotechar='|')
		for row in port_handling:
			if row[0] == switch:
				if row[1] == host_forward:
					if row[2] == host_send:
						forward_to_send_port = int (row[3])
				if row[1] == host_send:
					if row[2] == host_forward:
						send_to_forward_port = int (row[3])



	self._my_install_change_new(switch = int (switch),
		out_port = forward_to_send_port, 
		srcport = port_connection,
		src_ip = ip_host_forward,
		dst_ip = ip_host_send,
		new_ipaddr = ip_host_receive,
		new_macaddr = mac_host_receive)

	self._my_install_change_new2(switch = int (switch), 
		out_port = send_to_forward_port, 
		dstport = port_connection,
		src_ip = ip_host_send, 
		dst_ip = ip_host_receive,
		new_ipaddr = ip_host_forward,
		new_macaddr = mac_host_forward)
	
  """
  This function is used for rule installation for general on the switches.
  inputs to this function
  switch = switch number that we want to install the rule
  host_send = host that want to send the data
  host_receiver = host that we want to send data to
  host_forward = host that actually data forwarded to it
  port_connection = port number that we want to use for connection
  """
  def _my_rule_installation_general(self, switch, host_send, host_receive, host_forward, port_connection):
	with open('/home/ubuntu/pox/ext/staticmapping.csv', 'rb') as csvfile:
		mapping = csv.reader(csvfile, delimiter=';', quotechar='|')
		for row in mapping:
			if row[0] == host_send :
				ip_host_send = row[1]
				mac_host_send = row[2]
				switch_host_send = int (row[3])
				switch_port_host_send = int (row[4])
			if row[0] == host_receive :
				ip_host_receive = row[1]
				mac_host_receive = row[2]
				switch_host_receive = int (row[3])
				switch_port_host_receive = int (row[4])
			if row[0] == host_forward :
				ip_host_forward = row[1]
				mac_host_forward = row[2]
				switch_host_forward = int (row[3])
				switch_port_host_forward = int (row[4])




	with open('/home/ubuntu/pox/ext/port_forwarding.csv', 'rb') as csvfile:
		port_handling = csv.reader(csvfile, delimiter=';', quotechar='|')
		for row in port_handling:
			if row[0] == switch:
				if row[1] == host_forward:
					if row[2] == host_send:
						forward_to_send_port = int (row[3])
				if row[1] == host_send:
					if row[2] == host_forward:
						send_to_forward_port = int (row[3])



	self._my_install_change_new2(switch = int (switch),
		out_port = send_to_forward_port, 
		dstport = port_connection,
		src_ip = ip_host_send,
		dst_ip = ip_host_receive,
		new_ipaddr = ip_host_forward,
		new_macaddr = mac_host_forward)

	self._my_install_change_new(switch = int (switch), 
		out_port = forward_to_send_port, 
		srcport = port_connection,
		src_ip = ip_host_forward, 
		dst_ip = ip_host_send,
		new_ipaddr = ip_host_receive,
		new_macaddr = mac_host_receive)
	

def launch ():
    def start_switch (event):
        Simples(event.connection)
    
    core.openflow.addListenerByName("ConnectionUp", start_switch)


    #core.registerNew(Simples)
