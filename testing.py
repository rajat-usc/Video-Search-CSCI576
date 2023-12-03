import os
import acoustid
from time import perf_counter
from scenedetect import detect, AdaptiveDetector, split_video_ffmpeg
import chromaprint
import audiodiff

print(' imports done')