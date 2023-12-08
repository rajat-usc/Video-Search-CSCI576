import os
import constants
import cv2 as cv
from time import perf_counter
from tqdm import tqdm
from PIL import Image
import imagehash
import hashlib
import csv
import subprocess
from collections import defaultdict


class RGBVideo:
    def __init__(self, rgb_path):
        self.height: int = 288
        self.width: int = 352
        self.pixels: int = 101_376
        self.frame_bytes: int = 304_128
        self.total_bytes: int = 0
        self.frames: int = 0
        self.path = rgb_path
        self.b = 0

        self.total_bytes = self.get_total_count()
        self.frames = self.total_bytes // self.frame_bytes
        self.anchor = self.get_anchor_frames()

    def get_total_count(self) -> int:
        count = 0
        b = 0
        with open(self.path, "rb") as f:
            # b = f.read(self.frame_bytes * 30)
            b = f.read()
            count = len(b)
            self.b = b

        # image = Image.frombytes("RGB", (self.width, self.height), b, "raw")
        # print(image.size)
        # image.show()

        return count

    def get_anchor_frames(self) -> tuple:
        first = self.b[: self.frame_bytes]
        last = self.b[-self.frame_bytes :]
        # x = self.frame_bytes * (self.frames // 2)
        # middle = self.b[x : x + self.frame_bytes]
        return (first, last)

    def get_frame(self, x: int):
        anchor = x * self.frame_bytes
        return self.b[anchor : anchor + self.frame_bytes]

    def show_frame(self, frame):
        image = Image.frombytes("RGB", (self.width, self.height), frame, "raw")
        image.show()

    def get_hash(self, frame):
        image = Image.frombytes("RGB", (self.width, self.height), frame, "raw")
        phash_result = imagehash.phash(image, hash_size=16)
        sha256_hash_result = hashlib.sha256(frame).hexdigest()
        average_hash = imagehash.average_hash(image, hash_size=16)

        return (phash_result, sha256_hash_result, average_hash)


def csv_video_hash(video: RGBVideo):
    video_name = os.path.basename(video.path).split(".")[0]
    datafile_path = os.path.join(constants.data_path, video_name + ".csv")
    data = defaultdict(list)

    for i in tqdm(range(video.frames)):
        frame = video.get_frame(i)
        phash, sha256, avghash = video.get_hash(frame)
        data[(str(phash), str(sha256), str(avghash))].append((video_name, i))

    with open(datafile_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        for keys, values in data.items():
            i = ""
            for v in values:
                i += f"{v[1]}:"

            datarow = [keys[0], keys[1], keys[2], video_name, i[: len(i) - 1]]
            writer.writerow(datarow)


def load_data(data_folder: str):
    for f in os.listdir(data_folder):
        datafile = os.path.join(data_folder, f)
        result = subprocess.run(
            [
                "sqlite3",
                "hashtable.db",
                "-cmd",
                ".mode csv",
                f".import '{datafile}' framehash",
            ],
            capture_output=True,
        )
        print(result)


def main():
    start = perf_counter()

    for f in tqdm(os.listdir(constants.rgb_path)):
        rgb_video_path = os.path.join(constants.rgb_path, f)
        rgb_video = RGBVideo(rgb_video_path)
        print(f"frames : {rgb_video.frames}")

        csv_video_hash(rgb_video)

    load_data(constants.data_path)

    end = perf_counter()
    print(f" success : {end-start:.2f}")


# if __name__ == "__main__":
    # total bytes : 5_675_332_608
    # width : 352
    # height : 288
    # duration 10:22
    # frame pixels : 101_376
    # frame bytes : 304_128
    # number of frames : 18_661

    # main()
