import cv2
import imagehash
from PIL import Image
import os
import math
import time

class QueryFrameMatcher:
    def __init__(self, videos_dir):
        self.videos_dir = videos_dir

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
                break  # break loop if no more frames
            last_frame = frame
            total_frames += 1

        cap.release()

        return first_frame, last_frame, total_frames

    def find_matching_window_1(self, main_video_path, start_time, target_start_frame, target_end_frame, window_size, interval=30):
        print("started at " + str(start_time))
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
                matched_start = self.compare_frame_hashes(frames[0], target_start_frame)
                if matched_start:
                    matched_end = self.compare_frame_hashes(frames[-1], target_end_frame)
                    if matched_end:
                        exact_time = (start_frame_number + start_pointer) / fps
                        cap.release()
                        return exact_time, start_frame_number + start_pointer

        cap.release()
        return None


    def compare_frame_hashes(self, frame1, frame2):
        frame1_image = Image.fromarray(frame1)
        frame2_image = Image.fromarray(frame2)
        hash1 = imagehash.average_hash(frame1_image)
        hash2 = imagehash.average_hash(frame2_image)

        return hash1 - hash2 == 0
    
    def convert_to_min_sec_millisec(self, time_in_seconds):
        time_in_seconds = math.ceil(time_in_seconds)
        minute = int(time_in_seconds // 60)
        second = int(time_in_seconds % 60)
        return minute, second
    
    def find_query(self, query_path, matched_chunk):
        start_time_search = time.time()

        video_path = os.path.join(self.videos_dir, matched_chunk['video'].split('.')[0] + '.mp4')

        first_frame, last_frame, frame_count = self.extract_frames_and_count(query_path)

        if first_frame is not None:
            cv2.imwrite('query_first_frame.jpg', first_frame)
        if last_frame is not None:
            cv2.imwrite('query_last_frame.jpg', last_frame)
        start_time = matched_chunk['chunk']['start_time'] - 35 # Expand search interval from -35 to +35
        if start_time < 0:
            start_time = 0
        try:
            match_time, frame_num = self.find_matching_window_1(
                video_path, start_time, first_frame, last_frame, frame_count, 85)
        except:
            print(f"Frame searched from {start_time}, not found")

        if match_time is not None:
            minute, second = self.convert_to_min_sec_millisec(
                match_time)
            print(
                f"Result found for {query_path} in {matched_chunk['video']} at time: {minute}:{second} at {frame_num}")
        
        end_time_search = time.time()
        time_taken = end_time_search - start_time_search
        print("Time taken for frame matching:", time_taken)


