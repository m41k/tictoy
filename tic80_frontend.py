import pygame
import os
import sys
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from PIL import Image

pygame.init()
pygame.joystick.init()

# ================= CONFIG =================
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TIC-80 Frontend")
clock = pygame.time.Clock()

BASE_URL = "https://tic80.com"
PLAY_URL = "https://tic80.com/play"

CACHE_FILE = "games.json"
COVERS_DIR = "covers"
os.makedirs(COVERS_DIR, exist_ok=True)

# ================= JOYSTICK =================
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
else:
    joystick = None

# ================= SCRAPER =================
def fetch_games():
    print("Baixando lista online...")
    response = requests.get(PLAY_URL)
    soup = BeautifulSoup(response.text, "html.parser")

    games = []

    for cart in soup.find_all("div", class_="cart"):
        title = cart.find("h2")
        image = cart.find("img", class_="pixelated")
        text_blocks = cart.find_all("div", class_="text-muted")

        if not title or not image:
            continue

        title_text = title.text.strip()
        description = text_blocks[0].text.strip() if len(text_blocks) > 0 else ""
        author = text_blocks[1].text.strip() if len(text_blocks) > 1 else ""

        image_url = urljoin(BASE_URL, image["src"])
        filename = title_text.replace(" ", "_").replace("/", "") + ".gif"
        filepath = os.path.join(COVERS_DIR, filename)

        # Baixar imagem se não existir
        if not os.path.exists(filepath):
            img_data = requests.get(image_url).content
            with open(filepath, "wb") as f:
                f.write(img_data)

        games.append({
            "title": title_text,
            "description": description,
            "author": author,
            "cover": filepath
        })

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(games, f, indent=4, ensure_ascii=False)

    return games

def load_games():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return fetch_games()

# ================= GIF LOADER =================
def load_gif_frames(path):
    frames = []
    durations = []
    img = Image.open(path)

    try:
        while True:
            frame = img.convert("RGBA")
            data = frame.tobytes()
            py_img = pygame.image.fromstring(data, frame.size, "RGBA")
            frames.append(py_img)
            durations.append(img.info.get("duration", 100))
            img.seek(img.tell() + 1)
    except EOFError:
        pass

    return frames, durations

# ================= ESTADOS =================
state = "menu"
menu_options = ["Atualizar Lista", "Galeria Online", "Sair"]
menu_selected = 0

games = load_games()
selected = 0
frames, durations = ([], [])
frame_index = 0
frame_timer = 0

if games:
    frames, durations = load_gif_frames(games[0]["cover"])

# ================= FONTES =================
title_font = pygame.font.SysFont("monospace", 60)
menu_font = pygame.font.SysFont("monospace", 32)
small_font = pygame.font.SysFont("monospace", 24)

# ================= LOOP =================
running = True

while running:
    dt = clock.tick(60)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if state == "menu":

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    menu_selected = (menu_selected + 1) % len(menu_options)

                if event.key == pygame.K_UP:
                    menu_selected = (menu_selected - 1) % len(menu_options)

                if event.key == pygame.K_RETURN:
                    if menu_options[menu_selected] == "Atualizar Lista":
                        games = fetch_games()
                        selected = 0
                        frames, durations = load_gif_frames(games[0]["cover"])

                    elif menu_options[menu_selected] == "Galeria Online":
                        state = "viewer"

                    elif menu_options[menu_selected] == "Sair":
                        running = False

        elif state == "viewer":

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(games)
                    frames, durations = load_gif_frames(games[selected]["cover"])
                    frame_index = 0

                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(games)
                    frames, durations = load_gif_frames(games[selected]["cover"])
                    frame_index = 0

                if event.key == pygame.K_ESCAPE:
                    state = "menu"

    # ================= RENDER =================
    screen.fill((20, 20, 30))

    if state == "menu":

        title = title_font.render("TIC-80 ONLINE", True, (0, 255, 150))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))

        y = 250
        for i, option in enumerate(menu_options):
            color = (255,255,255)
            if i == menu_selected:
                color = (0,255,0)

            text = menu_font.render(option, True, color)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, y))
            y += 50

    elif state == "viewer":

        if games:
            game = games[selected]

            # Info
            title = menu_font.render(game["title"], True, (255,255,255))
            desc = small_font.render(game["description"], True, (200,200,200))
            author = small_font.render(game["author"], True, (150,150,150))

            screen.blit(title, (50, 40))
            screen.blit(desc, (50, 80))
            screen.blit(author, (50, 110))

            # GIF
            if frames:
                frame_timer += dt
                if frame_timer > durations[frame_index]:
                    frame_timer = 0
                    frame_index = (frame_index + 1) % len(frames)

                img = pygame.transform.scale(frames[frame_index], (500, 380))
                screen.blit(img, (WIDTH - 600, 150))

    pygame.display.flip()

pygame.quit()
sys.exit()
