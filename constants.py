import os

base = os.getcwd()
video_folder = os.path.join(base, "Videos")
scene_folder = os.path.join(base, "Scenes")
queries_folder = os.path.join(base, "Queries")
audios_folder = os.path.join(base, "Audios")
db_folder = os.path.join(base, "Database")

sql_create_tasks_table = """CREATE TABLE IF NOT EXISTS tasks (
                                    id integer PRIMARY KEY,
                                    name text NOT NULL,
                                    priority integer,
                                    status_id integer NOT NULL,
                                    project_id integer NOT NULL,
                                    begin_date text NOT NULL,
                                    end_date text NOT NULL,
                                    FOREIGN KEY (project_id) REFERENCES projects (id)
                                );"""