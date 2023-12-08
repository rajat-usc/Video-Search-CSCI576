import os
import constants
from constants import Timer
import cv2 as cv
from time import perf_counter
from tqdm import tqdm
from PIL import Image
import imagehash
import hashlib
import csv
import subprocess
import numpy as np
from collections import defaultdict
from rgb_hash import RGBVideo
import sqlite3


def mp4_to_rgb(video_path: str) -> str:
    video_name = os.path.basename(video_path).split(".")[0]
    output_file_path = os.path.join(constants.query_path, video_name + ".rgb")
    subprocess.run(
        ["ffmpeg", "-i", video_path, "-vf", "format=rgb24", output_file_path]
    )
    return output_file_path


def create_connection(db_file):
    """create a database connection to a SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)

    return conn


# ffmpeg -ss 00:07:47 -i video\video20.mp4 -t 30 -c copy query\video20_2.mp4
def main():
    mc = Timer("main")
    query_processing = Timer("query processing")
    search = Timer("frame search")

    conn = create_connection(constants.DB_NAME)
    if conn is None:
        print(" database connection failed ")
        exit()
    cur = conn.cursor()

    frame_dict: dict = {}

    mc.start()

    # query video -> mp4 to rgb -> get anchor frames
    query_processing.start()
    query_name = "video3_1.mp4"
    if(query_name.endswith("mp4")):
        query_path = os.path.join(constants.query_path, query_name)
        query_rgb_path = mp4_to_rgb(query_path)
    else:
        query_rgb_path = os.path.join(constants.query_path, query_name)
    query = RGBVideo(query_rgb_path)
    query_processing.end()
    print(query.frames)

    # search db for anchor frames
    search.start()
    video_name = ""
    for item, frame in enumerate(query.anchor):
        phash, sha256, _ = query.get_hash(frame)
        result = cur.execute(
            constants.sql_search_frame, (str(phash), str(sha256))
        ).fetchall()

        if result:
            frame_dict[item] = [x[1] for x in result]
            video_name = result[0][0]
        else:
            frame_dict[item] = []
            video_name = None

    if video_name is None:
        print(" no frames found")

    print(f" {video_name=}\n {frame_dict=}")

    search.end()

    # return frames

    mc.end()

    print("\n")
    query_processing.state()
    search.state()
    mc.state()


if __name__ == "__main__":
    main()
