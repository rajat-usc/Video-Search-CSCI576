import os
import subprocess
from time import perf_counter
import constants
from tqdm import tqdm


def convert_video_to_audio_ffmpeg(video_file, output_ext="wav"):
    """Converts video to audio directly using `ffmpeg` command
    with the help of subprocess module"""
    filename, ext = os.path.splitext(video_file)
    subprocess.call(
        ["ffmpeg", "-y", "-i", video_file, f"{filename}.{output_ext}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )


def main():
    """generates audio for all videos in video_folder"""
    start = perf_counter()
    video_folder = os.path.join(constants.queries_folder)

    print(f" GENERATING AUDIO FOR VIDEOS : {video_folder}")
    for video in tqdm(os.listdir(video_folder)):
        video_path = os.path.join(video_folder, video)
        convert_video_to_audio_ffmpeg(video_path)

    end = perf_counter()
    print(f" success : {end-start:.2f}s")


if __name__ == "__main__":
    main()
