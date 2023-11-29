import cv2
import os


def sortKey(string) -> int:
    return int(string.replace("Gen","").replace(".png",""))

frames_dir = './100x100-Video'

frames = [img for img in os.listdir(frames_dir) if img.endswith(".png")]

frames.sort(key = sortKey)

fourcc = cv2.VideoWriter_fourcc(*'h264')
video = cv2.VideoWriter('100x100.mp4', fourcc, 60.0, (100, 100))

for frame in frames:
    img_path = os.path.join(frames_dir, frame)
    img = cv2.imread(img_path)
    video.write(img)

video.release()
