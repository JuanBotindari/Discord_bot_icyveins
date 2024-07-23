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

import os
import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
import re

# Clase para extraer las listas de tier
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

# Diccionario de agrupamiento basado en el texto en paréntesis
grouping_conditions = {
    'OP': 'S - OP',
    'Best': 'A - Best-Candidates',
    'Best-Candidates': 'A - Best-Candidates',
    'Impressive': 'B - Impressive',
    'Good Choice': 'C - Good Choice',
    'Good': 'D - Good Choice',
    'Decent': 'E - Decent',
    'Underperforming': 'F - Underperforming'
}

def format_as_table(command_name, tier_list):
    # Crear un diccionario para agrupar las especializaciones
    groups = {}
    
    for item in tier_list:
        # Extraer el texto entre paréntesis
        match = re.search(r'\((.*?)\)', item)
        if match:
            group_text = match.group(1)
            spec = item[:match.start()].strip()
            
            # Determinar el grupo usando el diccionario de condiciones
            group = 'Other'
            for key in grouping_conditions:
                if key in group_text:
                    group = grouping_conditions[key]
                    break
            
            # Añadir la especialización al grupo correspondiente
            if group not in groups:
                groups[group] = []
            groups[group].append(spec)

    # Construir la respuesta
    response = f"Lista de {command_name.capitalize()}s:\n"
    response += "```\n"  # Abre una sección de código en Discord

    for group, specs in groups.items():
        response += f"{group}:\n"
        for i, spec in enumerate(specs):
            response += f"  {i + 1}. {spec}\n"
        response += "\n"

    response += "```"  # Cierra la sección de código en Discord
    return response

# URLs y títulos de las listas de cada tipo
extractors_info = {
    'healer': {
        'url': 'https://www.icy-veins.com/wow/mythic-beta-healer-tier-list',
        'title': 'Healer Tier List for Season 1 of Mythic+ in The War Within'
    },
    'tank': {
        'url': 'https://www.icy-veins.com/wow/mythic-beta-tank-tier-list',
        'title': 'Tank Tier List for Season 1 of Mythic+ in The War Within'
    },
    'dps': {
        'url': 'https://www.icy-veins.com/wow/mythic-beta-dps-tier-list',
        'title': 'DPS Tier List for Season 1 of Mythic+ in The War Within'
    }
}

# Crear instancias de la clase para cada tipo de lista
extractors = {key: TierListExtractor(value['url'], value['title']) for key, value in extractors_info.items()}

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
        await ctx.send("Comando no encontrado. Usa `/tier help` para ver la lista de comandos disponibles.")
    else:
        raise error

# Comando principal /tier
@bot.group(invoke_without_command=True)
async def tier(ctx):
    await ctx.send("Usa `/tier help` para ver la lista de comandos disponibles.")

@tier.command(name='healer')
async def tier_healer(ctx):
    await tier_list(ctx, 'healer')

@tier.command(name='tank')
async def tier_tank(ctx):
    await tier_list(ctx, 'tank')

@tier.command(name='dps')
async def tier_dps(ctx):
    await tier_list(ctx, 'dps')

@tier.command(name='help')
async def tier_help(ctx):
    help_text = (
        "Comandos disponibles:\n"
        "/tier healer - Muestra la lista de Healers\n"
        "/tier tank - Muestra la lista de Tanks\n"
        "/tier dps - Muestra la lista de DPS\n"
        "/tier help - Muestra este mensaje de ayuda\n"
    )
    await ctx.send(help_text)

async def tier_list(ctx, tipo):
    command_name = tipo.lower()  # Convertir el tipo a minúsculas
    print(f'Comando /tier {command_name} recibido')

    extractor = extractors.get(command_name)
    if not extractor:
        await ctx.send(f"No se encontró extractor para el comando {command_name}.")
        return

    tier_list = extractor.extract_list()
    if tier_list:
        response = format_as_table(command_name, tier_list)
    else:
        response = f"No se encontró la lista de {command_name.capitalize()}s en la página."

    await ctx.send(response)

# Iniciar el bot
bot.run(os.getenv('DISCORD_TOKEN'))




