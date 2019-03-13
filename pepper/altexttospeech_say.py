#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""Example: Use say Method"""

from naoqi import ALProxy

tts = ALProxy("ALTextToSpeech", "192.168.43.56", 9559)

tts.say("This is a sample text!")
print("complete")

