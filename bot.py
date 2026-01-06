import discord
from discord import app_commands, ButtonStyle
from discord.ui import View, Button
import asyncio
import json
import os
from dotenv import load_dotenv

# ---------- ENV ----------
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")  # У .env: DISCORD_TOKEN=твой_токен

# ---------- CONFIG ----------
CONFIG_FILE = "config.json"
DELETE_FINISHED_AFTER = 1800  # 30 хвилин
event_messages = {}

# Завантажуємо/створюємо конфіг
def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "event_channel_id": None,
                "log_channel_id": None,
                "role_id": None
            }, f, indent=4)
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

config = load_config()

# ---------- DISCORD ----------
intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True

bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# ---------- BUTTON ----------
def event_button(url: str):
    view = View()
    view.add_item(Button(
        label="Приєднатись до події",
        style=ButtonStyle.link,
        url=url
    ))
    return view

# ---------- READY ----------
@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Бот онлайн як {bot.user}")

# ---------- LOG ----------
async def log(message: str):
    if config.get("log_channel_id"):
        channel = bot.get_channel(config["log_channel_id"])
        if channel:
            await channel.send(message)

# ---------- SETUP ----------
@tree.command(name="setup", description="Налаштувати бота (тільки адмін)")
@app_commands.describe(
    event_channel="Канал для подій",
    log_channel="Канал для логів",
    role="Роль для пінгу"
)
async def setup(interaction: discord.Interaction,
                event_channel: discord.TextChannel,
                log_channel: discord.TextChannel,
                role: discord.Role):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ Тільки адміністратор може налаштовувати бота",
            ephemeral=True
        )
        return

    config["event_channel_id"] = event_channel.id
    config["log_channel_id"] = log_channel.id
    config["role_id"] = role.id
    save_config(config)

    await interaction.response.send_message(
        f"✅ Бот налаштовано\n"
        f"📢 Події: {event_channel.mention}\n"
        f"📝 Логи: {log_channel.mention}\n"
        f"👥 Роль: {role.mention}",
        ephemeral=True
    )

# ---------- EVENT ----------
@tree.command(name="event", description="Оголосити подію")
async def event(interaction: discord.Interaction, name: str, url: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Тільки адміністратори", ephemeral=True)
        return

    if not all(config.values()):
        await interaction.response.send_message("❌ Бот не налаштований. Використай `/setup`", ephemeral=True)
        return

    channel = bot.get_channel(config["event_channel_id"])
    role_id = config["role_id"]

    msg = await channel.send(
        f"📢 **Нова подія**\n{name}\n<@&{role_id}>",
        view=event_button(url)
    )

    await interaction.response.send_message("✅ Подію опубліковано", ephemeral=True)
    await log(f"📢 Подія створена: **{name}**\n👤 {interaction.user.mention}")

# ---------- SHUTDOWN ----------
@tree.command(name="shutdown", description="Вимкнути бота (тільки адмін)")
async def shutdown(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Тільки адміністратор", ephemeral=True)
        return

    await interaction.response.send_message("🛑 Бот вимикається...", ephemeral=True)
    await log(f"🛑 Бот вимкнено\n👤 {interaction.user.mention}")
    await bot.close()

# ---------- RESTART ----------
@tree.command(name="restart", description="Перезапустити бота (тільки адмін)")
async def restart(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Тільки адміністратор", ephemeral=True)
        return

    await interaction.response.send_message("🔁 Бот перезапускається...", ephemeral=True)
    await log(f"🔁 Бот перезапущено\n👤 {interaction.user.mention}")
    await bot.close()  # Render/хостинг автоматично перезапустить

# ---------- RUN ----------
bot.run(TOKEN)
