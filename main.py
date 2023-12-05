import sys
from consecutive_matching import get_video_clip
from text_matching.QueryTextMatcher import QueryTextMatcher
from frame_matching.QueryFrameMatcher import QueryFrameMatcher
import os

def main():
    # if len(sys.argv) != 4:
    #     print("python script.py <mp4_file> <wav_file> <rgb_file>")
    #     sys.exit(1)

    # Extracting arguments
    mp4_file = sys.argv[1]
    wav_file = sys.argv[2]
    rgb_file = sys.argv[3]

    mp4_file = './Queries/video6_1.mp4'
    wav_file = './Queries/audio/video6_1.wav'
    rgb_file = ''

    base = os.getcwd()
    video_folder = os.path.join(base, "Videos")

    shot_boundary_res = get_video_clip(mp4_file, './Frames/Video_6_Frames/')
    text_matcher = QueryTextMatcher()
    matched_chunk = text_matcher.find_query(wav_file, shot_boundary_res)
    print(matched_chunk)
    frame_matcher = QueryFrameMatcher(video_folder)
    frame_matcher.find_query(mp4_file, matched_chunk)

    
if __name__ == "__main__":
    main()
