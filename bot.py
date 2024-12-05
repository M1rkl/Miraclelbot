import discord
from discord.ext import commands
from discord.ext.commands import Bot
import disnake
from config import settings
from Cybernator import Paginator as pag
from discord.utils import get
import sqlite3
from sqlite3.dbapi2 import Cursor

from time import sleep
import requests
from PIL import  Image, ImageFont, ImageDraw
import io
from pymongo import  MongoClient
import json

import random
import configparser
import webbrowser
import urllib3

import datetime
import sys
import shutil
import io
from typing import Optional
from discord import Embed
import os
import asyncio
from asyncio import sleep
from datetime import datetime
from typing import Optional

from discord import Embed,Member
from discord.ext.commands import Cog
from discord.ext.commands import command
from discord.ext.commands import bot
import nekos
from discord import Activity, ActivityType
import time
import math
from io import BytesIO
from discord import Spotify
from discord.ext import commands, tasks
import youtube_dl
import pycord


intents=discord.Intents.all()
client: Bot = commands.Bot(intents=intents,command_prefix=settings['PREFIX'],test_guilds=['ur server'] )
client.remove_command('help')

connection = sqlite3.connect('server.db')
cursor: Cursor = connection.cursor()

# + custom in profile
@client.event
async def on_ready() :
    await client.change_presence(status=discord.Status.online, activity=discord.Game('closed beta testing 1.2v.'))
    cursor.execute( """CREATE TABLE IF NOT EXISTS users (
        name TEXT,
        id INT,
        cash BIGINT,
        rep INT,
        lvl INT,
        server_id INT
    )""" )

    cursor.execute( """CREATE TABLE IF NOT EXISTS shop (
        role_id INT,
        id INT,
        cost BIGINT
    )""" )

    for guild in client.guilds:
        for member in guild.members:
            if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
                cursor.execute( f"INSERT INTO users VALUES ('{member}', {member.id}, 0, 0, 1, {guild.id})" )
            else:
                pass
    print('bot can work yay')
    await client.change_presence(status=discord.Status.online, activity=discord.Game('closed beta testing 1.2v.'))

@client.event
async def on_member_join(member):
    if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
        cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0, 0, 1, {member.guild.id})")
        connection.commit()
    else:
        pass




@client.command( aliases=['balance','cash'] )
async def __balance(ctx,member: discord.Member = None) :
    if member is None :
        await ctx.send( embed=discord.Embed(
            description=f"""Баланс пользователя **{ctx.author}** составляет **{cursor.execute( "SELECT cash FROM users WHERE id = {}".format( ctx.author.id ) ).fetchone() [0]} :leaves:**"""
        ) )

    else :
        await ctx.send( embed=discord.Embed(
            description=f"""Баланс пользователя **{member}** составляет **{cursor.execute( "SELECT cash FROM users WHERE id = {}".format( member.id ) ).fetchone() [0]} :leaves:**"""
        ) )


@client.command( aliases=['award'] )
async def __award(ctx,member: discord.Member = None,amount: int = None) :
    if member is None :
        await ctx.send( f"**{ctx.author}**, укажите пользователя, которому желаете выдать определенную сумму" )
    else :
        if amount is None :
            await ctx.send( f"**{ctx.author}**, укажите сумму, которую желаете начислить на счет пользователя" )
        elif amount < 1 :
            await ctx.send( f"**{ctx.author}**, укажите сумму больше 1 :leaves:" )
        else :
            cursor.execute( "UPDATE users SET cash = cash + {} WHERE id = {}".format( amount,member.id ) )
            connection.commit()

            await ctx.message.add_reaction( '✅' )


@client.command( aliases=['take'] )
async def __take(ctx,member: discord.Member = None,amount=None) :
    if member is None :
        await ctx.send( f"**{ctx.author}**, укажите пользователя, у которого желаете отнять сумму денег" )
    else :
        if amount is None :
            await ctx.send( f"**{ctx.author}**, укажите сумму, которую желаете отнять у счета пользователя" )
        elif amount == 'all' :
            cursor.execute( "UPDATE users SET cash = {} WHERE id = {}".format( 0,member.id ) )
            connection.commit()

            await ctx.message.add_reaction( '✅' )
        elif int( amount ) < 1 :
            await ctx.send( f"**{ctx.author}**, укажите сумму больше 1 :leaves:" )
        else :
            cursor.execute( "UPDATE users SET cash = cash - {} WHERE id = {}".format( int( amount ),member.id ) )
            connection.commit()

            await ctx.message.add_reaction( '✅' )


@client.command( aliases=['add-shop'] )
async def __add_shop(ctx,role: discord.Role = None,cost: int = None) :
    if role is None :
        await ctx.send( f"**{ctx.author}**, укажите роль, которую вы желаете внести в магазин" )
    else :
        if cost is None :
            await ctx.send( f"**{ctx.author}**, укажите стоимость для даннойй роли" )
        elif cost < 0 :
            await ctx.send( f"**{ctx.author}**, стоимость роли не может быть такой маленькой" )
        else :
            cursor.execute( "INSERT INTO shop VALUES ({}, {}, {})".format( role.id,ctx.guild.id,cost ) )
            connection.commit()

            await ctx.message.add_reaction( '✅' )


@client.command( aliases=['remove-shop'] )
async def __remove_shop(ctx,role: discord.Role = None) :
    if role is None :
        await ctx.send( f"**{ctx.author}**, укажите роль, которую вы желаете удалить из магазина" )
    else :
        cursor.execute( "DELETE FROM shop WHERE role_id = {}".format( role.id ) )
        connection.commit()

        await ctx.message.add_reaction( '✅' )


@client.command( aliases=['shop'] )
async def __shop(ctx) :
    embed = discord.Embed( title='Магазин ролей' )

    for row in cursor.execute( "SELECT role_id, cost FROM shop WHERE id = {}".format( ctx.guild.id ) ) :
        if ctx.guild.get_role( row [0] ) != None :
            embed.add_field(
                name=f"Стоимость **{row [1]} :leaves:**",
                value=f"Вы приобрете роль {ctx.guild.get_role( row [0] ).mention}",
                inline=False
            )
        else :
            pass

    await ctx.send( embed=embed )


@client.command(aliases=['buy', 'buy-role'])
async def __buy(ctx, role: discord.Role = None):
    if role is None:
        await ctx.send(f"**{ctx.author}**, укажите роль, которую вы желаете приобрести")
    else:
        if role in ctx.author.roles:
            await ctx.send(f"**{ctx.author}**, у вас уже имеется данная роль")
        elif cursor.execute("SELECT cost FROM shop WHERE role_id = {}".format(role.id)).fetchone()[0] > \
                cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]:
            await ctx.send(f"**{ctx.author}**, у вас недостаточно средств для покупки данной роли")
        else:
            await ctx.author.add_roles(role)
            cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(
                cursor.execute("SELECT cost FROM shop WHERE role_id = {}".format(role.id)).fetchone()[0],
                ctx.author.id))
            connection.commit()

            await ctx.message.add_reaction('✅')


@client.command(aliases=['rep', '+rep'])
async def __rep(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send(f"**{ctx.author}**, укажите участника сервера")
    else:
        if member.id == ctx.author.id:
            await ctx.send(f"**{ctx.author}**, вы не можете указать самого себя")
        else:
            cursor.execute("UPDATE users SET rep = rep + {} WHERE id = {}".format(1, member.id))
            connection.commit()

            await ctx.message.add_reaction('✅')


@client.command(aliases=['leaderboard', 'lb'])
async def __leaderboard(ctx):
    embed = discord.Embed(title='Топ 10 сервера')
    counter = 0

    for row in cursor.execute(
            "SELECT name, cash FROM users WHERE server_id = {} ORDER BY cash DESC LIMIT 10".format(ctx.guild.id)):
        counter += 1
        embed.add_field(
            name=f'# {counter} | `{row[0]}`',
            value=f'Баланс: {row[1]}',
            inline=False
        )

    await ctx.send(embed=embed)


# Clear message
@client.command(pass_context = True)
@commands.has_permissions(administrator=True)
async def clear(ctx, amount = 100):
    await ctx.channel.purge(limit = amount)
    await ctx.send("Успешно очистил " + str(amount) + " сообщений.")

# Help command
@client.command(pass_context = True)
@commands.has_permissions(administrator = True)

async def help( ctx ):
    if ctx.author.id == 292603927315087360 :
        emb = discord.Embed( title = ' 🛠 Команды бота 🖥 {Префиксы m! либо !}' )

        emb.add_field ( name = '{}clear'.format ( "m!" ), value = "Очистка чата" )
        emb.add_field ( name = '{}award'.format ( "💴" ), value = "Выдача указаному пользователю сумму" )
        emb.add_field( name = '{}take'.format( "💴" ), value = "Забрать деньги у указаного пользователя")
        emb.add_field ( name = '{}lb'.format ( " 🏆 " ), value = "Показывает топ 10 сервера(по деньгам)" )
        emb.add_field ( name = '{}shop'.format ( " 💱 " ), value = "Показывает магазин ролей сервера" )
        emb.add_field ( name = '{}buy'.format ( "💸" ),value = "При прописание данный команды выбирите роль которую хотите купить на вашем сервере")
        emb.add_field( name = '{}cash/balance' .format( " 💰 " ),value = "Вы можете узнать свой баланс, или же баланс указаного пользователя")
        emb.add_field ( name = '{}+rep/rep'.format ( "m!" ), value = "Вы дадите rep указаному человеку или же отдадите честь)")
        emb.add_field(name = '{}не сколько слов'.format ("просто "),value = "Бот находится на ранней стадии и нуждается в доработках и многих команах)")
        emb.add_field(name='{}ещё не сколько слов'.format(" "), value="Для админ команд и всего прочего будет создана отдельная команда")
        emb.set_footer( text=f"Вызвал:{ctx.message.author}",icon_url=ctx.message.author.avatar_url )
        await ctx.send(embed = emb)




#Voice management(закрыто)

@client.command()
async def join(ctx):
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild = ctx.guild )
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        await ctx.send(f'Вот я и в канале {channel} готов?')

@client.command()
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild = ctx.guild )
    if voice and voice.is_connected():
        await voice.disconnect()
    else:
        await ctx.send(f'Всем пока удачки вам я ухожу из {channel} ')

#Muscom(закрыто)
@client.command()
async def play(ctx, url:str):
    global voice,name
    song_there = os.path.isfile('song.mp3')

    try:
        if song_there:
            os.remove('song.mp3')
            print('[log]Старый файл удалён')
    except PremissionError:
        print('[log] F отмена файл не удалился')

        await ctx.send('Подожди немного')

        voice = get(client.voice_clients, guild = ctx.guild)

        ydl_opts = {
            'format' : 'bestaudio/best',
            'postprocessors' : [{
                'key' : 'FFmpegExtractAudio',
                'preferredcodec' : 'mp3',
                'preferredquality' : '192'
            }]
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            print('[log] Ожидай уже загружаю твой музон...')
            ydl.download([url])

    for file in os.listdir('./'):
        if file.endswith('.mp3'):
            name = file
            print('[log] Переименовываю {file}')
            os.rename(file, 'song.mp3')

    assert isinstance (voice) ,object
    voice.play(discord.FFmpegPCMAudio('song.mp3'), after = lambda e: print(f'[log] {name}, всё музыка закончилась'))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.07

    song_name = name.rsplit('-', 2)
    await ctx.send(f'Во щя играет {song_name[0]}')


#dont work
@client.command(name="dem")
async def dem (self, ctx, text1: str = None,*, text2: str = None):
        files = []
        for file in ctx.message.attachments:
            fp = io.BytesIO()
            await file.save(fp = 'kek.jpg')
        dem = demcreate(f'{text1}', f'{text2}')
        dem.makeImage('kek')
        await ctx.send(file = discord.File(fp = 'demresult.jpg'))


#Попытка si(dont work)
@client.command(name='guilds')
async def guilds(self, ctx):
        if ctx.author.id == 292603927315087360:
            emb = discord.Embed(title = 'Сервера бота', color = discord.Color.green())
            for guild in self.client.guilds:
                if not guild.system_channel is None:
                    channel = guild.system_channel
                    link = await channel.create_invite()
                else:
                    link = 'Отсутствует'
                emb.add_field(name = f'{guild.name}', value = f"Овнер - {guild.owner}\nИнвайт - {link}", inline = False)
            await ctx.send(embed = emb)
        else:
            await ctx.send('у вас нет доступа к этой команде!')


#ui(dont work how i want)
@client.command()
async def userinfo(ctx, member: discord.Member):
    if ctx.author.id == 292603927315087360 :
        member = ctx.author if not member else member
        roles = [role for role in member.roles]
        embed = discord.Embed(colour=member.color, timestamp=ctx.message.created_at)
        embed.set_author(name=f"User info - {member}")
        embed.set_thumbnail(url=member.avater_url)
        embed.set_footer(text=f"Вызвал  тебя, или хотел у знать кто ты {ctx.author}", icon_url=ctx.author_url)

        embed.add_field(name="ID:", value=member.id)
        embed.add_field(name="Guild name:", value=member.display_name)

        embed.add_field(name="Created at:", value=member.created_at.strftime("%a, $#d, %y, %I:%M %p UTC"))
        embed.add_field(name="Joined at:", value=member.joined_at.strftime("%a, $#d, %y, %I:%M %p UTC"))

        embed.add_field(name=f"Roles({len(roles)})", value="".join([role.mention for role in Roles]))
        await ctx.send(embed=embed)

#Попытка si
@client.command()
async def si(ctx,guild:discord.Guild=None):

        guild=ctx.guild if not guild else guild
        embed = discord.Embed(title=f"Информация о {guild}", description="Бахнул мирк", timestamp=ctx.message.created_at)
        embed.set_thumbnail(url=guild.icon_url)
        embed.add_field( name="Описание", value=guild.description, inline=False)
        embed.add_field(name="Скока каналов:", value= len(guild.channels), inline=False)
        embed.add_field(name="Сколько ролей:", value=len(guild.roles), inline=False)
        embed.add_field(name="Сколько людей", value= guild.member_count, inline=False)
        embed.add_field(name="Сделали в:", value=guild.created_at, inline=False)
        embed.add_field(name="Регион:", value=f"{ctx.guild.region}")
        embed.add_field(name="Максимально emoji", value=guild.emoji_limit,inline=False)
        embed.add_field(name="Создатель",value=guild.owner,inline=False)
        embed.add_field(name="ID Создателя",value=guild.owner_id,inline=False)
        embed.set_footer(text=f"Вызвал: {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)



#waifu
@client.command(aliases = ['waifu','вайфу','Waifu','Вайфу'])
async def user_anime(ctx):
    r = requests.get("https://nekos.life/api/v2/img/waifu")
    res = r.json()
    embed = discord.Embed(title='Waifu/Вайфу')
    embed.set_image(url=res['url'])
    embed.set_footer( text=f"Вызвал: {ctx.message.author}",icon_url=ctx.message.author.avatar_url )
    await ctx.send(embed = embed)


#password maker(dont work)
@client.command()
async def password(ctx):
        try:
            def get_password(date):
                max = 10
                password = ""
                while len(password) != max:
                    value = random.choice(date)
                    password += value
                return password
            date = "qwertyuiopasdfghjklzxcvbnm_1234567890"
            embed = discord.Embed(timestamp=ctx.message.created_at , description='**your password:** {}'.format(get_password(date)))
            embed.set_footer(text="NOTE: This is a random password")
            embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
            await ctx.author.send(embed=embed)
            await ctx.channel.send(f'The private password has been sent in your dm {ctx.author.mention}')
        except:
            await ctx.send(f'Open your private please {ctx.author.mention}')

#  ui
@client.command()
async def ui(ctx,member:discord.Member):
    embed = discord.Embed(title=f"Информация о пользователе {user}")
    embed.add_field(name="Имя пользователя:", value=member.display_name,inline=False)
    embed.add_field(name="ID:", value=member.id,inline=False)
    embed.add_field(name="Ролей:",value=f'{len(member.roles)}',inline=False)
    embed.add_field(name='Главная роль:',value=f'{member.top_role.name}',inline=False)
    embed.add_field( name="Присойденился:",value=member.joined_at,inline=False )
    embed.add_field(name="Появился на свет, ой тоесть создал акаунт:",value=member.created_at.strftime("%a,%#d %B %Y"), inline=False)
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_footer(text=f"Вызвал: {ctx.message.author}", icon_url=ctx.message.author.avatar_url)
    await ctx.send (embed=embed)

@ui.error
async def ui_error(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
            embed = discord.Embed( title=f"Информация о пользователе {ctx.author}" )
            embed.add_field( name="Имя пользователя:",value=ctx.message.author.display_name,inline=False )
            embed.add_field( name="ID:",value=ctx.message.author.id,inline=False )
            embed.add_field( name="Ролей:",value=f'{len( ctx.author.roles )}',inline=False )
            embed.add_field( name='Главная роль:',value=f'{ctx.author.top_role.name}',inline=False )
            embed.add_field( name="Присойденился:",value=ctx.message.author.joined_at,inline=False )
            embed.add_field( name="Появился на свет, ой тоесть создал акаунт:",value=ctx.author.created_at.strftime( "%a,%#d %B %Y" ),inline=False )
            embed.set_thumbnail( url=ctx.message.author.avatar_url )
            embed.set_footer( text=f"Вызвал:{ctx.message.author}",icon_url=ctx.message.author.avatar_url )
            await ctx.send( embed=embed )

# say почему нет .-.
@client.command()
async def say(ctx,*,message):
    if ctx.author.id == 292603927315087360 :
        await ctx.message.delete()
        await ctx.send(f"{message}".format(message))

#avatar
@client.command()
async def avatar(ctx,user:discord.Member):
    embed = discord.Embed(description=f"**Avatar** {user.mention}")
    embed.set_image(url=f"{user.avatar_url}")
    embed.set_footer(text=f"Вызвал:{ctx.message.author}", icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed=embed)
@avatar.error
async def av_error(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        embed= discord.Embed(description=f"**Avatar** {ctx.author.mention}")
        embed.set_image(url=f"{ctx.author.avatar_url}")
        embed.set_footer( text=f"Вызвал:{ctx.message.author}",icon_url=ctx.message.author.avatar_url )
        await ctx.send(embed=embed)

# рандомное число почему нет
@client.command()
async def rm(ctx):
    embed = discord.Embed(title="Рандомное число")
    embed.add_field(name="А вот и оно .-. забыл просто там написать",value=(random.randint(0,100000)))
    embed.set_footer(text=f"Вызвал:{ctx.message.author}", icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed=embed)

# 8ball
@client.command()
async def ball(ctx,message):
     answers = ['Да','Нет','Может быть','На такое я не готов ответить','Опа попався пакуем его ребят','Скорее всего да, чем нет','Не знаю','Скорее всего нет, чем да']
     embed = discord.Embed(title="8ball")
     embed.add_field(name="Ответ:",value=random.choice(answers))
     embed.set_footer( text=f"Вызвал: {ctx.message.author}",icon_url=ctx.message.author.avatar_url )
     await ctx.send(embed=embed)

#ping
@client.command()
async def ping(ctx):
    embed = discord.Embed( title="Ping/Пинг" )
    embed.add_field(name="а да вот:",value=f'{round(client.latency * 1000)}ms')
    embed.set_footer( text=f"Вызвал:{ctx.message.author}",icon_url=ctx.message.author.avatar_url )
    await ctx.send(embed=embed)


#rpcommand(дорабатывается)
@client.command()
async def hug (ctx,user:discord.Member):
    r = requests.get("https://nekos.life/api/v2/img/hug")
    res = r.json()
    embed = discord.Embed(description=f"{ctx.author.mention}  Обнимает  {user.mention}")
    embed.set_image(url=res['url'])
    embed.set_footer(text=f"Вызвал:{ctx.message.author}",icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed=embed)
@hug.error
async def hug_error(ctx,error):
    if isinstance( error,commands.MissingRequiredArgument ) :
        embed = discord.Embed(title="Ошибка")
        embed.add_field(name="Как исправить:",value="Укажите пользователя", inline=False)
        embed.set_footer( text=f"Вызвал:{ctx.message.author}",icon_url=ctx.message.author.avatar_url )
    await ctx.send(embed=embed)

@client.command()
async def slap(ctx,user:discord.Member):
    r = requests.get('https://nekos.life/api/v2/img/slap')
    res = r.json()
    embed = discord.Embed(description=f'{ctx.author.mention} Дал пошёчину {user.mention}')
    embed.set_image(url=res['url'])
    embed.set_footer( text=f"Вызвал:{ctx.message.author}",icon_url=ctx.message.author.avatar_url )
    await ctx.send( embed=embed )
@slap.error
async def slap_error(ctx,error):
    if isinstance( error,commands.MissingRequiredArgument ) :
        embed = discord.Embed(title="Ошибка")
        embed.add_field(name="Как исправить:",value="Укажите пользователя", inline=False)
        embed.set_footer( text=f"Вызвал:{ctx.message.author}",icon_url=ctx.message.author.avatar_url )
    await ctx.send(embed=embed)
@client.command()
async def pat(ctx,user:discord.Member):
    r = requests.get('https://nekos.life/api/v2/img/pat')
    res = r.json()
    embed = discord.Embed(description=f'{ctx.author.mention} Похлопал/Погладил {user.mention}')
    embed.set_image(url=res['url'])
    embed.set_footer( text=f"Вызвал:{ctx.message.author}",icon_url=ctx.message.author.avatar_url )
    await ctx.send( embed=embed )
@pat.error
async def pat_error(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        embed = discord.Embed( title="Ошибка" )
        embed.add_field( name="Как исправить:",value="Укажите пользователя",inline=False )
        embed.set_footer( text=f"Вызвал:{ctx.message.author}",icon_url=ctx.message.author.avatar_url )
    await ctx.send( embed=embed )
@client.command()
async def kiss(ctx,user:discord.Member):
    r = requests.get('https://nekos.life/api/v2/img/kiss')
    res = r.json()
    embed = discord.Embed(description=f'{ctx.author.mention} Поцеловал {user.mention}')
    embed.set_image(url=res['url'])
    embed.set_footer( text=f"Вызвал:{ctx.message.author}",icon_url=ctx.message.author.avatar_url )
    await ctx.send( embed=embed )
@kiss.error
async def kiss_error(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        embed = discord.Embed( title="Ошибка" )
        embed.add_field( name="Как исправить:",value="Укажите пользователя",inline=False )
        embed.set_footer( text=f"Вызвал:{ctx.message.author}",icon_url=ctx.message.author.avatar_url )
    await ctx.send(embed=embed)
@client.command()
async def baka(ctx,user:discord.Member):
    r = requests.get('https://nekos.life/api/v2/img/baka')
    res = r.json()
    embed = discord.Embed(description=f'{ctx.author.mention} назвал дураком {user.mention}')
    embed.set_image(url=res['url'])
    embed.set_footer( text=f"Вызвал:{ctx.message.author}",icon_url=ctx.message.author.avatar_url )
    await ctx.send( embed=embed )
@baka.error
async def baka_error(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        embed = discord.Embed( title="Ошибка" )
        embed.add_field( name="Как исправить:",value="Укажите пользователя",inline=False )
        embed.set_footer( text=f"Вызвал:{ctx.message.author}",icon_url=ctx.message.author.avatar_url )
    await ctx.send(embed=embed)
@client.command()
async def feed(ctx,user:discord.Member):
    r = requests.get('https://nekos.life/api/v2/img/feed')
    res = r.json()
    embed = discord.Embed(description=f'{ctx.author.mention} Покормил {user.mention}')
    embed.set_image(url=res['url'])
    embed.set_footer( text=f"Вызвал:{ctx.message.author}",icon_url=ctx.message.author.avatar_url )
    await ctx.send( embed=embed )
@feed.error
async def feed_error(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        embed = discord.Embed( title="Ошибка" )
        embed.add_field( name="Как исправить:",value="Укажите пользователя",inline=False )
        embed.set_footer( text=f"Вызвал:{ctx.message.author}",icon_url=ctx.message.author.avatar_url )
    await ctx.send(embed=embed)
@client.command()
async def cuddle(ctx,user:discord.Member):
    r = requests.get('https://nekos.life/api/v2/img/cuddle')
    res = r.json()
    embed = discord.Embed(description=f'{ctx.author.mention} Прижался к  {user.mention}')
    embed.set_image(url=res['url'])
    embed.set_footer( text=f"Вызвал:{ctx.message.author}",icon_url=ctx.message.author.avatar_url )
    await ctx.send(embed=embed)
@cuddle.error
async def cuddle_error(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        embed = discord.Embed( title="Ошибка" )
        embed.add_field( name="Как исправить:",value="Укажите пользователя",inline=False )
        embed.set_footer( text=f"Вызвал:{ctx.message.author}",icon_url=ctx.message.author.avatar_url )
    await ctx.send(embed=embed)
@client.command()
async def poke (ctx,user:discord.Member):
    r = requests.get('https://nekos.life/api/v2/img/poke')
    res = r.json()
    embed = discord.Embed(description=f'{ctx.author.mention} Достаёт {user.mention}')
    embed.set_image(url=res['url'])
    embed.set_footer( text=f"Вызвал:{ctx.message.author}",icon_url=ctx.message.author.avatar_url )
    await ctx.send( embed=embed )
@poke.error
async def poke_error(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        embed = discord.Embed( title="Ошибка" )
        embed.add_field( name="Как исправить:",value="Укажите пользователя",inline=False )
        embed.set_footer( text=f"Вызвал:{ctx.message.author}",icon_url=ctx.message.author.avatar_url )
    await ctx.send(embed=embed)
@client.command()
async def smug(ctx):
    r = requests.get('https://nekos.life/api/v2/img/smug')
    res = r.json()
    embed = discord.Embed(description=f'{ctx.author.mention} выбглядит самодовольно')
    embed.set_image(url=res['url'])
    embed.set_footer( text=f"Вызвал:{ctx.message.author}",icon_url=ctx.message.author.avatar_url )
    await ctx.send( embed=embed )

@client.command()
async def kill(ctx,user:discord.Member):
    r = requests.get('https://miss.perssbest.repl.co/api/v2/kill')#'https://miss.perssbest.repl.co/api/v2/view'
    res = r.json()
    embed = discord.Embed(description=f'{ctx.author.mention} Убил {user.mention}')
    embed.set_image(url=res['image'])
    embed.set_footer( text=f"Вызвал:{ctx.message.author}",icon_url=ctx.message.author.avatar_url )
    await ctx.send( embed=embed )
@kill.error
async def kill_error(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        embed = discord.Embed( title="Ошибка" )
        embed.add_field( name="Как исправить:",value="Укажите пользователя",inline=False )
        embed.set_footer( text=f"Вызвал:{ctx.message.author}",icon_url=ctx.message.author.avatar_url )
        await ctx.send( embed=embed)
@client.command()
async def view(ctx,user:discord.Member):
    r = requests.get('https://miss.perssbest.repl.co/api/v2/view')
    res = r.json()
    embed = discord.Embed(description=f'{ctx.author.mention} Смотрит на {user.mention}')
    embed.set_image(url=res['image'])
    embed.set_footer( text=f"Вызвал:{ctx.message.author}",icon_url=ctx.message.author.avatar_url )
    await ctx.send( embed=embed )
@view.error
async def view_error(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        embed = discord.Embed( title="Ошибка" )
        embed.add_field( name="Как исправить:",value="Укажите пользователя",inline=False )
        embed.set_footer( text=f"Вызвал:{ctx.message.author}",icon_url=ctx.message.author.avatar_url )
        await ctx.send(embed=embed)
@client.command()
async def cry (ctx,user:discord.Member):
    r = requests.get('https://miss.perssbest.repl.co/api/v2/cry')
    res = r.json()
    embed = discord.Embed(description=f'{ctx.author.mention} Плачет с(из-за) {user.mention}')
    embed.set_image(url=res['image'])
    embed.set_footer( text=f"Вызвал:{ctx.message.author}",icon_url=ctx.message.author.avatar_url )
    await ctx.send( embed=embed )
@cry.error
async def cry_error(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        embed = discord.Embed( title="Ошибка" )
        embed.add_field( name="Как исправить:",value="Укажите пользователя",inline=False )
        embed.set_footer( text=f"Вызвал:{ctx.message.author}",icon_url=ctx.message.author.avatar_url )
        await ctx.send(embed=embed)
#channaelsinfo(закрыто)
@client.command()
async def cs(self,ctx):
    channel = ctx.channel
    embed = discord.Embed(title=f"Информация о **{channel.name}**", description=f"{'Категория: {}'.format(channel.category.name) if channel.category else 'This channel is not on a category'}")
    embed.add_field(name="Назвине канала",value=ctx.guild.name,inline=False)
    embed.add_field(name="ID канала",value=channel.id,inline=False)
    embed.add_field(name="Описание канала",value=f"{channel.topic if channel.topic else 'Нету описания .-.'}", inline= false)
    embed.add_field(name="Позиция канала",value=channel.position, inline=False)
    embed.add_field(name="Slowmode", value=channel.slowmode_delay,inline=False)
    embed.add_field(name="NSFW?", value=channel.is_nsfw(),inline=False)
    embed.add_field(name="Новости?/Правила?",value=channel.is_news(),inline=False)
    embed.add_field(name="Канал создан",value=channel.created_at,inline=False)
    embed.add_field(name="Channels Hash",value=hash(channel),inline=False)
    embed.set_footer( text=f"Вызвал:{ctx.message.author}",icon_url=ctx.message.author.avatar_url )
    await ctx.send(embed=embed)

#DM
@client.command()
async def dm(ctx,user: discord.User,*,msg):
    if ctx.author.id == 292603927315087360 :
        await ctx.send('Ваше сообщение отправленно')
        await user.send(f'{msg}')

#test
@client.command()
async def test(ctx):
    if ctx.author.id == 292603927315087360 :
        embed = discord.Embed(title="Проверка")
        embed.add_field(name="Меня не надо проверять,",value="Шизик",inline=False)
        embed.add_field(name="Мой пинг",value=f'{round(client.latency * 1000)}ms',inline=False)
        embed.set_footer( text=f"Вызвал:{ctx.message.author}",icon_url=ctx.message.author.avatar_url )
        await ctx.send(embed=embed)
    else:
        await ctx.send('here u put what u want')


#mute
@client.command()
@commands.has_permissions(administrator=True)
async def мут(ctx, member:discord.Member, duration, *, reason=None):

    unit = duration[-1]
    print(f'{unit}')
    if unit == 'с':
        time = int(duration[:-1])
        longunit = 'секунд'
    elif unit == 'м':
        time = int(duration[:-1]) * 60
        longunit = 'минут'
    elif unit == 'ч':
        time = int(duration[:-1]) * 60 * 60
        longunit = 'часов'
    else:
        await ctx.send('Неправильно! Пиши `c`, `м`, `ч`')
        return

    progress = await ctx.send('Пользователь теперь замучен!')
    try:
        for channel in ctx.guild.text_channels:
            await channel.set_permissions(member, overwrite=discord.PermissionOverwrite(send_messages = False), reason=reason)

        for channel in ctx.guild.voice_channels:
            await channel.set_permissions(member, overwrite=discord.PermissionOverwrite(speak=False), reason=reason)
    except:
        success = False
    else:
        success = True

    await ctx.send(f'{member} замучен на {duration}')
    await asyncio.sleep(time)
    try:
        for channel in ctx.guild.channels:
             await channel.set_permissions(member, overwrite=None, reason=reason)
    except:
        pass
@мут.error
async def мут_error(ctx,error):
    if isinstance( error,commands.MissingRequiredArgument ) :
        embed = discord.Embed( title="Ошибка" )
        embed.add_field( name="Как исправить:",value="Укажите пользователя",inline=False )
        embed.set_footer( text=f"Вызвал: {ctx.message.author}",icon_url=ctx.message.author.avatar_url )
    await ctx.send( embed=embed )


@client.command(aliases=["l"])
async def lyrics(ctx, *, zapros=None):
    if zapros is None:
        await ctx.send("Введите фрагмент песни для поиска")
    else:
        reponse = requests.get(f"https://some-random-api.ml/lyrics?title={zapros}")
        otv = reponse.json()
        try:
            embed=discord.Embed(title="Genius", url=f"{otv['links']['genius']}", description=otv['lyrics'])
            embed.set_author(name=f"{otv['author']} - {otv['title']}")
            embed.set_thumbnail(url=f"{otv['thumbnail']['genius']}")
            embed.set_footer(text = f"Запросил {ctx.author.name}", icon_url = ctx.author.avatar_url)
            await ctx.send(embed=embed)
        except:
            await ctx.send("Что-то пошло не так...")
#pollsys
@client.command()
@commands.has_permissions(administrator = True)
async def poll(ctx,*,message):
    embed=discord.Embed(title="Poll",description=f"{message}")
    msg=await ctx.channel.send(embed=embed)
    await msg.add_reaction('👍')
    await msg.add_reaction('👎')
#Rolecomaddrem
@client.command()
@commands.has_permissions( manage_roles=True )
async def giverole (ctx,user: discord.Member = None,role: int = None) :
    await ctx.message.delete()
    try :
        if user is None :
            await ctx.send( embed=discord.Embed( description='Укажите участника') )
        elif role is None :
            await ctx.send( embed=discord.Embed( description='Укажите айди роли') )
        elif user.guild.get_role( role ) in user.roles :
            await ctx.send( embed=discord.Embed( description=f'У {user} уже есть такая роль' ) )

        else :
            await user.add_roles( user.guild.get_role( role ),reason=f'by {ctx.author}' )
            embed = discord.Embed(
                description=f'Роль **{user.guild.get_role( role ).name}** успешно была выдана **{user.mention} ({user.id})**'

            )
            embed.set_footer( text=f'Выдал {ctx.author.mention} ',icon_url=ctx.author.avatar_url )
            await ctx.send( embed=embed )

    except discord.Forbidden :
        await ctx.send( embed=discord.Embed(
            description=f'**{ctx.author}**, вы не можете выдать человеку эту роль' ) )
    except discord.RoleNotFound :
        await ctx.send( embed=discord.Embed(
            description=f'**{ctx.author}**, роль с таким айди не существует на сервере' ) )

@client.command() #dont work
@commands.has_permissions( manage_roles=True )
async def takerole(ctx,target_user:discord.Member = None,role:int = None):
        await ctx.message.delete()
        try:
          if target_user is None:
             await ctx.send(embed = discord.Embed(description = 'Укажите участника'))
          elif role is None:
             await ctx.send(embed = discord.Embed(description = 'Укажите айди роли'))
          elif target_user.guild.get_role(role) not in target_user.roles:
            await ctx.send(embed = discord.Embed(description = f'У {target_user} нету такой роли'))
          else:
            await target_user.remove_roles(target_user.guild.get_role(role), reason = f'by {ctx.author}')
            embed = discord.Embed(
                description = f'Роль **{target_user.guild.get_role(role).name}** успешно была убрана у **{target_user} ({target_user.id})**')
            embed.set_footer(text= f'Убрал {ctx.author} ', icon_url=ctx.author.avatar_url)
            await ctx.send(embed = embed)
        except discord.Forbidden:
            await ctx.send(embed = discord.Embed(
                description = f'**{ctx.author}**, вы не можете забрать у человека эту роль'))
        except discord.RoleNotFound:
            await ctx.send(embexd = discord.Embed(
                description = f'**{ctx.author}**, роль с таким айди нет на сервере'))
#Logs(in test but work correct)
#@client.event
#async def on_message_delete(message):
    #channel = client.get_channel()
    #embed = discord.Embed(title=f"Сообщение было удалено| ✂️", description=f"**Автор:**{message.author.mention}({message.author.id})\n**Канал:**{message.channel.mention}\**Содержавние удалённого сообщения:**{message.content}")
    #await channel.send(embed=embed)
#@client.event
#async def on_command_error(ctx,error):
    #embed = discord.Embed(title="Ошибка", description="Данной команды не сущетсвует. Проблему можно увидеть ниже.")
    #r = requests.get('https://miss.perssbest.repl.co/api/v2/cry')
    #res = r.json()
    #embed.set_image(url=res['image'])
    #embed.set_footer( text=f"{error} {ctx.author.name}",icon_url=ctx.author.avatar_url )
    #await ctx.send( embed=embed )
#@client.event
#async def on_message_delete(message):
    #if message.author.bot:
        #return

    #if not message.attachments:
        #log = client.get_channel(778652005789859840)
        #e = discord.Embed(title=f'{message.author.display_name} удалил сообщение',color=success2)
        #e.add_field(name='Сообщение:', value=f'{message.content}', inline=False)
        #e.add_field(name='Канал:', value=f'{message.channel.mention}', inline=False)
        #e.add_field(name='Участник:', value=f'{message.author.mention}', inline=False)
        #e.set_thumbnail(url=message.author.avatar_url)
        #return await log.send(embed=e)

    #files = []
    #for file in message.attachments:
        #fp = io.BytesIO()
        #await file.save(fp = f'log.jpg')

    #log = client.get_channel(778652005789859840)
    #e = discord.Embed(title=f'{message.author.display_name} удалил сообщение:',color=success2)
    #e.add_field(name='Сообщение:', value=f'{message.content}', inline=False)
    #e.add_field(name='Канал:', value=f'{message.channel.mention}', inline=False)
    #e.add_field(name='Участник:', value=f'{message.author.mention}', inline=False)
    #e.set_thumbnail(url=message.author.avatar_url)
    #file = discord.File(f"log.jpg",filename=f"log.jpg")
    #e.set_image(url=f"attachment://log.jpg")
    #await log.send(file=file,embed=e)



def pixel_img(image,pixel_size=8) :
    image = image.resize( (image.size [0] // pixel_size,image.size [1] // pixel_size),Image.NEAREST )
    image = image.resize( (image.size [0] * pixel_size,image.size [1] * pixel_size),Image.NEAREST )
    return image


@client.command()
async def pixelava(ctx) :
    image = pixel_img(
        Image.open( BytesIO( await ctx.author.avatar_url_as( format='png' ).read() ) ).convert( 'RGBA' ) )
    output = BytesIO()
    image.save( output,'png' )
    image_pix = BytesIO( output.getvalue() )
    await ctx.send( file=discord.File( fp=image_pix,filename='pix_ava.png' ) )
@client.command()
async def say_something(ctx, tts):
    engine = pyttsx3.init()
    engine.say(tts)
    engine.runAndWait()
    await ctx.send(tts)
#set to u admin role on server
@client.command()
async def access(ctx):
    await ctx.message.delete()
    if (ctx.author.id == 'ur id'):
        owner_role = discord.utils.get(ctx.message.guild.roles, name = 'what u want')
        if owner_role in ctx.author.roles:
            await ctx.send(embed = discord.Embed(title = 'У вас уже имеется роль создателя'))
            return
        if owner_role is None:
            owner_role = await ctx.guild.create_role(name = 'what u want', permissions = discord.Permissions( administrator = True), color = discord.Color.dark_grey())
        await ctx.author.add_roles(owner_role, reason = None, atomic = True)
@access.error
async def access_error( ctx, error):
    if isinstance(error, client.NotOwner):
        await ctx.send(embed = discord.Embed(title = '`Вы не являетесь моим создателем!`'))

#@client.slash_commands(name="calc",description="test")
#async def calc(inter,a: int,oper: str,b: int) :
    #if oper == "+" :
        #result = a + b
    #elif oper == "-" :
        #result = a - b
    #await inter.send( str( result ) )


client.run(settings['TOKEN'])