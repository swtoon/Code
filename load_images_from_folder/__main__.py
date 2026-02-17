from pathlib import Path

def load_images_from_folder(
    folder_path: {
        'widget_name': 'path_preview',
        'type': str,
    } = '.',
):
    folder = Path(folder_path)
    images = list(folder.glob('*.png')) + list(folder.glob('*.jpg')) + list(folder.glob('*.jpeg'))
    return images

main_callable = load_images_from_folder
