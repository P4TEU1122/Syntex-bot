import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import random
import asyncio

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))
VERIFY_CHANNEL_ID = int(os.getenv('VERIFY_CHANNEL_ID'))

intents = discord.Intents.default()
intents.members = True  # Necesare pentru verificare
bot = commands.Bot(command_prefix="!", intents=intents)

# Rol de verificare
VERIFY_ROLE_NAME = "Verified"

@bot.event
async def on_ready():
    print(f'{bot.user} s-a conectat!')

# Comandă de start verificare
@bot.command()
async def verify(ctx):
    if ctx.channel.id != VERIFY_CHANNEL_ID:
        return await ctx.send("Comanda se poate folosi doar în canalul de verificare!")

    member = ctx.author
    guild = ctx.guild

    # Generăm o "provocare" simplă
    num1 = random.randint(1, 20)
    num2 = random.randint(1, 20)
    await ctx.send(f"{member.mention}, rezolvă: `{num1} + {num2}`")

    def check(m):
        return m.author == member and m.channel == ctx.channel

    try:
        msg = await bot.wait_for('message', check=check, timeout=30)
        if int(msg.content) == num1 + num2:
            role = discord.utils.get(guild.roles, name=VERIFY_ROLE_NAME)
            if role:
                await member.add_roles(role)
                await ctx.send(f"{member.mention} a fost verificat cu succes!")
            else:
                await ctx.send("Rolul de verificare nu există!")
        else:
            await ctx.send(f"{member.mention}, răspuns greșit!")
    except asyncio.TimeoutError:
        await ctx.send(f"{member.mention}, timpul a expirat!")

bot.run(TOKEN)
