import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup

'''
Ahi lo encontre, esta en
- body
- div id= main
- div id = content
- div id = center
- div class = page_content_container text_color ...
- div class = page_content

Luego, los elementos:
-div class = heading_container heading number_2
- ol 

'''


class TierListExtractor:
    def __init__(self, url, section_title):
        self.url = url
        self.section_title = section_title

    def fetch_html(self):
        print(f'Fetching HTML for {self.section_title} from {self.url}')
        response = requests.get(self.url)
        response.raise_for_status()
        return response.text

    def extract_list(self):
        print(f'Extracting list for {self.section_title}')
        html = self.fetch_html()
        soup = BeautifulSoup(html, 'html.parser')

        # Encontrar el apartado con el título específico
        header = soup.find('h2', text=self.section_title)
        if not header:
            print(f'Header {self.section_title} not found')
            return None

        # Encontrar la lista numerada que sigue al título
        list_items = header.find_next('ol').find_all('li')

        tier_list = [item.get_text(strip=True) for item in list_items]
        return tier_list

# URL de las páginas
healer_url = 'https://www.icy-veins.com/wow/mythic-beta-healer-tier-list'
tank_url = 'https://www.icy-veins.com/wow/mythic-beta-tank-tier-list'
dps_url = 'https://www.icy-veins.com/wow/mythic-beta-dps-tier-list'

# Títulos de las secciones
healer_title = 'Healer Tier List for Season 1 of Mythic+ in The War Within'
tank_title = 'Tank Tier List for Season 1 of Mythic+ in The War Within'
dps_title = 'DPS Tier List for Season 1 of Mythic+ in The War Within'

# Crear instancias de la clase para cada tipo de lista
healer_extractor = TierListExtractor(healer_url, healer_title)
tank_extractor = TierListExtractor(tank_url, tank_title)
dps_extractor = TierListExtractor(dps_url, dps_title)

# Crear el bot de Discord con intents adicionales
intents = discord.Intents.default()
intents.message_content = True  # Asegúrate de tener habilitada la intención para contenido de mensajes
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Comando no encontrado.")
    else:
        raise error

@bot.command(name='healer')
async def healer(ctx):
    print('Comando /healer recibido')
    healer_list = healer_extractor.extract_list()
    if healer_list:
        response = "Lista de Healers:\n" + "\n".join(healer_list)
    else:
        response = "No se encontró la lista de Healers en la página."
    await ctx.send(response)

@bot.command(name='tank')
async def tank(ctx):
    print('Comando /tank recibido')
    tank_list = tank_extractor.extract_list()
    if tank_list:
        response = "Lista de Tanks:\n" + "\n".join(tank_list)
    else:
        response = "No se encontró la lista de Tanks en la página."
    await ctx.send(response)

@bot.command(name='dps')
async def dps(ctx):
    print('Comando /dps recibido')
    dps_list = dps_extractor.extract_list()
    if dps_list:
        response = "Lista de DPS:\n" + "\n".join(dps_list)
    else:
        response = "No se encontró la lista de DPS en la página."
    await ctx.send(response)



# Iniciar el bot
bot.run('MTI2NDk1MzgxNDg2NDEwNTU5Mg.GTPudj.QKB4N_anZR7hxpy5eB34l7lY1RprxK-4NogkV4')




