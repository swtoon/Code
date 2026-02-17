import subprocess
from pathlib import Path

def train_yolo_model(
    dataset_dir: {
        "widget_name": "path_preview",
        "type": str,
        "label": "Dataset folder",
    } = "C:/Users/TUF/Downloads/dataset_A",

    output_dir: {
        "widget_name": "path_preview",
        "type": str,
        "label": "Output (runs) folder",
    } = "C:/Users/TUF/Downloads/yolo_runs",

    run_name: str = "train1",
    model: str = "yolov8n-seg.pt",
    epochs: int = 100,
    imgsz: int = 640,
):
    """
    Train YOLOv8 model (custom output directory)
    """

    dataset_dir = Path(dataset_dir)
    data_yaml = dataset_dir / "data.yaml"

    if not data_yaml.exists():
        return "data.yaml not found"

    cmd = [
        "yolo",
        "segment",
        "train",
        f"model=yolov8n-seg.pt",   # เป็น seg
        f"data={data_yaml.as_posix()}",
        f"epochs={epochs}",
        f"imgsz={imgsz}",
        f"project={Path(output_dir).as_posix()}",
        f"name={run_name}",
    ]


    subprocess.Popen(cmd)
    return f"YOLO training started → {output_dir}/{run_name}"
    

main_callable = train_yolo_model
