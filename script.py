
import pyaudio
import webbrowser
import secrets
from tokens import get_access_token
import openwakeword
from openwakeword import Model
import numpy as np
import requests
import whisper
import time
from spotify import spotify_command




#first step is to get the access token
#if no access token, check for refresh token
#if no refresh token, open the callback server to ask for the code
    #to obtain the refresh and access token from spotify
    #save it to a json file
#with the access token, it can be passed in to make the calls to the spotify api

CHUNK = 1280
MODEL_PATH = "" #empty string are the default models
INFERENCE_FRAMEWORK = "onnx"
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
audio = pyaudio.PyAudio()
openwakeword.utils.download_models()

wake_word_active = False

#open connection ot mic
mic_stream = audio.open(format = FORMAT, channels = 1, rate = RATE, input = True, frames_per_buffer= CHUNK)


#record until silence, or when certain amount of time has passed, turn result into value passable into whisper
def record_command(mic_stream, chunk = CHUNK, rate = RATE, silence_threshold = 500, silence_duration = 1.5, max_duration = 2.5):
    print("speak")
    frames = [] #what will be passed into whisper
    silence_start = None
    start_time = time.time()

    while True:
        chunk_data = mic_stream.read(chunk, exception_on_overflow = False)
        frames.append(chunk_data)

        #audio_np = np.frombuffer(chunk_data, dtype=np.int16)


        if (start_time + max_duration < time.time()):
            break


    bytes = b"".join(frames)
    return np.frombuffer(bytes, dtype=np.int16).astype(np.float32) / 32768.0



if __name__ == "__main__":
    print("Loading models...............")
    oww_model = Model(wakeword_models=["hey_jarvis"], inference_framework=INFERENCE_FRAMEWORK)
    whisper_model = whisper.load_model("base")


    access_token = get_access_token()

    print("Listening for wakeword...")
    while True:

        audio_stream = np.frombuffer(mic_stream.read(CHUNK), dtype=np.int16)
        prediction = oww_model.predict(audio_stream)

        if prediction["hey_jarvis"] > 0.5:
            if not wake_word_active:
                wake_word_active = True
                print("Wake word detected")
                #get transcript, and then pass into spotify command to make api call
                audio = record_command(mic_stream) #numpy array of float32 audio samples
                transcript = whisper_model.transcribe(audio)
                #print(transcript)
                print(transcript["text"])
                spotify_command(transcript["text"], access_token)

                #reset for the next iteration
                oww_model.reset()
                mic_stream.read(mic_stream.get_read_available(), exception_on_overflow=False)
                time.sleep(0.5)
        else:
            wake_word_active = False

