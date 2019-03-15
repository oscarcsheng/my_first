#! /usr/bin/env python
# -*- encoding: UTF-8 -*-
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule
import time
"""Example: Use ALSpeechRecognition Module"""


    def __init__(self, IP, PORT):
        ALModule.__init__(self, "SpeechTestClass")
        try:
            self.asr = ALProxy("ALSpeechRecognition")
            self.asr.setLanguage("English")
        except Exception as e:
            self.asr = None
            self.logger.error(e)
        self.memory = ALProxy("ALMemory")



if __name__ == '__main__':
    
    # Replace here with your NaoQi's IP address.
    #IP = "nao.local"  
    IP = "192.168.43.56"
    PORT = 9559
    
    # Read IP address from first argument if any.
    if len(sys.argv) > 1:
        IP = sys.argv[1]
      We need this broker to be able to construct
    # NAOqi modules and subscribe to other modules
    # The broker must stay alive until the program exists
    myBroker = ALBroker("myBroker",
       "0.0.0.0",   # listen to anyone
       0,           # find a free port and use it
       IP,          # parent broker IP
       PORT)        # parent broker port
    SpeechTestClass = SpeechTestClass(IP, PORT)
    

    #global SpeechTestClass
        
    tts = ALProxy("ALTextToSpeech")
    tts.say("test")   



# Creates a proxy on the speech-recognition module

asr = ALProxy("ALSpeechRecognition", ROBOT_IP, PORT)

tts = ALProxy("ALTextToSpeech",  ROBOT_IP, PORT)

myBroker = ALBroker("myBroker",
       "0.0.0.0",   # listen to anyone
       0,           # find a free port and use it
       ROBOT_IP,          # parent broker IP
       PORT)


while True:
   
    print("Start~")
    asr.startMicrophonesRecording("/home/cs/Pepper/test.wav", "wav", 16000, channels);
 
    
    time.sleep(10)
    asr.stopMicrophonesRecording()