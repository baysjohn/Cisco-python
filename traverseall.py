#!/usr/local/bin/python

import time
import sys
from threading import Thread
import syslog
import socket

from CiscoSwitch import *

""" Traverse a network of Cisco switches. Assume a tree (no loops) """

def traverse(sip,fip,l):
  global visited
  global count
  global nt

  while nt > 7:
  	time.sleep(1)
  nt = nt + 1  
  print "Entering ",sip,l
  if sip in visited:
    syslog.syslog('Loop ' + sip + '. Skipping')
    print "Loop detected ",sip," already visited. Skipping"
    return
  visited.add(sip)
  try:
    s = CiscoSwitch(sip)
  except NoPermission:
    syslog.syslog('Cannot rsh ' + sip + ' ' + socket.getfqdn(sip))
    print "Cannot rsh to ",sip,socket.getfqdn(sip)
    return 1
  count = count + 1
  syslog.syslog('Switch ' + sip + ' ' + socket.getfqdn(sip) + ' model ' + s.model + ' count=' + str(count))
  #print sip,socket.getfqdn(sip)," model is ",s.model,count," so far"
  for i in s.neighbour:
    if s.neighbour[i] == fip:
      continue
    if s.neighbour[i] == "0.0.0.0":
      syslog.syslog('neighbour of ' + sip + ' interface ' + i + ' has no IP address')
      print "Neighbour of ",sip," interface ",i," has no IP address"
      continue
    tauip = re.search("132.66.",s.neighbour[i])
    if not tauip:
      syslog.syslog('neighbour of ' + sip + ' interface ' + i + ' has bad IP address ' + s.neighbour[i])
      print "Neighbour of ",sip," interface ",i," has bad IP address",s.neighbour[i]
      continue
    t = Thread(target=traverse, args=(s.neighbour[i],sip,l+1,))
    t.start()
    #traverse(s.neighbour[i],sip,l+1)
    nt = nt - 1

global visited
global count
global nt
visited = set()


#syslog.openlog(logoption=syslog.LOG_PID,facility=syslog.LOG_LOCAL7)
syslog.openlog("traverse",syslog.LOG_PID,syslog.LOG_LOCAL7)
syslog.syslog('Started')
seed = "132.66.8.11"
nt = 0
count = 0

traverse(seed,"",0)

syslog.syslog('Ended')
