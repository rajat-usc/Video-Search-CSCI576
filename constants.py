import os

base = os.getcwd()
video_folder = os.path.join(base, "Videos")
scene_folder = os.path.join(base, "Scenes")
queries_folder = os.path.join(base, "Queries")
audios_folder = os.path.join(base, "Audios")
db_folder = os.path.join(base, "Database")

sql_create_scenes_table = """CREATE TABLE IF NOT EXISTS scenes (
                                    scene_name text PRIMARY KEY,
                                    video_name text NOT NULL,
                                    start_time integer,
                                    end_time integer,
                                    duration integer,
                                    first_frame text,
                                    last_frame text,
                                    audio_name text,
                                    speech_to_text text
                                );"""

sql_test_command = "SELECT 9 FROM DUAL;"
