from pathlib import Path
import pygame
import json
import colorsys
import copy
import yaml

# =====================
# CONFIG
# =====================
HANDLE_SIZE = 8
IMG_WIDTH = 900
IMG_HEIGHT = 700
SIDEBAR_WIDTH = 220
WINDOW_SIZE = (IMG_WIDTH + SIDEBAR_WIDTH, IMG_HEIGHT)

BG_COLOR = (30, 30, 30)
BOX_THICKNESS = 2
FONT_COLOR = (220, 220, 220)

def detect_corner(mx, my, x, y, w, h):
    corners = {
        "tl": (x, y),
        "tr": (x + w, y),
        "bl": (x, y + h),
        "br": (x + w, y + h),
    }
    for name, (cx, cy) in corners.items():
        if abs(mx - cx) < HANDLE_SIZE and abs(my - cy) < HANDLE_SIZE:
            return name
    return None

# =====================
# COLOR GENERATOR
# =====================
def get_class_color(cid: int):
    hue = (cid * 0.61803398875) % 1.0
    r, g, b = colorsys.hsv_to_rgb(hue, 0.85, 1.0)
    return int(r * 255), int(g * 255), int(b * 255)


# =====================
# TOOLTIP TEXT
# =====================
TOOLTIP_LINES = [
    "🖱️ Mouse:",
    "  Drag        : Draw box",
    "  Click box   : Select box",
    "",
    "⌨️ Keyboard:",
    "  Enter       : Confirm box",
    "  Backspace   : Delete typing",
    "  Delete      : Delete selected box",
    "  Ctrl + U    : Undo last box",
    "  Ctrl + C    : Clear all boxes",
    "  Ctrl + Y    : Redo box",
    "  Ctrl + P    : polygon box",
    "",
    "🧠 Class:",
    "  Type name   : Create new class",
    "  ↑ / ↓       : Change class",
    "",
    "🖼️ Images:",
    "  ← / →       : Prev / Next image",
    "  Alt + N     : Next image",
    "",
    "🚪 Exit:",
    "  ESC         : Exit annotator",
    "  H           : Toggle help",
]


def draw_tooltip(screen, font, visible=True):
    if not visible:
        return

    padding = 8
    line_h = 20
    width = 320
    height = line_h * len(TOOLTIP_LINES) + padding * 2

    x = IMG_WIDTH - width - 10
    y = IMG_HEIGHT - height - 10

    # background
    s = pygame.Surface((width, height), pygame.SRCALPHA)
    s.fill((0, 0, 0, 170))
    screen.blit(s, (x, y))

    # text
    ty = y + padding
    for line in TOOLTIP_LINES:
        txt = font.render(line, True, (230, 230, 230))
        screen.blit(txt, (x + padding, ty))
        ty += line_h


def draw_class_list(screen, font, class_map, active_class_id):
    click_areas = []

    x = IMG_WIDTH + 10
    y = 20
    title = font.render("CLASSES", True, (255, 255, 255))
    screen.blit(title, (x, y))
    y += 30

    for name, cid in sorted(class_map.items(), key=lambda x: x[1]):
        rect = pygame.Rect(x, y, SIDEBAR_WIDTH - 20, 22)
        color = get_class_color(cid)
        prefix = "▶ " if cid == active_class_id else "  "
        txt = font.render(f"{prefix}{cid}: {name}", True, color)
        screen.blit(txt, (x, y))
        click_areas.append((rect, cid))
        y += 24

    return click_areas

def draw_class_menu(screen, font, menu):
    if not menu:
        return []

    x, y = menu["pos"]
    w, h = 120, 30

    pygame.draw.rect(screen, (40,40,40), (x, y, w, h))
    pygame.draw.rect(screen, (200,200,200), (x, y, w, h), 1)

    r = pygame.Rect(x, y, w, 30)
    screen.blit(font.render("Delete", True, (255,255,255)), (x+10, y+6))

    return [(r, "delete")]

def draw_confirm_popup(screen, font, data):
    if not data:
        return []

    w, h = 300, 120
    x = IMG_WIDTH//2 - w//2
    y = IMG_HEIGHT//2 - h//2

    pygame.draw.rect(screen, (50,50,50), (x,y,w,h))
    pygame.draw.rect(screen, (220,220,220), (x,y,w,h), 2)

    screen.blit(font.render("Delete this class?", True, (255,255,255)), (x+50, y+20))

    yes = pygame.Rect(x+40, y+70, 80, 30)
    no  = pygame.Rect(x+180, y+70, 80, 30)

    pygame.draw.rect(screen, (200,50,50), yes)
    pygame.draw.rect(screen, (80,80,80), no)

    screen.blit(font.render("Yes", True, (255,255,255)), (yes.x+25, yes.y+5))
    screen.blit(font.render("No", True, (255,255,255)), (no.x+30, no.y+5))

    return [(yes,"yes"), (no,"no")]

def write_data_yaml(dataset_dir: Path, class_map: dict):
    if not class_map:
        return

    names = [None] * len(class_map)
    for name, cid in class_map.items():
        names[cid] = name

    data = {
        "path": dataset_dir.as_posix(),
        "train": "images/train",
        "val": "images/val",
        "nc": len(names),
        "names": names,
    }

    yaml_path = dataset_dir / "data.yaml"
    yaml_path.write_text(
        yaml.dump(data, sort_keys=False, allow_unicode=True),
        encoding="utf-8"
    )

# =====================
# MAIN TOOL
# =====================
def annotate_images_pygame(
    image_paths: list = [],

    dataset_dir: {
        "widget_name":"path_preview",
        "type":str,
        "label":"Dataset folder",
    }="C:/",
    project_dir: {
        "widget_name":"path_preview",
        "type":str,
        "label":"Project folder (shared classes)",
    }="C:/",
    split: str = "train",
):

    if not image_paths:
        return "No images to label"

    dataset_dir = Path(dataset_dir)
    labels_dir = dataset_dir / f"labels/{split}"
    labels_dir.mkdir(parents=True, exist_ok=True)

    project_dir = Path(project_dir)
    project_dir.mkdir(parents=True, exist_ok=True)

    class_map_path = project_dir / "classes.json"
    class_map = json.loads(class_map_path.read_text()) if class_map_path.exists() else {}

    def get_class_id(name):
        if name not in class_map:
            class_map[name] = len(class_map)
            class_map_path.write_text(json.dumps(class_map, indent=2))
        return class_map[name]

    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption(f"YOLO Annotation Tool [{split}]")
    clock = pygame.time.Clock()
    try:
        font = pygame.font.SysFont("Segoe UI Emoji", 22)
    except:
        font = pygame.font.SysFont("Segoe UI", 22)


    active_class_id = 0
    show_help = True

    idx = 0
    while 0 <= idx < len(image_paths):
        img_path = Path(image_paths[idx])
        label_file = labels_dir / f"{img_path.stem}.txt"

        image = pygame.image.load(str(img_path)).convert_alpha()
        iw, ih = image.get_size()
        scale = min(IMG_WIDTH / iw, IMG_HEIGHT / ih)
        disp_size = (int(iw * scale), int(ih * scale))
        image_disp = pygame.transform.smoothscale(image, disp_size)
        selected_idx = None
        polygon_mode = False
        current_polygon = []

        boxes = []
        if label_file.exists():
            for line in label_file.read_text().splitlines():
                parts = list(map(float, line.split()))
                cid = int(parts[0])

            # ===== SEGMENTATION =====
                if len(parts) > 5:
                    pts = parts[1:]
                    mask = [
                        (pts[i] * disp_size[0], pts[i+1] * disp_size[1])
                        for i in range(0, len(pts), 2)
                    ]

                    xs = [p[0] for p in mask]
                    ys = [p[1] for p in mask]
                    x = min(xs)
                    y = min(ys)
                    w = max(xs) - x
                    h = max(ys) - y

                    boxes.append((x, y, w, h, cid, mask))

                # ===== BBOX =====
                else:
                    _, xc, yc, bw, bh = parts
                    boxes.append((
                        (xc - bw/2) * disp_size[0],
                        (yc - bh/2) * disp_size[1],
                        bw * disp_size[0],
                        bh * disp_size[1],
                        cid,
                        None
                    ))  

        # ===== UNDO STACK =====
        undo_stack = []
        redo_stack = []
        selected_idx = None

        class_menu = None        # {"cid": int, "pos": (x,y)}
        confirm_delete = None    # {"cid": int}


        def push_undo():
            undo_stack.append(copy.deepcopy(boxes))
            redo_stack.clear()

        current_box = None
        drawing = False
        label_text = ""

        polygon_mode = False        # โหมดวาด polygon
        current_polygon = []        # จุดของ polygon ปัจจุบัน

        resizing = False
        resize_corner = None
        resize_start = None

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "Exited"

                if event.type == pygame.KEYDOWN:
                    mods = pygame.key.get_mods()

                    if event.key == pygame.K_ESCAPE:
                        if polygon_mode:
                            polygon_mode = False
                            current_polygon = []
                            continue
                        if confirm_delete:
                            confirm_delete = None
                            drawing = False
                            current_box = None
                            continue
                        if class_menu:
                            class_menu = None
                            continue
                        write_data_yaml(dataset_dir, class_map)
                        return "Exited"
                    
                    elif event.key == pygame.K_RETURN and polygon_mode:
                        if selected_idx is not None and len(current_polygon) >= 3:
                            old = boxes[selected_idx]
                            x, y, w, h, cid = old[:5]

                            push_undo()
                            boxes[selected_idx] = (
                                x, y, w, h,
                                cid,
                                current_polygon.copy()
                                )

                        current_polygon = []
                        polygon_mode = False
                   
                    elif event.key == pygame.K_u and mods & pygame.KMOD_CTRL:
                        if undo_stack:
                            redo_stack.append(copy.deepcopy(boxes))
                            boxes[:] = undo_stack.pop()
                   
                    elif event.key == pygame.K_y and mods & pygame.KMOD_CTRL:
                        if redo_stack:
                            undo_stack.append(copy.deepcopy(boxes))  # กลับไป undo ได้
                            boxes[:] = redo_stack.pop()

                    elif event.key == pygame.K_c and mods & pygame.KMOD_CTRL:
                        if boxes:
                            push_undo()
                            boxes.clear()

                    elif event.key == pygame.K_h and mods & pygame.KMOD_CTRL:
                        show_help = not show_help

                    elif event.key == pygame.K_p and mods & pygame.KMOD_CTRL:
                        if selected_idx is not None:
                            polygon_mode = not polygon_mode
                            current_polygon = []

                    elif event.key == pygame.K_LEFT:
                        idx -= 1
                        selected_idx = None
                        polygon_mode = False
                        current_polygon = []
                        running = False

                    elif event.key == pygame.K_RIGHT or (event.key == pygame.K_n and mods & pygame.KMOD_ALT):
                        idx += 1
                        selected_idx = None
                        polygon_mode = False
                        current_polygon = []
                        running = False

                    elif event.key == pygame.K_UP:
                        # กรณีกำลังวาดกรอบใหม่ (ยังไม่กด Enter)
                        if current_box:
                            active_class_id = max(0, active_class_id - 1)
                        
                         # กรณีเลือก box ที่มีอยู่แล้ว
                        elif selected_idx is not None:
                            push_undo()
                            active_class_id = max(0, active_class_id - 1)
                            x, y, w, h, _, mask = boxes[selected_idx]
                            boxes[selected_idx] = (x, y, w, h, active_class_id, mask)

                    elif event.key == pygame.K_DOWN:
                        max_cid = max(len(class_map) - 1, 0)

                        # กรณีกำลังวาดกรอบใหม่ (ยังไม่กด Enter)
                        if current_box:
                            active_class_id = min(max_cid, active_class_id + 1)

                        # กรณีเลือก box ที่มีอยู่แล้ว
                        elif selected_idx is not None:
                            push_undo()
                            active_class_id = min(max_cid, active_class_id + 1)
                            x, y, w, h, _, mask = boxes[selected_idx]
                            boxes[selected_idx] = (x, y, w, h, active_class_id, mask)
    
                    elif event.key == pygame.K_DELETE and selected_idx is not None:
                        push_undo()            # ถ้ามี Undo
                        boxes.pop(selected_idx)
                        selected_idx = None

                    elif event.key == pygame.K_RETURN and current_box:
                        push_undo()  # ⬅️ เก็บก่อนแก้
                        if label_text.strip():
                            active_class_id = get_class_id(label_text.strip())
                            write_data_yaml(dataset_dir, class_map)  # ✅ เพิ่มบรรทัดนี้
                        boxes.append((*current_box, active_class_id, None)) #เพิ่ม
                        current_box = None
                        label_text = ""

                    elif event.key == pygame.K_BACKSPACE:
                        label_text = label_text[:-1]

                    else:
                        if event.unicode.isalnum() or event.unicode in "_-":
                            label_text += event.unicode

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos

                    if polygon_mode:
                        current_polygon.append((mx, my))
                        continue   # ⬅️ สำคัญมาก กันไม่ให้ไปโดน logic box

                    if confirm_delete:
                        mx, my = event.pos
                        for r, act in confirm_actions:
                            if r.collidepoint(mx, my):
                                if act == "yes":
                                    push_undo()
                                    cid = confirm_delete["cid"]

                                    name = next(k for k,v in class_map.items() if v == cid)
                                    class_map.pop(name)

                                    new_map = {k:i for i,k in enumerate(class_map.keys())}
                                    class_map.clear()
                                    class_map.update(new_map)

                                    new_boxes = []
                                    for box in boxes:
                                        x, y, w, h, c = box[:5]
                                        mask = box[5] if len(box) == 6 else None
                                        if c == cid:
                                            continue
                                        elif c > cid:
                                            new_boxes.append((x, y, w, h, c-1, mask))
                                        else:
                                            new_boxes.append((x, y, w, h, c, mask))

                                    boxes[:] = new_boxes

                                    class_map_path.write_text(json.dumps(class_map, indent=2))
                                    write_data_yaml(dataset_dir, class_map)
                                    active_class_id = 0
                                    selected_idx = None
                                    
                                confirm_delete = None
                                break
                        continue
                    
                    if class_menu:
                        for r, act in menu_actions:
                            if r.collidepoint(mx, my) and act == "delete":
                                confirm_delete = {"cid": class_menu["cid"]}
                                class_menu = None
                                drawing = False       
                                current_box = None
                                break
                        continue
                    
                    selected_idx = None
                    resizing = False
                    resize_corner = None

                    for i, box in enumerate(boxes):
                        x, y, w, h, _ = box[:5] 
                        if x <= mx <= x + w and y <= my <= y + h:
                            selected_idx = i
                            corner = detect_corner(mx, my, x, y, w, h)
                            if corner:
                                push_undo()
                                resizing = True
                                drawing = False
                                resize_corner = corner
                                resize_start = (mx, my)
                            break

                        #ถ้าไม่โดน box → เริ่มวาดใหม่
                    if selected_idx is None:
                        drawing = True
                        start_pos = event.pos
                        current_box = None


                # คลิกขวา (เปิดเมนู class)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    mx, my = event.pos
                    class_menu = None

                    for rect, cid in class_clicks:
                        if rect.collidepoint(mx, my):
                            class_menu = {"cid": cid, "pos": (mx, my)}
                            break    

                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if drawing:
                        drawing = False
                    if resizing:
                        resizing = False
                        resize_corner = None

                if event.type == pygame.MOUSEMOTION and drawing:
                    x1, y1 = start_pos
                    x2, y2 = event.pos
                    current_box = (min(x1,x2), min(y1,y2), abs(x2-x1), abs(y2-y1))

                if event.type == pygame.MOUSEMOTION and resizing and selected_idx is not None:
                    x, y, w, h, c = boxes[selected_idx][:5]
                    mx, my = event.pos
                    sx, sy = resize_start
                    dx = mx - sx
                    dy = my - sy
    
                    if resize_corner == "br":
                        w = max(5, w + dx)
                        h = max(5, h + dy)

                    elif resize_corner == "tr":
                        y += dy
                        h = max(5, h - dy)
                        w = max(5, w + dx)

                    elif resize_corner == "bl":
                        x += dx
                        w = max(5, w - dx)
                        h = max(5, h + dy)

                    elif resize_corner == "tl":
                        x += dx
                        y += dy
                        w = max(5, w - dx)
                        h = max(5, h - dy)

                    w = max(5, w)
                    h = max(5, h)
                    old = boxes[selected_idx]
                    ox, oy, ow, oh, c, mask = old

                    new_mask = None
                    if mask:
                        sx = w / ow
                        sy = h / oh
                        new_mask = [
                            (
                                x + (px - ox) * sx,
                                y + (py - oy) * sy
                            )
                            for px, py in mask
                        ]

                    boxes[selected_idx] = (x, y, w, h, c, new_mask)

                    resize_start = (mx, my)

            screen.fill(BG_COLOR)
            screen.blit(image_disp, (0, 0))

            for i, box in enumerate(boxes):
                if len(box) == 5:
                    x, y, w, h, cid = box
                    mask = None          
                else:
                    x, y, w, h, cid, mask = box

                color = (255, 255, 0) if i == selected_idx else get_class_color(cid)
                pygame.draw.rect(screen, color, (x, y, w, h), BOX_THICKNESS)

                # =========================
                # DRAW SAVED POLYGON
                # =========================
                if i == selected_idx and mask and len(mask) >= 3:
                    pygame.draw.polygon(
                        screen,
                        get_class_color(cid),
                        mask,
                        2
                    )
                # วาด resize handle (4 มุม)
                # ===============================ห
                if i == selected_idx:
                    for px, py in [
                        (x, y),               # TL
                        (x + w, y),           # TR
                        (x, y + h),           # BL
                        (x + w, y + h),       # BR
                    ]:
                        pygame.draw.rect(
                            screen,
                            (255, 255, 255),
                            (
                                px - HANDLE_SIZE // 2,
                                py - HANDLE_SIZE // 2,
                                HANDLE_SIZE,
                                HANDLE_SIZE,
                            )
                        )
            if current_box:
                pygame.draw.rect(screen, (255,255,0), current_box, 1)

            info = font.render(f"{idx+1}/{len(image_paths)} | Boxes:{len(boxes)} | Typing:{label_text}", True, FONT_COLOR)
            screen.blit(info, (10, IMG_HEIGHT - 28))

            class_clicks = draw_class_list(screen, font, class_map, active_class_id)
            menu_actions = draw_class_menu(screen, font, class_menu)
            confirm_actions = draw_confirm_popup(screen, font, confirm_delete)
            draw_tooltip(screen, font, show_help)

            # =========================
            # DRAW CURRENT POLYGON (preview)
            # =========================
            if polygon_mode and len(current_polygon) >= 2:
                pygame.draw.lines(
                    screen,
                    (0, 255, 255),
                    False,
                    current_polygon,
                    2
                )

            pygame.display.flip()
            clock.tick(60)

        with open(label_file, "w") as f:
            for box in boxes:
                x, y, w, h, cid = box[:5]
                mask = box[5] if len(box) == 6 else None
                # ===== SEGMENTATION (YOLOv8) =====
                if mask and len(mask) >= 3:
                    seg = []
                    for px, py in mask:
                        seg.append(
                            f"{px / disp_size[0]:.6f} {py / disp_size[1]:.6f}"
                        )

                    f.write(
                        f"{cid} " + " ".join(seg) + "\n"
                    )

                # ===== BBOX (fallback) =====
                else:
                    xc = (x + w / 2) / disp_size[0]
                    yc = (y + h / 2) / disp_size[1]

                    f.write(
                        f"{cid} {xc:.6f} {yc:.6f} "
                        f"{w/disp_size[0]:.6f} {h/disp_size[1]:.6f}\n"
                    )


    return "Done"

main_callable = annotate_images_pygame
