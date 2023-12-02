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
                                    start_time text NOT NULL,
                                    end_time text NOT NULL,
                                    duration integer NOT NULL,
                                    first_frame text NOT NULL,
                                    last_frame text NOT NULL,
                                    audio_name text NOT NULL,
                                    speech_to_text text NOT NULL,
                                );"""
