import os

base = os.path.join(os.getcwd(), "Video-Search-CSCI576", "Sample")

video_folder = os.path.join(base, "Video")
scene_folder = os.path.join(base, "Scene")
queries_folder = os.path.join(base, "Query")

DB_NAME = "sample.db"

# sql_create_scenes_table = """CREATE TABLE IF NOT EXISTS scenes (
#                                     scene_name text PRIMARY KEY,
#                                     video_name text NOT NULL,
#                                     start_time integer,
#                                     end_time integer,
#                                     duration integer,
#                                     first_frame text,
#                                     last_frame text,
#                                     audio_name text,
#                                     speech_to_text text
#                                 );"""

# sql_test_command = "SELECT 9 FROM DUAL;"