import cv2
from datetime import datetime
from pathlib import Path
from ultralytics import YOLO
import time
import numpy as np

def camera_viewer_popup(

    camera_index: int = 0,

    model_path: {
        "widget_name":"path_preview",
        "type":str,
        "label":"YOLO model"
    }="yolov8n.pt",

    save_folder: {
        "widget_name":"path_preview",
        "type":str,
        "label":"Save folder"
    }="C:/",

    conf_thres: float = 0.7,

):

    # โหลดโมเดล
    model = YOLO(model_path)

    cap = cv2.VideoCapture(camera_index)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cap.set(cv2.CAP_PROP_FPS, 15)

    if not cap.isOpened():
        return "Cannot open camera"

    frame_count = 0
    prev_frame = None

    window_name = "YOLO Detection | ENTER=Capture | ESC=Close"

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1200, 720)

    frame_counter = 0
    fps = 0
    start_time = time.time()

    while True:

        ret, frame = cap.read()
        if not ret:
            break

        frame_counter += 1

        if time.time() - start_time >= 1:
            fps = frame_counter
            frame_counter = 0
            start_time = time.time()

        frame_count += 1

        if frame_count % 2 == 0:
            results = model(frame, conf=conf_thres, verbose=False)
            annotated_frame = results[0].plot()
            prev_frame = annotated_frame.copy()
        else:
           annotated_frame = prev_frame.copy() if prev_frame is not None else frame.copy()
        
        display_frame = annotated_frame.copy()

        # ใส่ FPS
        cv2.putText(
            display_frame,
            f"FPS: {int(fps)}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2
        )

        try:
            rect = cv2.getWindowImageRect(window_name)
            win_w, win_h = rect[2], rect[3]
        except:
            win_w, win_h = 0, 0

        if win_w <= 0 or win_h <= 0:
            cv2.imshow(window_name, display_frame)
            continue

        h, w = display_frame.shape[:2]

        scale = min(win_w / w, win_h / h)
        new_w, new_h = int(w * scale), int(h * scale)

        resized = cv2.resize(display_frame, (new_w, new_h))

        canvas = np.zeros((win_h, win_w, 3), dtype=np.uint8)

        x_offset = (win_w - new_w) // 2
        y_offset = (win_h - new_h) // 2

        canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized

        display_frame = canvas

        cv2.imshow(window_name, display_frame)

        key = cv2.waitKey(1) & 0xFF

        # ESC ปิด
        if key == 27:
            break

        # ENTER ถ่ายภาพ
        elif key == 13:

            filename = datetime.now().strftime("capture_%Y%m%d_%H%M%S.png")

            save_path = Path(save_folder) / filename

            cv2.imwrite(str(save_path), annotated_frame)

            print("Saved:", save_path)

    cap.release()
    cv2.destroyAllWindows()

    return "Closed"


main_callable = camera_viewer_popup
