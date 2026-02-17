import subprocess
from pathlib import Path

def val_yolo_model(
    dataset_dir: {
        "widget_name": "path_preview",
        "type": str,
        "label": "Dataset folder",
    } = "C:/dataset",

    model_path: {
        "widget_name": "path_preview",
        "type": str,
        "label": "YOLO model (.pt)",
    } = "C:/runs/detect/train/weights/best.pt",

    output_dir: {
        "widget_name": "path_preview",
        "type": str,
        "label": "Output (runs) folder",
    } = "C:/Users/TUF/Downloads/yolo_runs",

    run_name: str = "val_run",

    imgsz: int = 640,
):
    """
    YOLOv8 Validation Node
    """

    dataset_dir = Path(dataset_dir)
    model_path = Path(model_path)
    output_dir = Path(output_dir)

    data_yaml = dataset_dir / "data.yaml"

    if not data_yaml.exists():
        return "data.yaml not found"

    if not model_path.exists():
        return "model not found"

    task = "segment" if model_path.name.endswith("-seg.pt") else "detect"

    cmd = [
        "yolo",
        f"task={task}",
        "mode=val",
        f"model={model_path.as_posix()}",
        f"data={data_yaml.as_posix()}",
        f"imgsz={imgsz}",
        f"project={output_dir.as_posix()}",
        f"name={run_name}",
        "plots=True",
    ]

    subprocess.Popen(cmd)
    return output_dir / run_name


main_callable = val_yolo_model
