import time
import random
import os
from brewapp import app
from brewapp.base.actor import ActorBase
from brewapp.base.model import *
from flowmeterdata import *

import threading
try:
	import RPi.GPIO as GPIO
	app.logger.info("SETUP GPIO Module Loaded")
except Exception as e:
	app.logger.error("SETUP GPIO Module " + str(e))
	pass


class Flowmeter(ActorBase):
	global fms
	fms = dict()
	def init(self):
		app.logger.info("INIT flowmeter")
		try:
			GPIO.setmode(GPIO.BCM) # use real GPIO numbering			
			app.logger.info(app.brewapp_flowmeter_cfg)
			for f in app.brewapp_flowmeter_cfg:
				hw = app.brewapp_flowmeter_cfg[f];

				gpioNumber = self.translateDeviceName(hw["config"]["switch"])
				GPIO.setup(gpioNumber,GPIO.IN, pull_up_down = GPIO.PUD_UP)
				GPIO.add_event_detect(gpioNumber, GPIO.RISING, callback=self.doAClick, bouncetime=20) # Beer, on Pin 23
				app.logger.info("flowmeter" + str(gpioNumber))
				app.logger.info("INIT flowmeter" + str(f))
				fms[f] = FlowMeterData()
		except Exception as e:
			app.logger.error("SETUP GPIO for flowmeter FAILED " + str(e))
			self.state = False

	def doAClick(self, channel):
		for f in app.brewapp_flowmeter_cfg:
			hw = app.brewapp_flowmeter_cfg[f];
			gpioNumber = self.translateDeviceName(hw["config"]["switch"])
			if (gpioNumber == channel):
				currentTime = int(time.time() * FlowMeterData.MS_IN_A_SECOND)
				fms[f].update(currentTime)

	def getUpdate(self, flowId):
		for f in app.brewapp_flowmeter_cfg:
			flow = fms[f].thisPour
			flow = "{0:.2f}".format(flow)
			return flow


	def translateDeviceName(self, name):
		if(name == None or name == ""):
			return None
		return int(name[4:])
	
	
	def getSensors(self):
		gpio = []
		for i in range(2, 28):
			gpio.append("GPIO"+str(i))
		return gpio

	def clearFlowmeterData(self,flowId):
		fms[int(flowId)].clear
		return "ok"

	


