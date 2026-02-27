import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://tic80.com"
URL = "https://tic80.com/play"

response = requests.get(URL)
soup = BeautifulSoup(response.text, "html.parser")

games = []

for cart in soup.find_all("div", class_="cart"):

    title = cart.find("h2")
    image = cart.find("img", class_="pixelated")
    text_blocks = cart.find_all("div", class_="text-muted")

    if title and image:

        title_text = title.text.strip()

        description = ""
        author = ""

        if len(text_blocks) > 0:
            description = text_blocks[0].text.strip()

        if len(text_blocks) > 1:
            author = text_blocks[1].text.strip()

        image_url = urljoin(BASE_URL, image["src"])

        games.append({
            "title": title_text,
            "description": description,
            "author": author,
            "image": image_url
        })

for g in games[:5]:
    print("Título:", g["title"])
    print("Descrição:", g["description"])
    print("Autor:", g["author"])
    print("Imagem:", g["image"])
    print("-" * 40)
