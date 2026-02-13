python
import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import asyncio

# ---------- CONFIG ----------
TOKEN = "ТВІЙ_ТОКЕН_ТУТ"  # Сюди встав свій токен від Discord Developer Portal

CONFIG_FILE = "config.json"
DELETE_FINISHED_AFTER = 1800  # 30 хвилин (в секундах)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"event_channel_id": None, "log_channel_id": None, "role_id": None}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

config = load_config()

# ---------- BOT SETUP ----------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

async def log(message: str):
    """Функція для відправки логів у спеціальний канал"""
    channel_id = config.get("log_channel_id")
    if channel_id:
        channel = bot.get_channel(channel_id)
        if not channel:
            try:
                channel = await bot.fetch_channel(channel_id)
            except:
                return
        await channel.send(message)

# ---------- UI ----------
class event_button(discord.ui.View):
    def __init__(self, url):
        super().__init__()
        super().__init__(timeout=None)

@tree.command(name="shutdown", description="Вимкнути бота (тільки адмін)")
@app_commands.checks.has_permissions(administrator=True)
async def shutdown(interaction: discord.Interaction):
    await interaction.response.send_message("🛑 Вимикаю бота...", ephemeral=True)
    await log(f"🛑 **Бот вимкнено** адміном {interaction.user.mention}")
    await bot.close()

# ---------- RUN ----------
bot.run(TOKEN)
```

'
