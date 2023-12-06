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
    rgb_folder = os.path.join(base, "RGBs")
    queries_folder = os.path.join(base, "Queries")
    frames_folder = os.path.join(base, "Frames")
    text_matcher = QueryTextMatcher()
    frame_matcher = QueryFrameMatcher(video_folder, rgb_folder)

    # queries = os.listdir(queries_folder)
    # for query in queries:
    #     if query.endswith('.mp4'):
    #         print(query)
    #         video_num = int(query.split('/')[-1].split('.')[0][-1])
    #         if os.path.exists(f'./Frames/Video_{video_num}_Frames'):
    #             shot_boundary_res = get_video_clip('./Queries/' + query, './Frames/Video_1_Frames/')
    #         matched_chunk = text_matcher.find_query('./Queries/audio/' + query.split('.')[0] + '.wav', shot_boundary_res)
    #         print(matched_chunk)
    #         if matched_chunk:
    #             frame_matcher.find_query('./Queries/' + query, matched_chunk)

    
    shot_boundary_res = get_video_clip(mp4_file, './Frames/Video_6_Frames/')
    text_matcher = QueryTextMatcher()
    matched_chunk = text_matcher.find_query(wav_file, shot_boundary_res)
    # TODO(L): if not matched_chunk, set matched_chunk to scenes > 20
    # print(matched_chunk)
    frame_matcher = QueryFrameMatcher(video_folder, rgb_folder)
    frame_matcher.find_query(mp4_file, matched_chunk)



    
if __name__ == "__main__":
    main()
