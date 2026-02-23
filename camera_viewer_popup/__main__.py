import cv2
from datetime import datetime
from pathlib import Path

def camera_viewer_popup(
    camera_index: int = 0,
    save_folder: {
        "widget_name":"path_preview",
        "type":str,
        "label":"Save folder",
    }="C:/",
):

    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        return "Cannot open camera"
    
    window_name = "ENTER = Capture | ESC = Close"

    # 🔥 ทำให้หน้าต่างปรับขนาดได้
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    # ตั้งขนาดหน้าจอเริ่มต้น
    cv2.resizeWindow(window_name, 1200, 720)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("ENTER = Capture | ESC = Close", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == 27:  # ESC
            break

        elif key == 13:  # ENTER
            filename = datetime.now().strftime("capture_%Y%m%d_%H%M%S.png")
            save_path = Path(save_folder) / filename
            cv2.imwrite(str(save_path), frame)
            print("Saved:", save_path)

    cap.release()
    cv2.destroyAllWindows()

    return "Closed"

main_callable = camera_viewer_popup
