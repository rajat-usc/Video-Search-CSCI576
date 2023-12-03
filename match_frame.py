import cv2
from skimage.metrics import structural_similarity as ssim

def get_first_frame(video_path):
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cap.release()
    return frame if ret else None

def is_frame_match(frame1_gray, frame2_gray, threshold=0.9):
    s = ssim(frame1_gray, frame2_gray)
    return s >= threshold

def find_matching_frame_time(main_video_path, target_video_path, start_time, skip=2, interval=30):
    target_frame = get_first_frame(target_video_path)
    target_frame_gray = cv2.cvtColor(target_frame, cv2.COLOR_BGR2GRAY)
    cap = cv2.VideoCapture(main_video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    start_frame_number = int(start_time * fps)
    end_frame_number = int((start_time + interval) * fps)

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame_number)

    frame_counter = 0 

    while True:
        ret, frame = cap.read()
        frame_counter += 1

        if not ret or cap.get(cv2.CAP_PROP_POS_FRAMES) > end_frame_number:
            break

        if frame_counter % skip == 0: #Number of frames to skip
            continue
        
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if (not frame_gray is None) and (not target_frame is None) and is_frame_match(frame_gray, target_frame_gray):
            exact_time = (cap.get(cv2.CAP_PROP_POS_FRAMES) - 1) / fps
            cap.release()
            return exact_time

    cap.release()
    return None