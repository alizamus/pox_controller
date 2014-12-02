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
  def __init__ (self):
    core.openflow.addListeners(self)
       
  def _handle_ConnectionUp (self, event):
    #self._install(event.connection.dpid,1,(2,3))
    #self._install(event.connection.dpid,2,(1,3))
    #self._install(event.connection.dpid,3,(1,2))
    self._my_install(event.connection.dpid,1,3,50023)
    self._my_install2(event.connection.dpid,3,1,50023)

  def _my_install(self,switch,in_port,out_port,dstport):
	  msg = of.ofp_flow_mod()
          match = of.ofp_match()
          match.in_port = in_port
	  match.dl_type = 0x0800
	  match.nw_proto = 6
	  match.tp_dst = dstport
          msg.match = match
          msg.idle_timeout = 0
          msg.hard_timeout = 0
          msg.actions.append(of.ofp_action_output(port = out_port))
          core.openflow.sendToDPID(switch,msg)

  def _my_install2(self,switch,in_port,out_port,srcport):
	  msg = of.ofp_flow_mod()
          match = of.ofp_match()
          match.in_port = in_port
	  match.dl_type = 0x0800
	  match.nw_proto = 6
	  match.tp_src = srcport
          msg.match = match
          msg.idle_timeout = 0
          msg.hard_timeout = 0
          msg.actions.append(of.ofp_action_output(port = out_port))
          core.openflow.sendToDPID(switch,msg)
     	
  def _install(self,switch,in_port,out_port):
          msg = of.ofp_flow_mod()
          match = of.ofp_match()
          match.in_port = in_port
          msg.match = match
          msg.idle_timeout = 0
          msg.hard_timeout = 0
          for i in range(len(out_port)):
              msg.actions.append(of.ofp_action_output(port = out_port[i]))
          core.openflow.sendToDPID(switch,msg)



def launch ():
  core.registerNew(Simples)
