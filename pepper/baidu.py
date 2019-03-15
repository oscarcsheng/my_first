#！-*-coding:utf-8-*-
import requests
import json
import qi
from naoqi import ALProxy


key = 'ff5c48b026ef481ea8972ad7f3e6a247'
#key = '7addaf980bb346309c98584ee7005b36'
userID = '406387'
#userID = '406582'
IP = "192.168.43.56"
#tts = ALProxy("ALTextToSpeech", "127.0.0.1", 38091)
tts = ALProxy("ALTextToSpeech", IP, 9559)
app = qi.Application(url='tcp://'+IP+':9559')

while True:
    app.start()
    session = app.session
    print("Connect to robot")
    dialog = session.service("ALDialog")
    dialog.setLanguage("Chinese")
    topicContent = ("topic:~testingBlockingEvents()\n"
                    "language:enu\n"
                    "u:")
    info = raw_input("\n我：")  
    url = 'http://openapi.tuling123.com/openapi/api/v2'
    data = {
        "perception":{
            "inputText":{
                "text":info
            }
        },
        "userInfo": 
            {
            "apiKey": key,
            "userId": userID  
            }
    }
    res = requests.post(url,data=json.dumps(data))
    res.encoding = 'utf-8'
    #res1 = res.text.find(values)
   # print(res.text)
    jd = json.loads(res.text)##将得到的json格式的信息转换为Python的字典格式
   # print(jd(values))
  #  res1 = res.emotion
  #  print(type(res.text))
   # answer = jd['results'][0]['values']
   # print(answer)
    answer1 = jd['results'][0]['values']['text']
    print(answer1)
   # answer3 = answer2['text']

    answer2=answer1.encode("utf-8")
    #print(answer3)
    tts.say(answer2)