import cv2
import imagehash
from PIL import Image
import os
import math
import time
import numpy as np
import random


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

    def compare_frame_array_rgb(self, frame_data1, frame_data2, width=352, height=288):
        frame1 = np.frombuffer(
            frame_data1, dtype=np.uint8).reshape((height, width, 3))
        frame2 = np.frombuffer(
            frame_data2, dtype=np.uint8).reshape((height, width, 3))

        return np.array_equal(frame1, frame2)


    def compare_frame_hashes_rgb(self, frame_data1, frame_data2, hashsize=16, threshold=0, width=352, height=288):
        frame1 = np.frombuffer(
            frame_data1, dtype=np.uint8).reshape((height, width, 3))
        frame2 = np.frombuffer(
            frame_data2, dtype=np.uint8).reshape((height, width, 3))

        frame1_image = Image.fromarray(frame1)
        frame2_image = Image.fromarray(frame2)

        hash1 = imagehash.average_hash(frame1_image, hash_size=hashsize)
        hash2 = imagehash.average_hash(frame2_image, hash_size=hashsize)

        return hash1 - hash2 <= threshold

    
    def print_array_differences(self, frame_data1, frame_data2, filename1, filename2, width=352, height=288):
    
        frame1 = np.frombuffer(frame_data1, dtype=np.uint8).reshape((height, width, 3))
        frame2 = np.frombuffer(
            frame_data2, dtype=np.uint8).reshape((height, width, 3))
        
        frame1_image = Image.fromarray(frame1)
        frame2_image = Image.fromarray(frame2)

        hash1 = imagehash.average_hash(frame1_image, hash_size=16)
        hash2 = imagehash.average_hash(frame2_image, hash_size=16)

        print("hash diff", hash1-hash2)

        differences = np.where(frame1 != frame2)
        num_differences = differences[0].size

        if num_differences == 0:
            print("Arrays are identical.")
        else:
            print(f"Arrays differ in {num_differences} elements.")
            # for index in zip(*differences):
            #     print(f"Difference at index {index}: {frame1[index]} != {frame2[index]}")
        image = Image.fromarray(frame2.astype('uint8'), 'RGB')
        image.save(filename1)
        image = Image.fromarray(frame1.astype('uint8'), 'RGB')
        image.save(filename2)
        return frame2


    def get_rgb_frame_match(self, video_rgb_path, query_rgb_path, query_frame_count, search_start_time, search_interval=85):
        print(video_rgb_path, query_rgb_path)
        query_start_frame = self.get_frame_data(query_rgb_path, 0)
        query_end_frame = self.get_frame_data(query_rgb_path, query_frame_count-1)
        start_frame_number = int(search_start_time * 30)
        end_frame_number = start_frame_number + query_frame_count-1
        max_end_frame_number = int((search_start_time + search_interval) * 30)
    
        while end_frame_number <= max_end_frame_number:
            start_video_frame = self.get_frame_data(
                video_rgb_path, start_frame_number)
            end_video_frame = self.get_frame_data(video_rgb_path, end_frame_number)
            # print((start_frame_number, end_frame_number))
            if self.compare_frame_array_rgb(start_video_frame, query_start_frame):
                print((start_frame_number, end_frame_number))
                if self.compare_frame_array_rgb(end_video_frame, query_end_frame):
                    print("Found with array : ", start_frame_number, end_frame_number)
                    return start_frame_number

            start_frame_number += 1
            end_frame_number += 1
        
        start_frame_number = int(search_start_time * 30)
        end_frame_number = start_frame_number + query_frame_count-1
        max_end_frame_number = int((search_start_time + search_interval) * 30)

        while end_frame_number <= max_end_frame_number:
            start_video_frame = self.get_frame_data(
                video_rgb_path, start_frame_number)
            end_video_frame = self.get_frame_data(video_rgb_path, end_frame_number)
            # print((start_frame_number, end_frame_number))
            if self.compare_frame_hashes_rgb(start_video_frame, query_start_frame, 16, 1):
                # print((start_frame_number, end_frame_number))
                if self.compare_frame_hashes_rgb(end_video_frame, query_end_frame, 16, 1):
                    print("Found with hash size 16 threshold 1: ", start_frame_number, end_frame_number)
                    return start_frame_number

            start_frame_number += 1
            end_frame_number += 1
        
        start_frame_number = int(search_start_time * 30)
        end_frame_number = start_frame_number + query_frame_count-1
        max_end_frame_number = int((search_start_time + search_interval) * 30)

        while end_frame_number <= max_end_frame_number:
            start_video_frame = self.get_frame_data(
                video_rgb_path, start_frame_number)
            end_video_frame = self.get_frame_data(video_rgb_path, end_frame_number)
            # print((start_frame_number, end_frame_number))
            if self.compare_frame_hashes_rgb(start_video_frame, query_start_frame, 8):
                # print((start_frame_number, end_frame_number))
                if self.compare_frame_hashes_rgb(end_video_frame, query_end_frame, 8):
                    print("Found with hash size 8 threshold 0: ", start_frame_number, end_frame_number)
                    return start_frame_number

            start_frame_number += 1
            end_frame_number += 1

        return None

    def convert_to_min_sec_millisec(self, time_in_seconds):
        time_in_seconds = math.ceil(time_in_seconds)
        minute = int(time_in_seconds // 60)
        second = int(time_in_seconds % 60)
        return minute, second
    
    def match_rgb_frames(self, query_rgb_path, video_rgb_path, start_frames, end_frames, frames_count):
        query_start_frame = self.get_frame_data(query_rgb_path, 0)
        query_end_frame = self.get_frame_data(query_rgb_path, frames_count-1)

        for start_frame in start_frames:
            start_frame_num = int(start_frame)
            video_start_frame = self.get_frame_data(video_rgb_path, start_frame_num)
            if self.compare_frame_array_rgb(video_start_frame, query_start_frame):
                video_end_frame = self.get_frame_data(video_rgb_path, start_frame_num + frames_count - 1)
                if self.compare_frame_array_rgb(video_end_frame, query_end_frame):
                    return start_frame_num
        
        for end_frame in end_frames:
            end_frame_num = int(end_frame)
            video_end_frame = self.get_frame_data(video_rgb_path, end_frame_num)
            if self.compare_frame_array_rgb(video_end_frame, query_end_frame):
                video_start_frame = self.get_frame_data(video_rgb_path, end_frame_num - frames_count + 1)
                if self.compare_frame_array_rgb(video_start_frame, query_start_frame):
                    return end_frame_num - frames_count + 1
        return None


    def find_query(self, query_mp4_path, query_rgb_path, hash_matched_chunk = None, matched_chunk = None):
        start_time_search = time.time()

        if hash_matched_chunk:
            video_rgb_path = os.path.join(self.rgbs_dir, hash_matched_chunk['video_name'] + '.rgb')
            frame_match = self.match_rgb_frames(query_rgb_path, video_rgb_path, hash_matched_chunk['start_frames'], hash_matched_chunk['end_frames'], int(hash_matched_chunk['frames_count']))
            return frame_match

        # video_path = os.path.join(
        #     self.videos_dir, matched_chunk['video'].split('.')[0] + '.mp4')

        first_frame, last_frame, frame_count = self.extract_frames_and_count(
            query_mp4_path)

        if first_frame is not None:
            cv2.imwrite('query_first_frame.jpg', first_frame)
        if last_frame is not None:
            cv2.imwrite('query_last_frame.jpg', last_frame)
        # Expand search interval from -35 to +35
        start_time = matched_chunk['chunk']['start_time'] - 35
        print("Starting frame search at time " + str(start_time))
        if start_time < 0:
            start_time = 0

        print(frame_count)
        exact_time_rgb = self.get_rgb_frame_match(os.path.join(self.rgbs_dir, matched_chunk['video'].split('.')[
                                                  0] + '.rgb'), query_rgb_path, frame_count, start_time)

        end_time_search = time.time()
        time_taken = end_time_search - start_time_search
        print(f"Time taken for frame matching: {time_taken:.5f} seconds")
        return exact_time_rgb
    
    # def find_matching_window_1(self, main_video_path, start_time, target_start_frame, target_end_frame, window_size, interval=30):
    #     print("Started searching for frame at " + str(start_time))
    #     cap = cv2.VideoCapture(main_video_path)
    #     cap2 = cv2.VideoCapture(main_video_path)
    #     fps = cap.get(cv2.CAP_PROP_FPS)

    #     start_frame_number = int(start_time * fps)
    #     end_frame_number = int((start_time + interval) * fps)

    #     cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame_number)

    #     start_pointer = 0
    #     end_pointer = 0
    #     frames = []
    #     frame_counter = 0

    #     while True:
    #         ret, frame = cap.read()
    #         if not ret or cap.get(cv2.CAP_PROP_POS_FRAMES) > end_frame_number:
    #             break

    #         frame_counter += 1
    #         frames.append(frame)

    #         end_pointer += 1
    #         if end_pointer - start_pointer > window_size:
    #             frames.pop(0)
    #             start_pointer += 1

    #         if end_pointer - start_pointer == window_size:
    #             matched_start = self.compare_frame_hashes(
    #                 frames[0], target_start_frame)
    #             if matched_start:
    #                 matched_end = self.compare_frame_hashes(
    #                     frames[-1], target_end_frame)
    #                 if matched_end:
    #                     exact_time = (start_frame_number + start_pointer) / fps
    #                     cap.release()
    #                     return exact_time, start_frame_number + start_pointer

    #     cap.release()
    #     return None, None

    
    # def compare_frame_hashes(self, frame_data1, frame_data2):
    #     frame1_image = Image.fromarray(frame_data1)
    #     frame2_image = Image.fromarray(frame_data2)

    #     hash1 = imagehash.average_hash(frame1_image, hash_size=16)
    #     hash2 = imagehash.average_hash(frame2_image, hash_size=16)

    #     return hash1 == hash2
