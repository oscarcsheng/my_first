#! /usr/bin/env python
# -*- encoding: UTF-8 -*-
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule
import time
"""Example: Use ALSpeechRecognition Module"""

ROBOT_IP = "192.168.43.56"

# Creates a proxy on the speech-recognition module

asr = ALProxy("ALSpeechRecognition", ROBOT_IP, 9559)

while True:
   
    print("Start~")
    asr.subscribe("Test_ASR")
    print 'Speech recognition engine started'
    
    asr.setLanguage("English")
    
    time.sleep(10)
    asr.unsubscribe("Test_ASR")