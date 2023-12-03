import os
import acoustid
from time import perf_counter
from scenedetect import detect, AdaptiveDetector, split_video_ffmpeg
import constants


def generate_scenes(video_folder: str, dest_folder: str) -> int:
    print(f"\n video folder : {video_folder}\n destination folder : {dest_folder}\n ")
    result = 1

    for video in os.listdir(video_folder):
        video_path = os.path.join(video_folder, video)
        scene_list = detect(video_path, AdaptiveDetector())
        print(f" {video} : {len(scene_list)}")
        try:
            split_video_ffmpeg(
                video_path,
                scene_list,
                os.path.join(dest_folder, "$VIDEO_NAME - Scene $SCENE_NUMBER.mp4"),
                show_progress=True,
            )
        except Exception as e:
            print(f" fail : {video}\n {e}")
            result = 0

    return result


def main():
    start = perf_counter()
    result = generate_scenes(constants.video_folder, constants.scene_folder)
    end = perf_counter()
    runtime = end - start

    if not result:
        print(f" error encountered : {runtime:.2f}s")
    else:
        print(f" success : {runtime:.2f}s")


if __name__ == "__main__":
    main()
