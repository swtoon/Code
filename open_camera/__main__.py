import cv2
from datetime import datetime
from pathlib import Path
import platform


def open_camera(

    camera_index: int = 0,

    save_folder: {
        "widget_name":"path_preview",
        "type":str,
        "label":"Save folder"
    }="Project/captures",

):

    if platform.system() == "Linux":
        cap = cv2.VideoCapture(camera_index, cv2.CAP_V4L2)

        if not cap.isOpened():
            cap = cv2.VideoCapture(camera_index)
    else:
        cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        return f"Cannot open camera index {camera_index}"

    window_name = "Camera Viewer | ENTER=Capture | ESC=Close"

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1200, 720)

    while True:

        ret, frame = cap.read()

        if not ret or frame is None:
            break

        cv2.imshow(window_name, frame)

        key = cv2.waitKey(1) & 0xFF

        # ESC = ปิด
        if key == 27:
            break

        # ENTER = แคปรูป
        elif key == 13:

            save_folder_path = Path(save_folder)
            save_folder_path.mkdir(parents=True, exist_ok=True)

            filename = datetime.now().strftime(
                "capture_%Y%m%d_%H%M%S.png"
            )

            save_path = save_folder_path / filename

            success = cv2.imwrite(str(save_path), frame)

            if success:
                print("Saved:", save_path)
            else:
                print("Failed to save:", save_path)

    cap.release()
    cv2.destroyAllWindows()

    return "Closed"


main_callable = open_camera