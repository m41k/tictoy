import pygame
import os
import sys

pygame.init()

# Pega resolução da tela
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Mini Frontend")

font = pygame.font.SysFont("monospace", 28)

# Lista gifs do diretório
files = sorted([f for f in os.listdir('.') if f.endswith('.gif')])
selected = 0

def load_image(name):
    try:
        return pygame.image.load(name)
    except:
        return None

image = load_image(files[selected]) if files else None

running = True
clock = pygame.time.Clock()

while running:
    screen.fill((20, 20, 20))

    # --- MENU LATERAL ---
    menu_width = WIDTH // 3
    y = 40
    for i, f in enumerate(files):
        color = (255,255,255)
        if i == selected:
            color = (0,255,0)
        text = font.render(f, True, color)
        screen.blit(text, (20, y))
        y += 35

    # --- PREVIEW ---
    if image:
        img = pygame.transform.scale(image, (WIDTH - menu_width - 40, HEIGHT - 80))
        screen.blit(img, (menu_width + 20, 40))

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                selected = (selected + 1) % len(files)
                image = load_image(files[selected])

            if event.key == pygame.K_UP:
                selected = (selected - 1) % len(files)
                image = load_image(files[selected])

            if event.key == pygame.K_q:
                running = False

    clock.tick(30)

pygame.quit()
sys.exit()
