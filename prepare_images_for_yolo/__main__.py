from pathlib import Path
import shutil

def prepare_images_for_yolo(
    image_paths: list = [],

    dataset_dir: {
        "widget_name": "path_preview",
        "type": str,
        "label": "Dataset folder",
    } = "C:/",

    split: str = "train",
):
    """
    Copy images into YOLO structure:
    dataset/images/train or dataset/images/val
    """

    if not image_paths:
        return "No images"

    dataset_dir = Path(dataset_dir)
    images_dir = dataset_dir / f"images/{split}"
    images_dir.mkdir(parents=True, exist_ok=True)

    copied = 0
    for img in image_paths:
        img = Path(img)
        dst = images_dir / img.name
        if not dst.exists():
            shutil.copy2(img, dst)
            copied += 1

    return f"Copied {copied} images to images/{split}"


main_callable = prepare_images_for_yolo
