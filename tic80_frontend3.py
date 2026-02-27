import pygame
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import os
import subprocess
import sys

# ================= CONFIG =================

BASE_URL = "https://tic80.com"
PLAY_URL = "https://tic80.com/play"
CACHE_FILE = "games.json"

WIDTH, HEIGHT = 1000, 650

# ================= SCRAPER =================

def fetch_games():
    print("Baixando lista online...")

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(PLAY_URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    games = []

    for cart in soup.find_all("div", class_="cart"):

        title = cart.find("h2")
        link_tag = cart.find("a")
        text_blocks = cart.find_all("div", class_="text-muted")

        if not title or not link_tag:
            continue

        games.append({
            "title": title.text.strip(),
            "description": text_blocks[0].text.strip() if len(text_blocks) > 0 else "",
            "author": text_blocks[1].text.strip() if len(text_blocks) > 1 else "",
            "page": urljoin(BASE_URL, link_tag["href"])
        })

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(games, f, indent=4, ensure_ascii=False)

    print(f"{len(games)} jogos encontrados.")
    return games


def load_games():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return fetch_games()


# ================= PEGAR URL DO .tic =================

def get_tic_download_url(cart_page_url):

    headers = {"User-Agent": "Mozilla/5.0"}

    print("Abrindo página:", cart_page_url)

    response = requests.get(cart_page_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.endswith(".tic"):
            full_url = urljoin(BASE_URL, href)
            print("URL encontrada:", full_url)
            return full_url

    print("Nenhum .tic encontrado.")
    return None


# ================= EXECUTAR TIC80 =================

def run_tic80_from_url(tic_url):
    print("Executando:", tic_url)

    pygame.quit()

    # Se não estiver no PATH, troque "tic80" pelo caminho completo
    subprocess.run(["tic80", tic_url])

    pygame.init()


# ================= INTERFACE =================

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TIC-80 Online Launcher")
clock = pygame.time.Clock()

font_title = pygame.font.SysFont("monospace", 28)
font_small = pygame.font.SysFont("monospace", 20)
font_info = pygame.font.SysFont("monospace", 16)

games = load_games()
selected = 0

running = True

while running:
    clock.tick(60)
    screen.fill((20, 20, 30))

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

                tic_url = get_tic_download_url(game["page"])

                if tic_url:
                    run_tic80_from_url(tic_url)

            if event.key == pygame.K_ESCAPE:
                running = False

    # ================= RENDER =================

    y = 40

    title = font_title.render("TIC-80 ONLINE LAUNCHER", True, (0, 255, 150))
    screen.blit(title, (40, 10))

    for i, game in enumerate(games):

        color = (200, 200, 200)
        if i == selected:
            color = (0, 255, 150)

        text = font_title.render(game["title"], True, color)
        screen.blit(text, (40, y))

        y += 35

        if i == selected:
            desc = font_small.render(game["description"], True, (180, 180, 180))
            author = font_small.render(game["author"], True, (120, 120, 120))

            screen.blit(desc, (60, y))
            y += 25
            screen.blit(author, (60, y))
            y += 25

        y += 10

    info = font_info.render("UP/DOWN: navegar  |  ENTER: rodar  |  R: atualizar  |  ESC: sair", True, (120, 120, 120))
    screen.blit(info, (40, HEIGHT - 30))

    pygame.display.flip()

pygame.quit()
sys.exit()
