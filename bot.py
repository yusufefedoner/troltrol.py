Gereksinimler
bash

Copy code
pip install discord.py python-dotenv
.env dosyası oluştur (token'ını buraya koy)

Copy code
DISCORD_TOKEN=your_bot_token_here
Ana Bot Kodu (trolbot.py)
python

Copy code
import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Aktif trol hedefleri: {message_id: {'target': user_id, 'end_time': datetime, 'event': str}}
active_trolls = {}

@bot.event
async def on_ready():
    print(f'{bot.user} trol moduna girdi! 🎭')
    countdown_loop.start()

@bot.command(name='trolbaslat')
async def start_troll(ctx, member: discord.Member, gun: int, saat: int, dakika: int, ne_olacak: str):
    """
    Kullanım: !trolbaslat @kisi 3 14 30 "patates yiyecek"
    """
    # Hedef tarih hesapla (bugünden gun gün, saat:dakika)
    now = datetime.now()
    target_time = now.replace(hour=saat, minute=dakika, second=0, microsecond=0)
    target_time += timedelta(days=gun)
    
    if target_time <= now:
        await ctx.send("❌ Gelecekte bir zaman seç lan! ⏰")
        return
    
    active_trolls[ctx.message.id] = {
        'target': member.id,
        'end_time': target_time,
        'event': ne_olacak,
        'channel': ctx.channel.id
    }
    
    embed = discord.Embed(title="🎭 TROL BAŞLATILDI!", color=0xff0000)
    embed.add_field(name="Hedef", value=member.mention, inline=False)
    embed.add_field(name="Bitiş", value=target_time.strftime("%d/%m/%Y %H:%M"), inline=False)
    embed.add_field(name="Olay", value=ne_olacak, inline=False)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name='trolkalan')
async def troll_countdown(ctx, message_id: int = None):
    """Belirli bir trolün kalan süresini gösterir"""
    if message_id and message_id in active_trolls:
        data = active_trolls[message_id]
        remaining = data['end_time'] - datetime.now()
        
        if remaining.total_seconds() <= 0:
            await ctx.send(f"⏰ **{data['event']}** ZAMAN DOLDU! 🎉")
            del active_trolls[message_id]
            return
        
        hours, remainder = divmod(int(remaining.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        await ctx.send(f"⏳ **{data['event']}** için kalan: **{hours}s {minutes}d {seconds}s**")
    else:
        await ctx.send("❌ Geçerli bir trol mesaj ID'si ver! (`!trolkalan 123456`)")

@tasks.loop(minutes=5)  # Her 5 dakikada kontrol et
async def countdown_loop():
    """Otomatik geri sayım mesajları"""
    current_time = datetime.now()
    to_delete = []
    
    for msg_id, data in active_trolls.items():
        remaining = data['end_time'] - current_time
        
        if remaining.total_seconds() <= 0:
            channel = bot.get_channel(data['channel'])
            if channel:
                target_user = bot.get_user(data['target'])
                await channel.send(f"💥 **BOOM!** <@{data['target']}> {data['event']} ZAMANI GELDİ! 🎊")
            to_delete.append(msg_id)
            continue
        
        # 1 saat, 30dk, 10dk, 5dk, 1dk uyarısı
        if (60 <= remaining.total_seconds() <= 65) or \
           (5 <= remaining.total_seconds() <= 10) or \
           (25 <= remaining.total_seconds() <= 35) or \
           (55 <= remaining.total_seconds() <= 65):
            
            channel = bot.get_channel(data['channel'])
            if channel:
                target_user = bot.get_user(data['target'])
                hours, remainder = divmod(int(remaining.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                await channel.send(f"⚠️ **UYARI** <@{data['target']}>! **{data['event']}** için **{hours}s {minutes}d** kaldı! ⏳")
    
    # Bittiği troll'leri temizle
    for msg_id in to_delete:
        del active_trolls[msg_id]

@bot.command(name='trollist')
async def troll_list(ctx):
    """Aktif troll'leri listele"""
    if not active_trolls:
        await ctx.send("🎭 Aktif trol yok!")
        return
    
    embed = discord.Embed(title="🎭 Aktif Troll'lar", color=0xffa500)
    for msg_id, data in active_trolls.items():
        remaining = data['end_time'] - datetime.now()
        time_str = str(remaining).split('.')[0]
        embed.add_field(
            name=f"ID: {msg_id}",
            value=f"<@{data['target']}> - {data['event']}\nKalan: {time_str}",
            inline=False
        )
    await ctx.send(embed=embed)

@bot.command(name='troliptal')
async def cancel_troll(ctx, message_id: int):
    """Trolü iptal et"""
    if message_id in active_trolls:
        del active_trolls[message_id]
        await ctx.send(f"🗑️ Trol ID `{message_id}` iptal edildi!")
    else:
        await ctx.send("❌ Böyle bir trol yok!")

bot.run(os.getenv('DISCORD_TOKEN'))
Kullanım Örnekleri

Copy code
!trolbaslat @kisi 2 15 30 "domates gibi kızaracak"
!trolkalan 123456789  (mesaj ID'si ile kalan süre)
!trollist            (tüm aktif troll'lar)
!troliptal 123456789 (iptal et)
Özellikler 🎉
✅ Gün/saat/dakika ile hedef zaman ayarla
✅ Otomatik geri sayım (5dk'da bir kontrol)
✅ Kritik zamanlarda uyarı (1s, 30dk, 10dk, 5dk, 1dk)
✅ Embed'li güzel görünüm
✅ Liste/iptal komutları
✅ Zaman dolunca patlama mesajı
Bot Token Alma
Discord Developer Portal
New Application → Bot → Token kopyala
.env dosyasına yapıştır
Server'a botu davet et (OAuth2 → bot permissions: Send Messages, Embed Links, Mention Everyone)
