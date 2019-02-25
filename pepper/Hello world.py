from naoqi import ALProxy
tts = ALProxy("ALTextToSpeech", "127.0.0.1", 38221)
tts.say("Hello, world!")
