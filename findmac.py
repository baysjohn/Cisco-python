#!/usr/local/bin/python

import sys
from CiscoSwitch import CiscoSwitch

m = sys.argv[1]

print "tracking ",m
seed = "132.66.8.11"
s = CiscoSwitch(seed)
try:
  p = s.portbymac[m]
except KeyError:
  sys.exit('not found')
print s.maccount[s.portbymac[m]]
while s.maccount[s.portbymac[m]] > 1:
  print m," is on ",s.portbymac[m]
  try:
    new = s.neighbour[s.portbymac[m]]
  except KeyError:
    break
  print "Checking with neighbour ",s.neighbour[s.portbymac[m]]
  olds = s
  s = CiscoSwitch(new)
print "switch is ",s.ip
print "port is ",s.portbymac[m]

