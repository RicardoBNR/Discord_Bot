import discord
import requests
from bs4 import BeautifulSoup
import os
from flask import Flask
from threading import Thread

# Inicializar Flask
app = Flask(__name__)


@app.route('/')
def home():
    return 'Bot Activo'


# Inicializar el bot de Discord
TOKEN = os.getenv(
    "DISCORD_TOKEN")  # Token del bot (guardado en Secrets en Replit)

intents = discord.Intents(messages=True)
intents.message_content = True
bot = discord.Client(intents=intents)


@bot.event
async def on_ready():
    print(f'Bot connected as {bot.user}')


@bot.event
async def on_message(message):

    if bot.user in message.mentions:
        await message.channel.send(
            f"Hi! you have to use !search __**Keyword**__ or !find __**Keyword**__  in order to use me :)"
        )

    print(f'Message from {message.author}: {message.content}')
    if message.author == bot.user:
        return

    size = 0

    check = message.content.startswith(
        "!search") or message.content.startswith("!find")

    if message.content.startswith("!search"):
        size = len("!search ")
    if message.content.startswith("!find"):
        size = len("!find ")

    if check:

        key_word = message.content[size:].strip()
        key_word = str(key_word).replace(" ", "+")
        results = find_recomendations(key_word)

        url = f"https://janto.shop/search?q={key_word}"

        if results == []:
            await message.channel.send(
                f"Hi! {message.author.mention} couldn't find any items related :c"
            )
        else:
            await message.channel.send(
                f"Hi! {message.author.mention}, i found this results!")
            for resultado in results:
                await message.channel.send(resultado)
                await message.channel.send(
                    "===================================================================================================================================="
                )
            await message.channel.send(
                f"__**If you want to see more options, check this link!**__ {url}"
            )


def find_recomendations(key_word):
    url = f"https://janto.shop/search?q={key_word}"

    print(url)
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return ["Can't reach page"]
    soup = BeautifulSoup(response.text, "html.parser")

    productos = []

    items = soup.find_all('div', class_="collection-item")

    if not items:
        return []

    else:

        for item in items[:3]:

            link = item.select_one("a")["href"]
            price = item.find("h3", class_="product-reg-price").text
            store_link = "https://janto.shop" + link

            response = requests.get(store_link, headers=headers)
            nsoup = BeautifulSoup(response.text, "html.parser")
            title = nsoup.find("h1", class_="product-title").text

            #print(f"Item: {titulo} - Price: {price} - Link to the item, {store_link}")
            productos.append(
                f"__**Item:**__ {title}\n__**Price:**__ {price}\n__**Store link:**__ {store_link}\n"
            )

        return productos


# Función para ejecutar el servidor Flask en un hilo
def run():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))


# Iniciar Flask en un hilo para mantenerlo activo
Thread(target=run).start()

# Ejecutar el bot
bot.run(TOKEN)