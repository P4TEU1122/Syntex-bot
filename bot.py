import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import random
import asyncio
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))
VERIFY_CHANNEL_ID = int(os.getenv('VERIFY_CHANNEL_ID'))
LOG_CHANNEL_ID = int(os.getenv('LOG_CHANNEL_ID'))
ROLE_UNVERIFIED_ID = int(os.getenv('ROLE_UNVERIFIED_ID'))
ROLE_VERIFIED_ID = int(os.getenv('ROLE_VERIFIED_ID'))

intents = discord.Intents.default()
intents.members = True
intents.message_content = True  # Necesită privilegii în portalul Discord
bot = commands.Bot(command_prefix="!", intents=intents)

MAX_ATTEMPTS = 3
TIMEOUT = 30
CAPTCHA_LENGTH = 6

FONTS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
]

# --- Funcție generare captcha ---
def generate_captcha():
    text = ''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ23456789', k=CAPTCHA_LENGTH))
    width, height = 200, 80
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    for i, char in enumerate(text):
        font = ImageFont.truetype(random.choice(FONTS), random.randint(30, 40))
        x = 10 + i * 30 + random.randint(-5, 5)
        y = random.randint(10, 30)
        color = tuple(random.randint(0, 150) for _ in range(3))
        draw.text((x, y), char, font=font, fill=color)

    # Noise - linii
    for _ in range(8):
        start = (random.randint(0, width), random.randint(0, height))
        end = (random.randint(0, width), random.randint(0, height))
        draw.line([start, end], fill=tuple(random.randint(0, 150) for _ in range(3)), width=2)

    # Noise - puncte
    for _ in range(30):
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.point((x, y), fill=tuple(random.randint(0, 150) for _ in range(3)))

    img = img.filter(ImageFilter.GaussianBlur(1))
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return text, buffer

# --- Bot ready ---
@bot.event
async def on_ready():
    print(f"{bot.user} s-a conectat!")

# --- Comandă verify ---
@bot.command()
async def verify(ctx):
    if ctx.channel.id != VERIFY_CHANNEL_ID:
        return await ctx.send("Comanda se poate folosi doar în canalul de verificare!")

    member = ctx.author
    guild = ctx.guild
    log_channel = guild.get_channel(LOG_CHANNEL_ID)
    role_unverified = guild.get_role(ROLE_UNVERIFIED_ID)
    role_verified = guild.get_role(ROLE_VERIFIED_ID)

    if role_unverified in member.roles:
        await member.remove_roles(role_unverified)

    attempts = 0
    success = False

    while attempts < MAX_ATTEMPTS and not success:
        captcha_text, captcha_image = generate_captcha()
        file = discord.File(fp=captcha_image, filename="captcha.png")

        embed = discord.Embed(
            title="Verificare Membri 🔒",
            description=f"{member.mention}, rezolvă captcha-ul pentru a te verifica!",
            color=discord.Color.blue()
        )
        embed.set_image(url="attachment://captcha.png")
        embed.set_footer(text=f"Ai {TIMEOUT} secunde să răspunzi, maxim {MAX_ATTEMPTS} încercări!")

        await ctx.send(embed=embed, file=file)

        def check(m):
            return m.author == member and m.channel == ctx.channel

        try:
            msg = await bot.wait_for('message', check=check, timeout=TIMEOUT)
            if msg.content.upper() == captcha_text:
                await member.add_roles(role_verified)
                
                embed_succes = discord.Embed(
                    title="✅ Verificare reușită!",
                    description=f"{member.mention} a fost verificat cu succes!",
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed_succes)

                if log_channel:
                    embed_log = discord.Embed(
                        title="Membri Verificați",
                        description=f"{member} a trecut verificarea.",
                        color=discord.Color.green()
                    )
                    await log_channel.send(embed=embed_log)

                success = True
            else:
                attempts += 1
                await ctx.send(f"{member.mention}, captcha greșit! Încercări rămase: {MAX_ATTEMPTS - attempts}")
        except asyncio.TimeoutError:
            attempts += 1
            await ctx.send(f"{member.mention}, timpul a expirat! Încercări rămase: {MAX_ATTEMPTS - attempts}")

    if not success:
        await member.add_roles(role_unverified)
        embed_fail = discord.Embed(
            title="❌ Verificare eșuată",
            description=f"{member.mention}, nu ai reușit să te verifici după {MAX_ATTEMPTS} încercări!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed_fail)

        if log_channel:
            embed_log = discord.Embed(
                title="Verificare eșuată",
                description=f"{member} a eșuat verificarea și a primit rolul neverificat.",
                color=discord.Color.red()
            )
            await log_channel.send(embed=embed_log)

# --- Run bot ---
bot.run(TOKEN)
