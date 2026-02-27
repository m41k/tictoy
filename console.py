import pygame
import os
import sys
from PIL import Image

pygame.init()
pygame.joystick.init()

# ------------------ CONFIG TELA ------------------
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Mini Console")

clock = pygame.time.Clock()

# ------------------ JOYSTICK ------------------
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print("Controle detectado:", joystick.get_name())
else:
    joystick = None
    print("Nenhum controle detectado")

# ------------------ ESTADOS ------------------
state = "menu"

# ------------------ MENU PRINCIPAL ------------------
menu_options = ["Galeria", "Configurações", "Sobre", "Sair"]
menu_selected = 0

# ------------------ GALERIA ------------------
files = sorted([
    f for f in os.listdir('.')
    if f.lower().endswith('.gif')
])

selected = 0
frames = []
durations = []
frame_index = 0
frame_timer = 0

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

if files:
    frames, durations = load_gif_frames(files[selected])

# ------------------ FONTES ------------------
title_font = pygame.font.SysFont("monospace", 80)
menu_font = pygame.font.SysFont("monospace", 40)
small_font = pygame.font.SysFont("monospace", 28)

# ------------------ LOOP PRINCIPAL ------------------
running = True

while running:
    dt = clock.tick(60)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # ================= MENU =================
        if state == "menu":

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    menu_selected = (menu_selected + 1) % len(menu_options)

                if event.key == pygame.K_UP:
                    menu_selected = (menu_selected - 1) % len(menu_options)

                if event.key == pygame.K_RETURN:
                    if menu_options[menu_selected] == "Galeria":
                        state = "viewer"
                    elif menu_options[menu_selected] == "Sair":
                        running = False

            if event.type == pygame.JOYHATMOTION:
                if event.value == (0, -1):
                    menu_selected = (menu_selected + 1) % len(menu_options)
                if event.value == (0, 1):
                    menu_selected = (menu_selected - 1) % len(menu_options)

            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:  # Botão A
                    if menu_options[menu_selected] == "Galeria":
                        state = "viewer"
                    elif menu_options[menu_selected] == "Sair":
                        running = False

        # ================= GALERIA =================
        elif state == "viewer":

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(files)
                    frames, durations = load_gif_frames(files[selected])
                    frame_index = 0

                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(files)
                    frames, durations = load_gif_frames(files[selected])
                    frame_index = 0

                if event.key == pygame.K_ESCAPE:
                    state = "menu"

            if event.type == pygame.JOYHATMOTION:
                if event.value == (0, -1):
                    selected = (selected + 1) % len(files)
                    frames, durations = load_gif_frames(files[selected])
                    frame_index = 0

                if event.value == (0, 1):
                    selected = (selected - 1) % len(files)
                    frames, durations = load_gif_frames(files[selected])
                    frame_index = 0

            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 1:  # Botão B
                    state = "menu"

    # ================= RENDER =================

    screen.fill((15, 15, 30))

    if state == "menu":

        # LOGO
        title = title_font.render("MEU CONSOLE", True, (0, 255, 150))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))

        # OPÇÕES
        y = 300
        for i, option in enumerate(menu_options):
            color = (255, 255, 255)
            if i == menu_selected:
                color = (0, 255, 0)

            text = menu_font.render(option, True, color)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, y))
            y += 60

        # PROPAGANDA
        sponsor = small_font.render("Apoiador: Seu Nome Aqui", True, (200, 200, 50))
        screen.blit(sponsor, (WIDTH//2 - sponsor.get_width()//2, HEIGHT - 100))

    elif state == "viewer":

        menu_width = WIDTH // 3

        # LISTA LATERAL
        y = 40
        for i, f in enumerate(files):
            color = (255,255,255)
            if i == selected:
                color = (0,255,0)

            text = small_font.render(f, True, color)
            screen.blit(text, (20, y))
            y += 35

        # ANIMAÇÃO
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

pygame.quit()
sys.exit()
