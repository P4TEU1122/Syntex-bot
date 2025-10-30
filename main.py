import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

# 🔧 CONFIGURĂRI — schimbă cu valorile tale
VERIFY_CHANNEL_ID = 123456789012345678  # ID canal unde se trimite mesajul de verificare
VERIFIED_ROLE_ID = 987654321098765432  # ID rol oferit după verificare

intents = discord.Intents.default()
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Syntex este online ca {bot.user}")
    channel = bot.get_channel(VERIFY_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title="🔒 Syntex Verification",
            description="Apasă butonul de mai jos pentru a te verifica și a accesa serverul.",
            color=0x5865F2,
        )
        embed.set_footer(text="Syntex Security Bot")

        view = discord.ui.View()
        view.add_item(VerifyButton())

        await channel.send(embed=embed, view=view)

class VerifyButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Verify", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(VERIFIED_ROLE_ID)
        if role is None:
            await interaction.response.send_message("⚠️ Rolul de verificare nu a fost găsit.", ephemeral=True)
            return

        await interaction.user.add_roles(role)
        await interaction.response.send_message("✅ Ai fost verificat cu succes!", ephemeral=True)

# Rulează botul
bot.run(TOKEN)
