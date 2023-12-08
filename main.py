import os
import sys
import time
import json
from PyQt5.QtWidgets import QApplication

# from consecutive_matching import get_video_clip, query_preprocesing
from text_matching.QueryTextMatcher import QueryTextMatcher
from frame_matching.QueryFrameMatcher import QueryFrameMatcher
# import frame_matching.backupQueryFrameMatcher as backupFrameMatcher
from media_player_1 import VideoPlayer
from shot_boundary.QueryShotBoundary import QueryShotBoundary

def convert_to_seconds(time_str):
    hours, minutes, seconds = map(float, time_str.split(':'))
    return int((hours * 3600) + (minutes * 60) + seconds)

def read_scene_greater_than_20():
    try:
        with open('./scenes_g_20.json', "r") as json_file:
            data = json.load(json_file)
            return {item['video_name']: [(chunk['start_time'], chunk['end_time']) for chunk in item['durations']] for item in data}
    except FileNotFoundError:
        return {}

def process_video(mp4_file, wav_file, rgb_file):
    start_processing_time = time.time()

    base = os.getcwd()
    video_folder = os.path.join(base, "Videos")
    rgb_folder = os.path.join(base, "RGBs")
    frames_folder = os.path.join(base, "Frames")

    text_matcher = QueryTextMatcher()
    frame_matcher = QueryFrameMatcher(video_folder, rgb_folder)
    shot_boundary_detector = QueryShotBoundary(mp4_file.split('.mp4')[0])


    shot_boundary_res = None
    shot_found = False
    frames_folders = os.listdir(frames_folder)
    frames_folders.sort()
    for folder in frames_folders:
        # shot_boundary_res = get_video_clip(query_frame_list, os.path.join(os.getcwd(), 'Frames', folder))
        print(folder)
        if "DS_Store" in folder:
            continue
        shot_boundary_res = shot_boundary_detector.get_video_clip(os.path.join(os.getcwd(), 'Frames', folder))
        if shot_boundary_res:
            print("Shot Boundary: ", shot_boundary_res)
            shot_found = True
            break
    
    if not shot_found:
        print("Shot Boundary: ", shot_boundary_res)
        shot_boundary_res = read_scene_greater_than_20()

    matched_chunk = text_matcher.find_query(wav_file, shot_boundary_res)
    print("Matched chunk", matched_chunk)

    # TODO: Audio matching if no text match
    start_frame = None
    if not matched_chunk and shot_found:
        # Assuming that shot boundary exists in query and no text was found
        for video_name, intervals in shot_boundary_res.items():
            print(video_name)
            for interval in intervals:
                matched_chunk = {
                    'video': video_name,
                    'chunk': {
                        'start_time': convert_to_seconds(interval[0]),
                        'end_time': convert_to_seconds(interval[1])
                    }
                }
                start_frame = frame_matcher.find_query(mp4_file, matched_chunk)
                if start_frame:
                    break
            if start_frame:
                break
    elif matched_chunk:
        # textmatching successful          
        start_frame = frame_matcher.find_query(mp4_file, matched_chunk)
    
    if matched_chunk:
        filename = os.path.join(video_folder, matched_chunk['video'] + '.mp4')
        print(start_frame)
        start_time = start_frame / 30  # Assuming 30 FPS
        end_processing_time = time.time()
        print(f"Time taken for total processing: {(end_processing_time - start_processing_time):.5f} seconds")
        play_video(filename, start_time, start_frame)



def play_video(filename, start_time, start_frame):
    app = QApplication(sys.argv)
    videoplayer = VideoPlayer(filename, start_time, start_frame)
    videoplayer.setFixedSize(375, 388)
    videoplayer.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    # if len(sys.argv) != 4:
    #     print("Usage: python script.py <mp4_file> <wav_file> <rgb_file>")
    #     sys.exit(1)

    # mp4_file = sys.argv[1]
    # wav_file = sys.argv[2]
    # rgb_file = sys.argv[3]

    mp4_file = './Queries/video1_1.mp4'
    wav_file = './Queries/audios/video1_1.wav'
    rgb_file = ''
    # start_time = time.time()
    process_video(mp4_file, wav_file, rgb_file)
    # end_time = time.time()
    # print(f"Time taken for everything: {(end_time - start_time):.5f} seconds")