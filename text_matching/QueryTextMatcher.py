import json
import math
import speech_recognition as sr
import pylcs
import time
import os
import json
from pydub import AudioSegment
import re


class QueryTextMatcher:
    def __init__(self):
        self.videos_data = self.read_existing_transcriptions(
            os.path.join(os.getcwd(), 'text_matching/transcriptions.json'))
        self.queries_data = self.read_existing_transcriptions_q(
            os.path.join(os.getcwd(), 'text_matching/transcriptions_queries.json'))
        self.recognizer = sr.Recognizer()

    def read_existing_transcriptions(self, file_path):
        try:
            with open(file_path, "r") as json_file:
                data = json.load(json_file)
                return {item['video_name'].split('.')[0]: [{'start_time': chunk['start_time'], 'end_time': chunk['end_time'], 'transcription': chunk['transcription']} for chunk in item['chunks']] for item in data}
        except FileNotFoundError:
            return {}

    def read_existing_transcriptions_q(self, file_path):
        try:
            with open(file_path, "r") as json_file:
                data = json.load(json_file)
                return {item['video_name'].split('.')[0]: item['text'] for item in data}
        except FileNotFoundError:
            return {}

    def find_text(self, input_text, matched_scenes={}):
        max_len = 0
        max_chunk = {}

        # TODO: Filter out matched scenes

        if matched_scenes:
            search_space = {}
            for video, intervals in matched_scenes.items():
                search_space[video] = []
                for interval in intervals:
                    start_interval = self.convert_to_seconds(interval[0])
                    end_interval = self.convert_to_seconds(interval[1])
                    for i in range(max(0, math.floor(start_interval/15)-1), math.ceil(end_interval/15)):
                        search_space[video].append(self.videos_data[video][i])
        else:
            search_space = self.videos_data

        for video_name, video_chunks in search_space.items():
            for chunk in video_chunks:
                chunk_text_preprocessed = chunk['transcription']
                similarity_len = self.longest_common_substring_pylcs(
                    chunk_text_preprocessed, input_text)

                if similarity_len >= 60 and similarity_len > max_len:
                    # print(similarity_len, chunk['start_time'])
                    max_len = similarity_len
                    max_chunk = {"video": video_name, "chunk": chunk}
        return max_chunk

    def convert_to_seconds(self, time_str):
        parts = time_str.split(':')
        
        hours, minutes, seconds = map(float, parts)
        total_seconds = (hours * 3600) + minutes * 60 + seconds
        return total_seconds

    def longest_common_substring_pylcs(self, s1, s2):
        res = pylcs.lcs_string_idx(s1, s2)
        return len(''.join([s2[i] for i in res if i != -1]))

    def convert_to_min_sec_millisec(self, time_in_seconds):
        time_in_seconds = math.ceil(time_in_seconds)
        minute = int(time_in_seconds // 60)
        second = int(time_in_seconds % 60)
        return minute, second

    # NOTE: use_pretranscribed_query should be set ot False for any queries other than the ones given by TAs
    def transcribe_query(self, query_path, use_pretranscribed_query=True):
        if use_pretranscribed_query:
            return self.queries_data[query_path.split('/')[-1].split('.')[0]]

        audio = AudioSegment.from_wav(query_path)
        temp_file = "temp_query.wav"
        audio.export(temp_file, format="wav")

        with sr.AudioFile(temp_file) as source:
            self.recognizer.adjust_for_ambient_noise(source)
            audio_data = self.recognizer.record(source)
            try:
                result = self.recognizer.recognize_azure(
                    audio_data, key='390b85c277ec4e638193ca1498b48414', location='eastus')
                print('query transcription:', result)
                return re.sub(r'[^\w\s]', '', result[0]).lower()

            except sr.UnknownValueError:
                print(f"Could not understand {query_path}")
            except sr.RequestError as e:
                print(f"API request error in {query_path}; {e}")
        return ""

    def find_query(self, query_path, matched_scenes={}, use_pretranscribed_query=True):
        # print(matched_scenes)
        start_time_transcript = time.time()
        query_text = self.transcribe_query(
            query_path, use_pretranscribed_query)
        end_time_transcript = time.time()
        print(f"Time taken for trascription: {(end_time_transcript - start_time_transcript):.5f} seconds")
        if query_text:
            start_time_itr = time.time()
            res = self.find_text(query_text, matched_scenes)
            end_time_itr = time.time()
            time_func_itr = end_time_itr - start_time_itr
            print(f"Time taken for text matching: {time_func_itr:.5f} seconds")
            if res:
                return res
            else:
                return None


# matcher = QueryTextMatcher('./../Videos')
# matcher.find_query('./../Queries/video11_2.mp4')
# matcher.find_query('./../Queries/video1_1.mp4')
# matcher.find_query('./../Queries/video2_1.mp4')
# matcher.find_query('./../Queries/video5_1.mp4')
# matcher.find_query('./../Queries/video6_1.mp4')
# matcher.find_query('./../Queries/video6_2.mp4')
# matcher.find_query('./../Queries/video7_1.mp4')
# matcher.find_query('./../Queries/video8_1.mp4')
# matcher.find_query('./../Queries/video9_1.mp4')
# matcher.find_query('./../Queries/video10_1.mp4')
# matcher.find_query('./../Queries/video11_1.mp4')
