from consecutive_matching import get_video_clip
from text_matching.QueryTextMatcher import QueryTextMatcher
from frame_matching.QueryFrameMatcher import QueryFrameMatcher
from media_player_1 import VideoPlayer
import os, time, sys
from PyQt5.QtWidgets import QApplication

                             

def main():
    # Extracting arguments
    mp4_file = sys.argv[1]
    wav_file = sys.argv[2]
    rgb_file = sys.argv[3]

    app = QApplication(sys.argv)

    mp4_file = './Queries/video6_2.mp4'
    wav_file = './Queries/audio/video6_2.wav'
    rgb_file = ''

    start_processing_time = time.time()

    base = os.getcwd()
    video_folder = os.path.join(base, "Videos")
    rgb_folder = os.path.join(base, "RGBs")
    queries_folder = os.path.join(base, "Queries")
    frames_folder = os.path.join(base, "Frames")
    text_matcher = QueryTextMatcher()
    frame_matcher = QueryFrameMatcher(video_folder, rgb_folder)
    
    shot_boundary_res = get_video_clip(mp4_file, './Frames/Video_6_Frames/')
    # TODO(L): if not shot_boundary_res, set shot_boundary_res to scenes > 20
    matched_chunk = text_matcher.find_query(wav_file, shot_boundary_res)
    # print(matched_chunk)

    # TODO: if not matched_chunk, add audio matching
    startFrame = frame_matcher.find_query(mp4_file, matched_chunk)

    startTime = startFrame / 30 # 30 is the FPS
    if matched_chunk:
        filename = os.path.join(os.getcwd(), 'Videos', matched_chunk['video'] + '.mp4')

    end_processing_time = time.time()
    print(f"Time taken for total processing: {(end_processing_time-start_processing_time):.5f} seconds")
    videoplayer = VideoPlayer(filename, startTime, startFrame)
    videoplayer.setFixedSize(375, 388)
    videoplayer.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
