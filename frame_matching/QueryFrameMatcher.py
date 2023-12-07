import cv2
import imagehash
from PIL import Image
import os
import math
import time
import numpy as np


class QueryFrameMatcher:
    def __init__(self, videos_dir, rgbs_dir):
        self.videos_dir = videos_dir
        self.rgbs_dir = rgbs_dir

    def get_frame_data(self, rgb_file, frame_number, width=352, height=288):
        frame_size = width * height * 3  # 3 bytes per pixel
        offset = frame_number * frame_size

        with open(rgb_file, 'rb') as file:
            file.seek(offset)
            frame_data = file.read(frame_size)

        return frame_data

    def extract_rgb_values(self, frame_data, width=352, height=288):
        frame = np.frombuffer(frame_data, dtype=np.uint8).reshape(
            (height, width, 3))
        return frame  # This is an array of RGB values for the entire frame

    def extract_frames_and_count(self, video_path):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("Error opening video file")
            return None, None, 0

        # Read the first frame
        ret, first_frame = cap.read()
        if not ret:
            print("Error reading the first frame")
            cap.release()
            return None, None, 0

        last_frame = None
        total_frames = 1

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            last_frame = frame
            total_frames += 1

        cap.release()

        return first_frame, last_frame, total_frames

    def find_matching_window_1(self, main_video_path, start_time, target_start_frame, target_end_frame, window_size, interval=30):
        print("Started searching for frame at " + str(start_time))
        cap = cv2.VideoCapture(main_video_path)
        cap2 = cv2.VideoCapture(main_video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)

        start_frame_number = int(start_time * fps)
        end_frame_number = int((start_time + interval) * fps)

        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame_number)

        start_pointer = 0
        end_pointer = 0
        frames = []
        frame_counter = 0

        while True:
            ret, frame = cap.read()
            if not ret or cap.get(cv2.CAP_PROP_POS_FRAMES) > end_frame_number:
                break

            frame_counter += 1
            frames.append(frame)

            end_pointer += 1
            if end_pointer - start_pointer > window_size:
                frames.pop(0)
                start_pointer += 1

            if end_pointer - start_pointer == window_size:
                matched_start = self.compare_frame_hashes(
                    frames[0], target_start_frame)
                if matched_start:
                    matched_end = self.compare_frame_hashes(
                        frames[-1], target_end_frame)
                    if matched_end:
                        exact_time = (start_frame_number + start_pointer) / fps
                        cap.release()
                        return exact_time, start_frame_number + start_pointer

        cap.release()
        return None, None

    def compare_frame_hashes_rgb(self, frame_data1, frame_data2, width=352, height=288):
        frame1 = np.frombuffer(
            frame_data1, dtype=np.uint8).reshape((height, width, 3))
        frame2 = np.frombuffer(
            frame_data2, dtype=np.uint8).reshape((height, width, 3))

        frame1_image = Image.fromarray(frame1)
        frame2_image = Image.fromarray(frame2)

        hash1 = imagehash.average_hash(frame1_image, hash_size=16)
        hash2 = imagehash.average_hash(frame2_image, hash_size=16)

        return hash1 == hash2

    def compare_frame_hashes(self, frame_data1, frame_data2):
        frame1_image = Image.fromarray(frame_data1)
        frame2_image = Image.fromarray(frame_data2)

        hash1 = imagehash.average_hash(frame1_image, hash_size=16)
        hash2 = imagehash.average_hash(frame2_image, hash_size=16)

        return hash1 == hash2

    def get_rgb_frame_match(self, rgb_path, frame_num, query_path, query_frame_count, start_time):
        query_path_parts = query_path.split('/')
        query_path_parts = query_path_parts[:-2] + ['Queries/RGBs'] + [
            query_path_parts[-1].split('.')[0] + '.rgb']
        query_path = '/'.join(query_path_parts)

        start_query = self.get_frame_data(query_path, 0)
        end_query = self.get_frame_data(query_path, query_frame_count-1)
        start_frame_number = int(start_time * 30)
        end_frame_number = start_frame_number + query_frame_count
        max_end_frame_number = int((start_time + 85) * 30)

        while end_frame_number <= max_end_frame_number:
            start_video_frame = self.get_frame_data(
                rgb_path, start_frame_number)
            end_video_frame = self.get_frame_data(rgb_path, end_frame_number)
            # print((start_frame_number, end_frame_number))
            if self.compare_frame_hashes_rgb(start_video_frame, start_query):
                if self.compare_frame_hashes_rgb(end_video_frame, end_query):
                    return start_frame_number

            start_frame_number += 1
            end_frame_number += 1

        return None

    def convert_to_min_sec_millisec(self, time_in_seconds):
        time_in_seconds = math.ceil(time_in_seconds)
        minute = int(time_in_seconds // 60)
        second = int(time_in_seconds % 60)
        return minute, second

    def find_query(self, query_path, matched_chunk):
        start_time_search = time.time()

        video_path = os.path.join(
            self.videos_dir, matched_chunk['video'].split('.')[0] + '.mp4')

        first_frame, last_frame, frame_count = self.extract_frames_and_count(
            query_path)

        if first_frame is not None:
            cv2.imwrite('query_first_frame.jpg', first_frame)
        if last_frame is not None:
            cv2.imwrite('query_last_frame.jpg', last_frame)
        # Expand search interval from -35 to +35
        start_time = matched_chunk['chunk']['start_time'] - 35
        if start_time < 0:
            start_time = 0
        # try:
        #     match_time, frame_num = self.find_matching_window_1(
        #         video_path, start_time, first_frame, last_frame, frame_count, 85)
        # except Exception as e:
        #     print(e.args)

        exact_time_rgb = self.get_rgb_frame_match(os.path.join(self.rgbs_dir, matched_chunk['video'].split('.')[
                                                  0] + '.rgb'), 0, query_path, frame_count, start_time)
        # print("Mp4 output: ", frame_num, "RGB output: ", exact_time_rgb)

        # if match_time is not None:
        #     minute, second = self.convert_to_min_sec_millisec(
        #         match_time)
        #     print(
        #         f"Result found for {query_path} in {matched_chunk['video']} at time: {minute}:{second} at {frame_num}")
        # else:
        #     print("Result not found for {query_path}")

        end_time_search = time.time()
        time_taken = end_time_search - start_time_search
        print(f"Time taken for frame matching: {time_taken:.5f} seconds")
        return exact_time_rgb