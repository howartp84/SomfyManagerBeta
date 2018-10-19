#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################
# Copyright (c) 2016, Perceptive Automation, LLC. All rights reserved.
# http://www.indigodomo.com

import indigo

import telnetlib, socket


# Note the "indigo" module is automatically imported and made available inside
# our global name space by the host process.


################################################################################
class Plugin(indigo.PluginBase):
	########################################
	def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
		super(Plugin, self).__init__(pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
		self.debug = pluginPrefs.get("showDebugInfo", False)

		self.myLink = None
		self.myLinkAuth = ""

	########################################

	def closedPrefsConfigUi(self, valuesDict, userCancelled):
		# Since the dialog closed we want to set the debug flag - if you don't directly use
		# a plugin's properties (and for debugLog we don't) you'll want to translate it to
		# the appropriate stuff here.
		if not userCancelled:
			self.debug = valuesDict.get("showDebugInfo", False)
			if self.debug:
				indigo.server.log("Debug logging enabled")
			else:
				indigo.server.log("Debug logging disabled")

	def closedDeviceConfigUi(self, valuesDict, userCancelled, typeId, devId):
		#self.debugLog(str(valuesDict))
		#self.debugLog(str(typeId))
		#self.debugLog(str(devId))
		if not userCancelled:
			if (str(typeId) == "mylink"):
				#self.debugLog("myLink")
				dev = indigo.devices[devId]
				devIP = valuesDict["devIP"]
				dev.stateListOrDisplayStateIdChanged()
				dev.updateStateOnServer("devIP",devIP)
			if (str(typeId) == "motor"):
				#self.debugLog("Motor")
				dev = indigo.devices[devId]
				targetAddr = valuesDict["devAddr"]
				targetCh = valuesDict["devCh"]
				if (str(targetCh) == ""):
					targetCh = "*"
				targetID = str(targetAddr) + "." + str(targetCh)
				dev.stateListOrDisplayStateIdChanged()
				dev.updateStateOnServer("devAddrCh",targetID)
		return True

	def deviceStartComm(self, dev):
		#dev.stateListOrDisplayStateIdChanged()
		if (dev.deviceTypeId == "mylink"):
			devIP = dev.ownerProps['devIP']
			devPort = dev.ownerProps['devPort']
			devAuth = dev.ownerProps['devAuth']
			connTimeout = dev.ownerProps['connTimeout']
			
			indigo.server.log("Connecting to MyLink:  %s" % str(devIP))
			self.myLink = telnetlib.Telnet(devIP, int(devPort), timeout = int(connTimeout))
			self.myLinkAuth = str(devAuth)
			self.debugLog(str(self.myLink))

	def deviceStopComm(self, dev):
		if (dev.deviceTypeId == "doorLock"):
			self.myLink.close()
			self.myLink = None
			self.myLinkAuth = ""

	def myLinkCmdSingle(self, pluginAction):
		self.debugLog("myLinkCmdSingle action called:")
		#self.debugLog(str(pluginAction))
		targetDev = pluginAction.deviceId
		targetAddr = indigo.devices[int(targetDev)].ownerProps["devAddr"]
		targetCh = indigo.devices[int(targetDev)].ownerProps["devCh"]
		if (targetCh == ""):
			targetCh = "*"
		targetID = str(targetAddr) + "." + str(targetCh)
		
		method = str(pluginAction.pluginTypeId)
		method = method.replace(".1","").replace(".2","")
	
		self.debugLog("Target device: " + str(targetID))

		payload = '{ "id":1, "method": "%s", "params": { "auth": "%s", "targetID" : "%s"} }' % (method,self.myLinkAuth,targetID)
		
		indigo.server.log("Sending payload:  %s" % str(payload))

		self.myLink.write(payload)
		
		
		reply = ""
		
		reply = self.myLink.read_very_eager()
		self.debugLog("Reply: " + str(reply))

		
	def myLinkRead(self, pluginAction):
		self.debugLog("myLinkRead action called:")
		reply = ""
		
		reply = self.myLink.read_very_eager()
		self.debugLog("Reply: " + str(reply))