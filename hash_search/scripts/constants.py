import os
from time import perf_counter

base = "/Users/shalinisaiprasad/Desktop/MMProject/Video-Search-CSCI576/hash_search"#os.getcwd()
scripts_path = os.path.join(base, "scripts")
video_path = os.path.join(base, "video")
rgb_path = os.path.join(base, "rgb")
data_path = os.path.join(base, "data")
query_path = os.path.join(base, "query")
frame_data_path = os.path.join(base, "frame_data")

DB_NAME = os.path.join(base, "hashtable.db")

sql_create_framehash_table = """
CREATE TABLE IF NOT EXISTS framehash ( 
    phash text NOT NULL , 
    sha256 text NOT NULL, 
    averagehash text NOT NULL,
    video_name text NOT NULL,
    video_frame text NOT NULL);
"""

sql_insert_row = """
INSERT INTO framehash VALUES(?,?,?,?);
"""

sql_search_frame = """
SELECT video_name ,video_frame FROM framehash WHERE phash=? and sha256=?;
"""

#
# class Timer:
#     def __init__(self, name: str):
#         self.s = 0
#         self.e = 0
#         self.name = name
#         self.runtime = 0
#
#     def start(self):
#         self.s = perf_counter()
#
#     def end(self):
#         self.e = perf_counter()
#
#     def run(self, precision: int):
#         self.runtime = round(self.e - self.s, precision)
#
#     def state(self):
#         self.run(2)
#         print(f" {self.name} : {self.runtime}s")
#
#
# if __name__ == "__main__":
#     x = Timer("test")
#     x.start()
#     print(f"{base=}")
#     print(f"{scripts_path=}")
#     print(f"{video_path=}")
#     print(f"{rgb_path=}")
#     x.end()
#     x.state()
#     print(x.runtime)
