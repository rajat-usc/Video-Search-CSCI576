import os
import cv2
from PIL import Image
import numpy as np
import imagehash


def convert_to_rgb(input_path, output_path):
    # Open the image file
    img = Image.open(input_path)

    # Convert to RGB mode
    rgb_img = img.convert('RGB')

    # Save as .rgb file using numpy
    rgb_data = np.array(rgb_img)
    with open(output_path, 'wb+') as f:
        f.write(rgb_data.tobytes())


def extract_frames(video_path, o_path_first, o_path_last):
    # Open the video file
    cap = cv2.VideoCapture(video_path)

    # Get the total number of frames in the video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Extract the first frame
    ret, first_frame = cap.read()
    cv2.imwrite(o_path_first, first_frame)

    # Extract the last frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames - 1)
    ret, last_frame = cap.read()
    cv2.imwrite(o_path_last, last_frame)

    # Release the video capture object
    cap.release()


def scenes_to_frames(scene_folder_name, frame_folder_name):
    # folder_name = "Scenes/Video_"+str(i)+"_Scenes/"
    frame_folder_name = "Frames/" + frame_folder_name
    video_list = os.listdir(scene_folder_name)
    video_list.sort()

    for file in video_list:
        # Output paths for first and last frames
        output_path_first = frame_folder_name + file + "_first_frame.png"
        output_path_last = frame_folder_name + file + "_last_frame.png"

        # Extract frames from the video
        extract_frames(scene_folder_name + file, output_path_first, output_path_last)

        # Convert frames to .rgb format
        convert_to_rgb(output_path_first, "first_frame.rgb")
        convert_to_rgb(output_path_last, "last_frame.rgb")


scenes_to_frames("Scenes/Video_1_Scenes", "Video_1_Frames")
