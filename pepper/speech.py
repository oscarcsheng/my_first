#!/usr/bin/env python
'''
Created on 23.03.2015
 modified class from nao choregraphe
@author: Andy Klay
'''
import copy
import sys
import time

from naoqi import ALProxy, ALModule, ALBroker

    def __init__(self, IP, PORT):
        ALModule.__init__(self, "SpeechTestClass")
        try:
            self.asr = ALProxy("ALSpeechRecognition")
            self.asr.setLanguage("English")
        except Exception as e:
            self.asr = None
            self.logger.error(e)
        self.memory = ALProxy("ALMemory")