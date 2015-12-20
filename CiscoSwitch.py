
import os
import re

class NoPermission(BaseException):
	pass

class CiscoSwitch:
  """ A Cisco Switch class """	
  def __init__(self,ip):
    self.data = []
    self.ip = ip
    r = os.system("rsh " + self.ip + " show ver > /dev/null 2>/dev/null")
    #print r
    if r > 0:
    	raise NoPermission("Cannot rshell to switch")
    self.getConfig()
    self.refreshver()
    self.refreshCDP()
    self.refreshMAC()

  def refreshver(self):
      for l in os.popen("rsh " + self.ip + " show ver").readlines():
        sios = re.search(".*IOS .*Version (.*),",l)
        if sios:
  	 	    self.version = sios.group(1)
        smodel = re.search("^Model number.*: (.*)\r",l)
        if smodel:
          self.model = smodel.group(1)
        smodel = re.search("^cisco ([a-zA-Z0-9-]*) ",l)
        if smodel:
          self.model = smodel.group(1)

  def refreshCDP(self):
    self.neighbour = {}
    neip = "0.0.0.0"
    for l in os.popen("rsh " + self.ip + " show cdp nei det").readlines():
      sip = re.search("IP address: ([0-9]*\.[0-9]*\.[0-9]*\.[0-9]*)",l)
      if sip:
      	neip = sip.group(1)
      sint = re.search("Interface: (.*), ",l)
      if sint:
         interface = sint.group(1)
         self.neighbour[interface] = neip
         neip = "0.0.0.0"	

  def refreshMAC(self):
    self.MaxPort = ""
    self.MaxCount = 0
    self.portbymac = {}
    self.maccount = {}
    REMAC = "[0-9]* +([0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4}) +DYNAMIC +(.*)"
    if self.model == "WS-C6513":
      REMAC = "[0-9]* +([0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4}) +dynamic.* +(.*)"
    for l in os.popen("rsh " + self.ip + " show mac-add").readlines():
      #smac = re.search("[0-9]* +([0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4}) +DYNAMIC +(.*)",l)
      smac = re.search(REMAC,l)
      if smac:
        try:
          port = self.shortint[smac.group(2)[:-1]]
        except KeyError:
        	pass
        mac = smac.group(1)
        self.portbymac[mac] = port
        self.maccount.setdefault(port,0)
        self.maccount[port] += 1
        if self.maccount[port] > self.MaxCount:
    	  	 self.MaxCount = self.maccount[port]
    	  	 self.MaxPort = port

  def getConfig(self):
    self.shortint = {}
    for l in os.popen("rsh " + self.ip + " show running-config").readlines():
    	sint = re.search("interface ([a-zA-Z-]*)([0-9/]*)",l)
    	if sint:
         interface = sint.group(1) + sint.group(2)
         intshort = sint.group(1)[0:2] + sint.group(2)
         self.shortint[intshort] = interface