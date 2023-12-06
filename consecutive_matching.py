import os
import time

import cv2
import numpy as np
from PIL import Image
import imagehash
from scenedetect import detect, AdaptiveDetector, split_video_ffmpeg
from collections import defaultdict


def get_matching_run_length(first_frame_dict, last_frame_dict, start_key):
    run_length = 0
    start_value = 1
    start_key += 1
    while start_key in first_frame_dict and start_value + 1 in first_frame_dict[start_key]:
        run_length += 1
        if start_key in last_frame_dict and start_value + 1 in last_frame_dict[start_key]:
            start_value += 1
        else:
            break
        start_key += 1
    return run_length, start_key


def find_consecutive_scenes(first_frame_dict, last_frame_dict, query_scenes_length):
    result = {}
    for v_frame, q_frames in last_frame_dict.items():
        for q_frame in q_frames:
            if q_frame == 1:
                run_length, end_key = get_matching_run_length(first_frame_dict, last_frame_dict, v_frame)
                if run_length >= query_scenes_length:
                    result[v_frame] = end_key
    return result


def check_diff_imagehash(query_frame, video_frame):
    hash0 = imagehash.average_hash(Image.open(query_frame))
    hash1 = imagehash.average_hash(Image.open(video_frame))
    cutoff = 5  # maximum bits that could be different between the hashes.

    if hash0 - hash1 < cutoff:
        # print(video_frame, ':', query_frame)
        # print(hash0)
        # print(hash1)
        return True

    # else:
    # print('images are not similar')
    return False


def extract_frames(video_path, o_path_first, o_path_last):
    # Open the video file
    cap = cv2.VideoCapture(video_path)

    # Get the total number of frames in the video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Extract the first frame
    ret, first_frame = cap.read()
    cv2.imwrite(o_path_first, first_frame)

    # Extract the last frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames - 1)
    ret, last_frame = cap.read()
    cv2.imwrite(o_path_last, last_frame)

    # Release the video capture object
    cap.release()
    return os.path.dirname(o_path_first)


def convert_to_rgb(input_path, output_path):
    # Open the image file
    img = Image.open(input_path)

    # Convert to RGB mode
    rgb_img = img.convert('RGB')

    # Save as .rgb file using numpy
    rgb_data = np.array(rgb_img)
    with open(output_path, 'wb+') as f:
        f.write(rgb_data.tobytes())


def get_frames(video_path, frames_path, video_list):
    if not os.path.exists(frames_path):
        os.mkdir(frames_path)

    for file in video_list:
        # Output paths for first and last frames
        output_path_first = frames_path + file + "_first_frame.png"
        output_path_last = frames_path + file + "_last_frame.png"

        # Extract frames from the video
        extract_frames(video_path + file, output_path_first, output_path_last)

        # Convert frames to .rgb format
        convert_to_rgb(output_path_first, "first_frame.rgb")
        convert_to_rgb(output_path_last, "last_frame.rgb")
    frame_list = os.listdir(frames_path)
    frame_list.sort()
    return frame_list


def get_scenes(video_path, video_scene_path):
    scene_list = detect(video_path, AdaptiveDetector())
    if not os.path.exists(video_scene_path):
        os.mkdir(video_scene_path)
    scenes = os.listdir(video_scene_path)
    if len(scenes) == 0:
        split_video_ffmpeg(video_path, scene_list, video_scene_path + "/$VIDEO_NAME-Scene-$SCENE_NUMBER.mp4")
        scenes = os.listdir(video_scene_path)
    scenes.sort()
    return scenes, scene_list

#NEEDS THE FOLDER CONTAINING THE FIRST AND LAST FRAMES OF THE VIDEO NOT THE SCENES
# CODE GIVEN IN extract_vid_frames.py

def get_video_clip(query_path, video_frames_path):
    # Record the start time
    start_time = time.time()
    #video_frames_path = "Frames/Video_9_Frames/"
    #query_path = "Queries/video9_1.mp4"
    query_scene_path = query_path.split(".")[0] + "_Scenes/"
    query_scene_list, query_scene_timecodes = get_scenes(query_path, query_scene_path)
    query_frames_path = query_path.split(".")[0] + "_Frames/"
    matched_frames = defaultdict(list)
    result = {}
    if len(query_scene_list) > 1:
        query_frame_list = get_frames(query_scene_path, query_frames_path, query_scene_list)
        # Record the end time
        end_time = time.time()
        # Calculate the runtime
        runtime = end_time - start_time
        # Print the runtime
        print(f"Total Frame creation runtime: {runtime:.5f} seconds")
        # Record the start time
        start_time = time.time()
        vid_frame_list = os.listdir(video_frames_path)
        timecode_csv = [file for file in vid_frame_list if file.endswith("csv")][0]
        vid_frame_list = [file for file in vid_frame_list if not file.endswith("csv")]
        vid_frame_list.sort()
        for query_frame in query_frame_list:
            for vid_frame in vid_frame_list:
                if check_diff_imagehash(query_frames_path + query_frame, video_frames_path + vid_frame):
                    matched_frames[vid_frame].append(query_frame)

        # Record the end time
        end_time = time.time()
        # Calculate the runtime
        runtime = end_time - start_time
        # Print the runtime
        print(f"Total Matching Time: {runtime:.5f} seconds")
        # Record the start time
        start_time = time.time()
        first_frames = defaultdict(list)
        last_frames = defaultdict(list)
        for matched_v_frame, matched_q_frame_list in matched_frames.items():
            v_frame_number = int(matched_v_frame.split('-')[2].split('_')[0])
            for matched_q_frame in matched_q_frame_list:
                q_frame_number = int(matched_q_frame.split('-')[2].split('.')[0])
                if "last" in matched_v_frame and "last" in matched_q_frame:
                    last_frames[v_frame_number].append(q_frame_number)
                elif "first" in matched_v_frame and "first" in matched_q_frame:
                    first_frames[v_frame_number].append(q_frame_number)
        consecutive_matched_frames = find_consecutive_scenes(first_frames, last_frames, len(query_scene_list) - 1)
        # print(consecutive_matched_frames)

        with open(video_frames_path + timecode_csv, "r") as file:
            timecodes = file.readline().strip().split(',')
        

        # Example result = 
        # { video1: [(00:4:01:00, 00:4:30:00), ...]
        #   video2: [(00:4:45:00, 00:4:55:00), ...]
        # }

        # Note: Try to sort the intervals and avoid overlapping intervals
        if consecutive_matched_frames:
            video_num = video_frames_path.split('_')[1]
            result['video'+video_num] = []
        for start_scene, end_scene in consecutive_matched_frames.items():
            result['video'+video_num].append((timecodes[start_scene-1], timecodes[end_scene]))
            #print(timecodes[start_scene-1], timecodes[end_scene])

        # Record the end time
        end_time = time.time()

        # Calculate the runtime
        runtime = end_time - start_time

        # Print the runtime
        print(f"Total Array processing runtime: {runtime:.5f} seconds")
        #print(result)
        return result

#get_video_clip('./Queries/video11_1.mp4', './Frames/Video_11_Frames/')
#get_video_clip('./Queries/video1_1.mp4', './Frames/Video_1_Frames/')
#get_video_clip('./Queries/video6_1.mp4', './Frames/Video_6_Frames/')
