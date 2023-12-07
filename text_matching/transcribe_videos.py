import os
import json
import speech_recognition as sr
from pydub import AudioSegment
from tqdm import tqdm 
import re

def is_speech(audio_chunk, threshold=-50):
    return True

def divide_chunks(audio, chunk_length):
    for i in range(0, len(audio), chunk_length):
        yield audio[i:i + chunk_length]

def read_existing_transcriptions(file_path):
    try:
        with open(file_path, "r") as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        return []

audio_directory = "./Audios/"

recognizer = sr.Recognizer()

# Load existing data
transcription_file = "./transcriptions.json"
videos_data = read_existing_transcriptions(transcription_file)

chunk_size = 15


# Process each audio file in the directory
for filename in tqdm(os.listdir(audio_directory)):
    if filename.endswith(".wav"):
        path = os.path.join(audio_directory, filename)
        video_data = {"video_name": filename, "chunks": []}

        audio = AudioSegment.from_wav(path)
        chunks = divide_chunks(audio, chunk_size * 1000) 

        # Process each chunk
        for i, chunk in tqdm(enumerate(chunks)):
            # Export chunk to a temporary file
            chunk_file = f"temp_chunk_{i}.wav"
            chunk.export(chunk_file, format="wav")

            # Recognize speech in the chunk
            with sr.AudioFile(chunk_file) as source:
                recognizer.adjust_for_ambient_noise(source)
                audio_data = recognizer.record(source)
                try:
                    # text = recognizer.recognize_sphinx(audio_data)
                    # text = recognizer.recognize_google(audio_data)
                    result = recognizer.recognize_azure(audio_data, key='8c95b173ccc54c21ac6c1cb11a9a8a07', location='eastus')
                    chunk_data = {
                        "start_time": i * chunk_size,  # start time in seconds
                        "end_time": (i + 1) * chunk_size,
                        "transcription": re.sub(r'[^\w\s]', '', result[0]).lower() # remove punctuation, letter casing
                    }
                    print(result)
                    video_data["chunks"].append(chunk_data)
                except sr.UnknownValueError:
                    print(f"Could not understand chunk {i} in {filename}")
                except sr.RequestError as e:
                    print(f"API request error in chunk {i} of {filename}; {e}")

            os.remove(chunk_file)

        videos_data.append(video_data)

# Write the transcriptions to a JSON file
with open("./transcriptions.json", "w") as json_file:
    json.dump(videos_data, json_file, indent=4)

print("Transcription completed and saved to transcriptions.json")
