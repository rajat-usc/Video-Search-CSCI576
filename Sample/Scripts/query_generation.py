import os
import acoustid
from time import perf_counter
from scenedetect import detect, AdaptiveDetector, split_video_ffmpeg
import scenedetect
import constants
import csv


def split_video(num: str, scene_list: list):
    video_path = os.path.join(constants.video_folder, f"video{num}.mp4")
    try:
        split_video_ffmpeg(
            video_path,
            scene_list,
            os.path.join(constants.queries_folder, "$VIDEO_NAME - $SCENE_NUMBER.mp4"),
        )
    except Exception as e:
        print(f" failure : {video_path}\n timestamp : {scene_list}")
        print(e)


def ts_to_float(timestamp: str) -> float:
    minutes, seconds = timestamp.split(":")
    result = (int(minutes) * 60) + int(seconds)
    return float(result)


def generate_queries(query_list: list) -> int:
    x = 0
    for row in query_list:
        video_number: str = row["video"]
        start: float = ts_to_float(row["start"])
        end: float = ts_to_float(row["end"])
        start_timecode = scenedetect.FrameTimecode(start, 30)
        end_timecode = scenedetect.FrameTimecode(end, 30)
        time_split = tuple([start_timecode, end_timecode])
        try:
            print(video_number, time_split)
            split_video(video_number, [time_split])
            x += 1
        except Exception as e:
            print(f" error: {e} ")

    return x


def fetch_queries(filepath: str) -> list[dict]:
    """returns a list of dictionaries : [video, start, end]"""
    result = []
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            result.append(row)
    return result


def main():
    start = perf_counter()
    query_path = os.path.join(constants.queries_folder, "queries.csv")
    query_list = fetch_queries(query_path)
    print(f" queries fetched : {len(query_list)}")
    result = generate_queries(query_list)
    print(f" generated {result} queries")
    end = perf_counter()
    print(f" success : {end-start:.2f}s")


if __name__ == "__main__":
    main()
