import pygame
import os
import sys
from PIL import Image

pygame.init()
pygame.joystick.init()

# ----- TELA -----
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Mini Frontend")

font = pygame.font.SysFont("monospace", 28)

# ----- JOYSTICK -----
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print("Controle detectado:", joystick.get_name())
else:
    joystick = None
    print("Nenhum controle detectado")

# ----- ARQUIVOS -----
files = sorted([
    f for f in os.listdir('.')
    if f.lower().endswith('.gif')
])

selected = 0

# ----- CARREGAR GIF -----
def load_gif_frames(filename):
    frames = []
    durations = []

    img = Image.open(filename)

    try:
        while True:
            frame = img.convert("RGBA")
            mode = frame.mode
            size = frame.size
            data = frame.tobytes()

            py_image = pygame.image.fromstring(data, size, mode)
            frames.append(py_image)

            durations.append(img.info.get("duration", 100))
            img.seek(img.tell() + 1)
    except EOFError:
        pass

    return frames, durations

frames, durations = load_gif_frames(files[selected]) if files else ([], [])
frame_index = 0
frame_timer = 0

clock = pygame.time.Clock()
running = True

# ----- LOOP PRINCIPAL -----
while running:
    dt = clock.tick(60)
    screen.fill((20, 20, 20))

    menu_width = WIDTH // 3

    # ----- MENU -----
    y = 40
    for i, f in enumerate(files):
        color = (255, 255, 255)
        if i == selected:
            color = (0, 255, 0)
        text = font.render(f, True, color)
        screen.blit(text, (20, y))
        y += 35

    # ----- ANIMAÇÃO GIF -----
    if frames:
        frame_timer += dt
        if frame_timer > durations[frame_index]:
            frame_timer = 0
            frame_index = (frame_index + 1) % len(frames)

        img = pygame.transform.scale(
            frames[frame_index],
            (WIDTH - menu_width - 40, HEIGHT - 80)
        )
        screen.blit(img, (menu_width + 20, 40))

    pygame.display.flip()

    for event in pygame.event.get():

        # ----- TECLADO -----
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                selected = (selected + 1) % len(files)
                frames, durations = load_gif_frames(files[selected])
                frame_index = 0

            if event.key == pygame.K_UP:
                selected = (selected - 1) % len(files)
                frames, durations = load_gif_frames(files[selected])
                frame_index = 0

            if event.key == pygame.K_q:
                running = False

        # ----- CONTROLE: BOTÃO -----
        if event.type == pygame.JOYBUTTONDOWN:
            print("Botão:", event.button)

            # Botão A (geralmente 0)
            if event.button == 0:
                print("A pressionado")

            # Botão B (geralmente 1) → sair
            if event.button == 1:
                running = False

        # ----- CONTROLE: D-PAD -----
        if event.type == pygame.JOYHATMOTION:
            if event.value == (0, -1):  # baixo
                selected = (selected + 1) % len(files)
                frames, durations = load_gif_frames(files[selected])
                frame_index = 0

            if event.value == (0, 1):  # cima
                selected = (selected - 1) % len(files)
                frames, durations = load_gif_frames(files[selected])
                frame_index = 0

        # ----- CONTROLE: ANALÓGICO -----
        if event.type == pygame.JOYAXISMOTION:
            if event.axis == 1:  # eixo vertical
                if event.value > 0.7:
                    selected = (selected + 1) % len(files)
                    frames, durations = load_gif_frames(files[selected])
                    frame_index = 0
                    pygame.time.wait(200)

                elif event.value < -0.7:
                    selected = (selected - 1) % len(files)
                    frames, durations = load_gif_frames(files[selected])
                    frame_index = 0
                    pygame.time.wait(200)

pygame.quit()
sys.exit()
