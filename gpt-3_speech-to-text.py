# /Applications/ffmpeg -i output.mp3 -ab 160k -ac 1 -ar 16000 -vn outputtest.flac
# ['ffmpeg', '-i', 'output.mp3', '-ab', '160k', '-ac', '1', '-ar', '16000', '-vn', 'outputtest.flac'], stdout=subprocess.PIPE)
import openai
import os
import pyaudio
import wave
import time
from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import pykakasi
from janome.tokenizer import Tokenizer

DEVICE_INDEX = 0
FORMAT = pyaudio.paInt16  # 16bit
CHANNELS = 1             # monaural
RATE = 48000             # sampling frequency [Hz]

time = 5  # record time [s]
output_path = "./sample.wav"

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True)

print("recording ...")

frames = []

for i in range(0, int(RATE / 1024 * time)):
    data = stream.read(1024)
    frames.append(data)

print("done.")

stream.stop_stream()
stream.close()
p.terminate()

wf = wave.open(output_path, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

authenticator = IAMAuthenticator(
    '<watson apikey>')
speech_to_text = SpeechToTextV1(
    authenticator=authenticator
)

speech_to_text.set_service_url(
    '<watsonapi url>')


class MyRecognizeCallback(RecognizeCallback):
    def __init__(self):
        RecognizeCallback.__init__(self)

    def on_data(self, data):
        print(data['results'][0]['alternatives'][0]['transcript'])
        with open('result_logs.txt', mode='a') as f:
            f.write(data['results'][0]['alternatives'][0]['transcript'] + '\n')

    def on_error(self, error):
        print('Error received: {}'.format(error))

    def on_inactivity_timeout(self, error):
        print('Inactivity timeout: {}'.format(error))


myRecognizeCallback = MyRecognizeCallback()

with open('sample.wav',
          'rb') as audio_file:
    audio_source = AudioSource(audio_file)
    response = speech_to_text.recognize_using_websocket(
        audio=audio_source,
        content_type='audio/wav',
        recognize_callback=myRecognizeCallback,
        model='ja-JP_BroadbandModel',
        keywords=['colorado'],
        keywords_threshold=0.5)

with open('result_logs.txt') as f:
    result_logs = f.readlines()
    last_result_log = result_logs[-1].replace('\n', '')
    print(last_result_log)


openai.api_key = '<openai apikey>'

start_sequence = '\nAI: '
restart_sequence = '\nHuman: '

response = openai.Completion.create(
    engine='davinci',
    prompt='Human: ' + last_result_log + '\nAI: ',
    temperature=0.9,
    max_tokens=50,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0.6,
    stop=['\n', ' Human:', ' AI:']
)

reply = response['choices'][0]['text']
print(reply)
t = Tokenizer()
kks = pykakasi.kakasi()
kana_text = ''

print(list(t.tokenize(reply, wakati=True)))

# for token in t.tokenize(reply):
#     kana_text += kks.convert(token)[0]['hira']
