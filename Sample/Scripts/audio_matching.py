import os
import numpy as np
import soundfile as sf
from time import perf_counter
import constants
from tqdm import tqdm


class AudioFile:
    def __init__(self, file_path: str):
        self.audio = None
        self.fs: int = 0
        self.duration: float = 0.0
        self.audio, self.fs, self.duration = self.read_audio(file_path)
        self.length = self.audio.shape[0]

    def __str__(self) -> str:
        return f" audio size : {self.length}\n fs : {self.fs}\n duration : {self.duration:.2f}\n"

    def read_audio(self, file_path: str):
        x, fs = sf.read(file_path)
        return (x, fs, x.shape[0] / fs)


def l2(a: np.ndarray, b: np.ndarray) -> float:
    return np.sum((a - b) ** 2)


def audio_match(query: AudioFile, video: AudioFile) -> tuple[int, int]:
    window: int = query.length
    ratio: float = 0.05
    stride: int = int(ratio * window)

    assert window <= video.length
    x = 0
    min_distance = np.inf
    frame = 0
    print(f" iterations : {(video.length-window)//stride}  stride : {stride}")
    pbar = tqdm(total=(video.length - window) // stride)

    while x <= (video.length - window):
        search_window = video.audio[x : x + window]
        distance = np.linalg.norm(search_window - query.audio)
        # distance = l2(search_window, query.audio)
        if distance < min_distance:
            min_distance = distance
            frame = x
        x += stride
        pbar.update(1)
    pbar.close()
    # print(f" {min_distance=}  {frame=}  timestamp={frame/video.fs}")

    granularity = stride // 100
    for c in tqdm(range(frame - granularity, frame + granularity)):
        search_window = video.audio[c : c + window]
        distance = np.linalg.norm(search_window - query.audio)
        # distance = l2(search_window, query.audio)
        if distance < min_distance:
            min_distance = distance
            frame = c

    start, end = (frame / video.fs), ((frame + window) / video.fs)
    start_frame, end_frame = start * 30, end * 30

    print(f" {min_distance=}  time={int(start//60)}:{round(start%60)}")

    return (round(start_frame), round(end_frame))


def main():
    start = perf_counter()

    # Sample query
    # query_path = os.path.join(
    #     constants.queries_folder, "Scene", "video1 - 5550 - Scene 003.wav"
    # )
    query_path = os.path.join(constants.queries_folder, "video11 - 11400.wav")
    # video_path = os.path.join(constants.queries_folder, "video1 - 5550.wav")
    video_path = os.path.join(constants.video_folder, "video11.wav")

    # Audio objects
    query = AudioFile(query_path)
    video = AudioFile(video_path)
    print(query)
    print(video)

    # Audio matching
    result = audio_match(query, video)
    print(f" frames: {result[0]} - {result[1]}")

    end = perf_counter()
    print(f" success : {end-start:.2f}")


if __name__ == "__main__":
    main()
