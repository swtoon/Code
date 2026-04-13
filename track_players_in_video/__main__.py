import cv2
import os
import numpy as np
from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont

def draw_thai_text(frame, text, position, box_height):

    img_pil = Image.fromarray(frame)
    draw = ImageDraw.Draw(img_pil)

    font_size = max(int(box_height * 0.2), 15)
    font = ImageFont.truetype("tahoma.ttf", font_size)
    x, y = position

    # กล่องพื้นหลัง
    text_w, text_h = draw.textbbox((0,0), text, font=font)[2:]
    padding = 4
    draw.rectangle((x, y, x+text_w+padding, y+text_h+padding), fill=(0,0,0))

    # ตัวหนังสือ
    draw.text((x+5, y+5), text, font=font, fill=(255,255,0))

    return np.array(img_pil)


# ฟังก์ชันสร้างชื่อไฟล์ใหม่ถ้ามีไฟล์เดิมอยู่แล้ว
def get_unique_filename(folder, filename):

    name, ext = os.path.splitext(filename)
    counter = 1
    new_path = os.path.join(folder, filename)

    while os.path.exists(new_path):
        new_filename = f"{name}_{counter}{ext}"
        new_path = os.path.join(folder, new_filename)
        counter += 1

    return new_path


def track_players_in_video(

    input_video_path: {
        "widget_name": "path_preview",
        "type": str,
        "label": "Input video"
    } = "test.mp4",

    save_folder: {
        "widget_name": "path_preview",
        "type": str,
        "label": "Save folder"
    } = "./",

    output_name: str = "tracked_output.avi",

    model_name: {
        "widget_name": "path_preview",
        "type": str,
        "label": "YOLO model"
    } = "yolov8n.pt",

     conf_thres: float = 0.7,

):

    input_video_path = os.path.abspath(input_video_path)
    save_folder = os.path.abspath(save_folder)
    model_name = os.path.abspath(model_name)

    os.makedirs(save_folder, exist_ok=True)

    # สร้างชื่อไฟล์ใหม่ถ้าไฟล์เดิมมีอยู่แล้ว
    output_video_path = get_unique_filename(save_folder, output_name)

    # โหลดโมเดล
    model = YOLO(model_name)

    # เปิดวิดีโอ
    cap = cv2.VideoCapture(input_video_path)

    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {input_video_path}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps == 0:
        fps = 30

    fourcc = cv2.VideoWriter_fourcc(*"XVID")

    out = cv2.VideoWriter(
        output_video_path,
        fourcc,
        fps,
        (width, height)
    )

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        results = model.track(frame, persist=True, verbose=False)

        for r in results:

            if r.boxes is None:
                continue

            for box, cls, conf in zip(r.boxes.xyxy, r.boxes.cls, r.boxes.conf):
                
                if conf < conf_thres:
                    continue

                x1, y1, x2, y2 = map(int, box.tolist())

                class_id = int(cls)
                label = str(model.names.get(class_id, "object"))

                text = f"{label} {conf:.2f}"

                # วาดกรอบ
                cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)

                # วาดข้อความภาษาไทย
                box_h = y2 - y1
                text_y = max(y1 - 20, 0)

                frame = draw_thai_text(frame, text, (x1, text_y), box_h)

        out.write(frame)

    cap.release()
    out.release()

    print("Saved to:", output_video_path)

    return output_video_path


main_callable = track_players_in_video
