import os
import numpy as np
import soundfile as sf
from time import perf_counter
import constants
from tqdm import tqdm
from audio_matching import AudioFile
import hashlib
import acoustid


def get_hash(folder: str) -> list:
    hash_list = []
    for f in os.listdir(folder):
        if not f.startswith("video11 -") or not f.endswith(".wav"):
            continue
        path = os.path.join(folder, f)
        x = AudioFile(path)
        print(x.audio)
        result = hashlib.md5(f"{x.audio}".encode()).hexdigest()
        # result = acoustid.fingerprint_file(path)
        # print(result)
        hash_list.append(result)
    return hash_list


def main():
    start = perf_counter()

    # Sample query
    query_path = os.path.join(
        constants.queries_folder, "Scene", "video1 - 5550 - Scene 003.wav"
    )
    # video_path = os.path.join(constants.queries_folder, "video1 - 5550.wav")
    video_path = os.path.join(constants.video_folder, "video1.wav")
    folder = os.path.join(constants.queries_folder, "Scene")

    query_hash = get_hash(folder)
    print(f" query scene hash: {len(query_hash)}")

    video_scene_hash = get_hash(constants.scene_folder)
    print(f" video scene hash: {len(video_scene_hash)}")

    common = set(query_hash).intersection(set(video_scene_hash))
    print(f" common hash : {common}")

    end = perf_counter()
    print(f" success : {end-start:.2f}")


if __name__ == "__main__":
    main()
