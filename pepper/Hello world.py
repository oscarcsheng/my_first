from naoqi import ALProxy
tts = ALProxy("ALTextToSpeech", "127.0.0.1", 38071)
tts.say("Hello, world!")
