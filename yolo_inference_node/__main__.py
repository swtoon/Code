import subprocess
from pathlib import Path


def yolo_inference_node(
    image_dir: {
        "widget_name": "path_preview",
        "type": str,
        "label": "Image folder",
    } = "C:/",

    model_path: {
        "widget_name": "path_preview",
        "type": str,
        "label": "YOLO model (.pt)",
    } = "C:/best.pt",

    output_dir: {
        "widget_name": "path_preview",
        "type": str,
        "label": "Output folder (project)",
    } = "C:/Users/TUF/Downloads/yolo_runs",

    task: str = "segment",

    run_name: str = "predict_run",

    imgsz: int = 640,
    conf: float = 0.25,
):
    """
    YOLO Inference Node (Nodezator)
    - Run YOLO detect predict
    - Return output folder path
    """

    image_dir = Path(image_dir)
    model_path = Path(model_path)
    output_dir = Path(output_dir)

    if not image_dir.exists():
        return "Image folder not found"

    if not model_path.exists():
        return "Model not found"

    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "yolo",
        f"task={task}",
        "mode=predict",
        f"model={model_path.as_posix()}",
        f"source={image_dir.as_posix()}",
        f"imgsz={imgsz}",
        f"conf={conf}",
        f"project={output_dir.as_posix()}",
        f"name={run_name}",
        "save=True",
    ]

    if task == "segment":
        cmd += [
            "save_txt=True",   # polygon/mask
            "save_conf=True",
        ]

    subprocess.Popen(cmd)

    # ส่ง path ของโฟลเดอร์ผลลัพธ์ออกไป
    return output_dir / run_name

main_callable = yolo_inference_node
