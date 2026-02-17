from pathlib import Path
import pygame
from math import ceil

# =========================
# 1. CONFIG (ต้องมีเพื่อให้ฟังก์ชันเรียกใช้ได้)
# =========================
THUMB_SIZE = (128, 128)
PREVIEW_MAX_SIZE = (400, 400)
PADDING = 8
BG_COLOR = (30, 30, 30)

# =========================
# 2. UTILS (ฟังก์ชันที่ระบบแจ้งว่าหาไม่เจอ)
# =========================
def scale_keep_ratio(surface, max_size):
    w, h = surface.get_size()
    mw, mh = max_size
    scale = min(mw / w, mh / h, 1)
    return pygame.transform.smoothscale(    
        surface, (int(w * scale), int(h * scale))
    )

def make_grid(images, thumb_size, max_width=None):
    if not images:
        return None

    cols = max_width // (thumb_size[0] + PADDING) if max_width else 4
    cols = max(cols, 1)
    rows = ceil(len(images) / cols)

    width = cols * thumb_size[0] + (cols + 1) * PADDING
    height = rows * thumb_size[1] + (rows + 1) * PADDING

    surface = pygame.Surface((width, height))
    surface.fill(BG_COLOR)

    for i, img in enumerate(images):
        thumb = pygame.transform.smoothscale(img, thumb_size)
        x = PADDING + (i % cols) * (thumb_size[0] + PADDING)
        y = PADDING + (i // cols) * (thumb_size[1] + PADDING)
        surface.blit(thumb, (x, y))

    return surface

# =========================
# 3. MAIN NODE
# =========================
def view_images_from_list(
    image_paths: list = [], # รับค่า list ของ Path จาก node ก่อนหน้า
):
    if not image_paths:
        return None

    images = []
    for p in image_paths:
        try:
            path_str = str(p) 
            img = pygame.image.load(path_str).convert_alpha()
            images.append(img)
        except Exception as e:
            print(f"Error loading {p}: {e}")
            pass

    if not images:
        return None

    # เรียกใช้ make_grid (ตอนนี้มีฟังก์ชันรองรับแล้ว)
    full_surface = make_grid(
        images,
        THUMB_SIZE,
        max_width=1200
    )

    # เรียกใช้ scale_keep_ratio
    preview_surface = scale_keep_ratio(
        full_surface,
        PREVIEW_MAX_SIZE
    )

    return {
        'preview_surface': preview_surface,
        'full_surface': full_surface,
    }

main_callable = view_images_from_list

# =========================
# 4. VIEWER HOOKS
# =========================
get_sideviz_from_output = lambda o: o['preview_surface'] if (o and 'preview_surface' in o) else None
get_loopviz_from_output = lambda o: o['full_surface'] if (o and 'full_surface' in o) else None