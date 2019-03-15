import qi

ROBOT_URL = "10.80.129.67"

print "Connecting to robot..."

app = qi.Application(url='tcp://'+ROBOT_URL+':9559')
app.start()
session = app.session

print "Connected to robot."

dialog = session.service("ALDialog")
dialog.setLanguage("English")

topicContent = ("topic: ~testingBlockingEvents()\n"
                "language: enu\n"
                "u:(start counting) 0, 1, 2, 3, 4, 5.\n"
                "u:(e:FrontTactilTouched) You touched my head!\n")

topicName = dialog.loadTopicContent(topicContent)
dialog.activateTopic(topicName)
dialog.subscribe("test_of_dialog")

print "Robot is listening."
print "Hit CTRL+C to stop."

app.run()

print "Exiting..."

dialog.unsubscribe("test_of_dialog")
dialog.deactivateTopic(topicName)
dialog.unloadTopic(topicName)
