import pygame
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import json
import subprocess
import sys

# ================= CONFIG =================

BASE_URL = "https://tic80.com"
PLAY_URL = "https://tic80.com/play"

CACHE_FILE = "games.json"
ROMS_DIR = "roms"

os.makedirs(ROMS_DIR, exist_ok=True)

WIDTH, HEIGHT = 1000, 600

# ================= SCRAPER =================

def fetch_games():
    print("Baixando lista online...")
    response = requests.get(PLAY_URL)
    soup = BeautifulSoup(response.text, "html.parser")

    games = []

    for cart in soup.find_all("div", class_="cart"):

        title = cart.find("h2")
        link_tag = cart.find("a")
        text_blocks = cart.find_all("div", class_="text-muted")

        if not title or not link_tag:
            continue

        title_text = title.text.strip()
        page_url = urljoin(BASE_URL, link_tag["href"])

        description = text_blocks[0].text.strip() if len(text_blocks) > 0 else ""
        author = text_blocks[1].text.strip() if len(text_blocks) > 1 else ""

        games.append({
            "title": title_text,
            "description": description,
            "author": author,
            "page": page_url
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


# ================= DOWNLOAD .tic =================

def download_cart_from_page(cart_page_url, title):

    print("Acessando página:", cart_page_url)

    response = requests.get(cart_page_url)
    soup = BeautifulSoup(response.text, "html.parser")

    download_link = None

    for a in soup.find_all("a", href=True):
        if a["href"].endswith(".tic"):
            download_link = urljoin(BASE_URL, a["href"])
            break

    if not download_link:
        print("Arquivo .tic não encontrado.")
        return None

    print("Baixando:", download_link)

    filename = title.replace(" ", "_").replace("/", "") + ".tic"
    filepath = os.path.join(ROMS_DIR, filename)

    if not os.path.exists(filepath):
        cart_data = requests.get(download_link).content
        with open(filepath, "wb") as f:
            f.write(cart_data)

    return filepath


# ================= EXECUTAR TIC80 =================

def run_tic80(cart_path):
    print("Executando:", cart_path)
    pygame.quit()
    subprocess.run(["tic80", cart_path])
    pygame.init()


# ================= INTERFACE =================

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TIC-80 Launcher")
clock = pygame.time.Clock()

font_title = pygame.font.SysFont("monospace", 28)
font_small = pygame.font.SysFont("monospace", 20)

games = load_games()
selected = 0

running = True

while running:
    clock.tick(60)
    screen.fill((25, 25, 35))

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_DOWN:
                selected = (selected + 1) % len(games)

            if event.key == pygame.K_UP:
                selected = (selected - 1) % len(games)

            if event.key == pygame.K_r:
                games = fetch_games()
                selected = 0

            if event.key == pygame.K_RETURN:
                game = games[selected]
		if "page" in game:
		    cart_path = download_cart_from_page(
		        game["page"],
		        game["title"]
		    )
		else:
		    print("Página do jogo não encontrada no JSON.")
		    cart_path = None
                if cart_path:
                    run_tic80(cart_path)

            if event.key == pygame.K_ESCAPE:
                running = False

    # ================= RENDER LISTA =================

    y = 40
    for i, game in enumerate(games):

        color = (200, 200, 200)
        if i == selected:
            color = (0, 255, 150)

        text = font_title.render(game["title"], True, color)
        screen.blit(text, (40, y))

        y += 35

        if i == selected:
            desc = font_small.render(game["description"], True, (180,180,180))
            author = font_small.render(game["author"], True, (120,120,120))

            screen.blit(desc, (60, y))
            y += 25
            screen.blit(author, (60, y))
            y += 25

        y += 10

    pygame.display.flip()

pygame.quit()
sys.exit()
