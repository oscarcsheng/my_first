#include <iostream>
#include <alproxies/alaudiorecorderproxy.h>
#include <qi/os.hpp>

int main(int argc, char **argv)
{
  if (argc < 2) {
    std::cerr << "Usage: alaudiorecorder_startrecording pIp"
              << std::endl;
    return 1;
  }
  const std::string pIp = argv[1];

  AL::ALAudioRecorderProxy proxy(pIp);

  /// Configures the channels that need to be recorded.
  AL::ALValue channels;
  channels.arrayPush(0); //Left
  channels.arrayPush(0); //Right
  channels.arrayPush(1); //Front
  channels.arrayPush(0); //Rear

  /// Starts the recording of NAO's front microphone at 16000Hz
  /// in the specified wav file
  proxy.startMicrophonesRecording("/home/cs/Pepper/test.wav", "wav", 16000, channels);

  qi::os::sleep(5);

  /// Stops the recording and close the file after 10 seconds.
  proxy.stopMicrophonesRecording();

  return 0;
}