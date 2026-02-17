from pathlib import Path
import pygame

pygame.init()

def view_images_popup(
    image_paths: {
        'type': object,   # รับ list จาก node ก่อนหน้า
    },
):
    # --------------------------------
    # normalize input (Nodezator อาจส่ง list ซ้อน)
    # --------------------------------
    if isinstance(image_paths, (list, tuple)) and image_paths:
        if isinstance(image_paths[0], (list, tuple)):
            image_paths = image_paths[0]

    if not image_paths:
        return None

    # --------------------------------
    # load images
    # --------------------------------
    images = []
    for p in image_paths:
        try:
            images.append(pygame.image.load(str(p)).convert_alpha())
        except Exception:
            pass

    if not images:
        return None

    # --------------------------------
    # open popup window
    # --------------------------------
    screen = pygame.display.set_mode((900, 700))
    pygame.display.set_caption("Image Viewer (ESC to close)")

    clock = pygame.time.Clock()
    index = 0
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    index += 1
                elif event.key == pygame.K_LEFT:
                    index -= 1
                elif event.key == pygame.K_ESCAPE:
                    return "Exited"  # ออกแค่ pop-up

                index = max(0, min(index, len(images) - 1))

        screen.fill((20, 20, 20))

        img = images[index]
        target = img.get_rect().fit(screen.get_rect())
        scaled = pygame.transform.smoothscale(img, target.size)
        rect = scaled.get_rect(center=screen.get_rect().center)
        screen.blit(scaled, rect)

        pygame.display.flip()
        clock.tick(60)

    # ปิดแค่หน้าต่าง ไม่ปิด pygame ทั้งระบบ
    pygame.display.quit()

    return None


main_callable = view_images_popup
