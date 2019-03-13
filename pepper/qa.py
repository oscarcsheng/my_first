from naoqi import ALProxy
import sys
import time
import qi
import argparse

#IP = "<192.168.43.56>"

asr = ALProxy("ALTextToSpeech", "192.168.43.56", 9559)


while True:
  #  asr.setLanguage("English")

    #vocabulary = ["yes", "no", "please"]
   # asr.setVocabulary(vocabulary, False)
  #  asr.subscribe('Test_ASR')
  #  print 'Speech recognition engine started'
  #  time.sleep(20)

    #asr.unsubscribe("Test_ASR")
    #asr_service = session.service("ALSpeechRecognition")

    asr.setLanguage("English")

    # Example: Adds "yes", "no" and "please" to the vocabulary (without wordspotting)
   # vocabulary = ["yes", "no", "please"]
    #asr.setVocabulary(vocabulary, False)

    # Start the speech recognition engine with user Test_ASR
    asr.subscribe()
    #asr.subscribe("Test_ASR")
    print 'Speech recognition engine started'
    time.sleep(20)
    asr.unsubscribe()
   # asr.unsubscribe("Test_ASR")