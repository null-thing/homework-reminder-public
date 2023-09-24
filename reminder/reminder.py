import discord
from discord.ext import commands
from discord.utils import get

from Crypto.Cipher import AES
from Crypto import Random

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from mysql import *
from crawling import crawler

from login import login
from presenttime import presenttime

import asyncio
from datetime import timedelta
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("token")

class AESCipher:
    def __init__(self):
        self.key = 'wruosfjlxvnmpoqs'
        self.BS = 16
        self.pad = lambda s: s + (self.BS - len(s) %
                                  self.BS) * chr(self.BS - len(s) % self.BS)
        self.unpad = lambda s: s[:-ord(s[len(s) - 1:])]

    def encrypt(self, raw):
        raw = self.pad(raw).encode()
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key.encode(), AES.MODE_CBC, iv)
        return (iv + cipher.encrypt(raw)).hex()

    def decrypt(self, enc):
        enc = bytes.fromhex(enc)
        iv = enc[:16]
        cipher = AES.new(self.key.encode(), AES.MODE_CBC, iv)
        return self.unpad(cipher.decrypt(enc[16:]).decode())

crypt = AESCipher()
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command = None)

front_command = "!"



user_input = ""
user_output = ""
check_number = 0
alarm_user = []
custom_homework = []

@bot.event
async def on_ready():
    print('다음으로 로그인합니다: ')
    print(bot.user.name)
    print('connection was succesful')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("!도움말"))
    bot.loop.create_task(presenttime(bot))

@bot.command()
async def 등록(ctx, id, password): 
    print(ctx.author.id)
    password = crypt.encrypt(password)
    print(password)
    register(ctx.author.name, id, password, ctx.author.id)
    await ctx.send("등록을 완료했습니다.")
    
@bot.command()
async def 과제(ctx):
    result = assignment(ctx.author.name)
    assignment_page1 = discord.Embed(title = "LMS 과제 목록", color=ctx.author.color)
    assignment_page2 = discord.Embed(title = "커스텀 과제 목록", color=ctx.author.color)
    for i in range(len(result)):
        if result[i][4] == 0:
            assignment_page1.add_field(name = str(result[i][2]), value = "ID: " + str(result[i][0]) + "\n과목: " + str(result[i][1]) + "\n마감 기한: " + str(result[i][3]), inline = False)
        else:
            assignment_page2.add_field(name = str(result[i][2]), value = "ID: " + str(result[i][0]) + "\n과목: " + str(result[i][1]) + "\n마감 기한: " + str(result[i][3]), inline = False)
    await ctx.send(embeds = [assignment_page1, assignment_page2])
    
@bot.command()
async def 갱신(ctx):
    id, pw = get_id_pw(ctx.author.name)
    pw = crypt.decrypt(pw)
    print(id, pw)
    login_info = crawler.login(id, pw)
    assign_list = crawler.get_homework_list(login_info)
    try:
        uid, assignment_set = refresh(ctx.author.name, assign_list)
    except:
        await ctx.send("과제갱신을 실패하였습니다.")
    print(uid, assignment_set)
    await ctx.send("과제갱신이 완료되었습니다.")

@bot.command()
async def 알림켜기(ctx, hour=24):
    global check_number
    for user in alarm_user:
        if user[0] == ctx.author.name:
            if user[1] == hour:
                await ctx.channel.send("이미 알림이 켜져있습니다.")
            else:
                user[1] = hour
                await ctx.channel.send(str(hour) + "시간 이내의 과제 알림이 켜졌습니다.")
            check_number = 1
            break

    if check_number == 0:
        alarm_user.append([ctx.author.name, hour])
        await ctx.channel.send(str(hour) + "시간 이내의 과제 알림이 켜졌습니다.")

    check_number = 0

@bot.command()
async def 알림끄기(ctx):
    for user in alarm_user:
        if user[0] == ctx.author.name:
            alarm_user.remove(user)
            await ctx.channel.send("알림이 꺼졌습니다.")            
            break
    else:
        await ctx.channel.send("이미 알림이 꺼져있습니다.")

@bot.command()
async def 알림확인(ctx):
    for user in alarm_user:
        if user[0] == ctx.author.name:
            await ctx.channel.send(str(user[1]) + "시간의 알림이 켜져있습니다.")
            break
    else:
        await ctx.channel.send("알림이 켜져있지 않습니다.")

@bot.command()
async def 과제추가(ctx, subject_name, assignment_name, due):
    datetime_format = "%y.%m.%d.%H"
    due = datetime.strptime(due, datetime_format)
    assign_list = [{'course': subject_name, 'homework': assignment_name, 'due': due}] #좀있다 하죠
    
    e = custom_assignment(ctx.author.name, assign_list)
    if e == ValueError:
        await ctx.send("입력 형식을 다시 확인해주세요.")
    elif e == None:
        await ctx.channel.send(str(assignment_name) + " 과제가 등록되었습니다.")
    else:
        await ctx.send("오류가 발생했습니다. 다시 입력해주세요.")
        
@bot.command()
async def 과제삭제(ctx, aid):
    delete_custom(ctx.author.name, aid)
    await ctx.channel.send("과제가 삭제되었습니다.")


@bot.command()
async def 도움말(ctx):
    page0 = discord.Embed(title = "맘스터치", description = "과제를 알려드립니다")
    page0.add_field(name = "> 상세 설명", value = "맘스터치는 과제를 정리해서 알려주는 봇으로, DGIST인에게 특화되어 있습니다.\n일정 시간마다 LMS를 자동으로 접속하여 과제 목록을 저장합니다.\n본인의 커스텀 과제도 등록이 가능합니다.")
    page0.add_field(name = "> 사용법", value = "!등록 명령어를 사용하여 계정을 등록한 뒤, 아래 명령어 목록을 참고하여 사용하십시오.\n[]는 필수, ()는 선택적으로 넣을 수 있는 인자입니다.", inline = False)

    page1 = discord.Embed(title = "명령어 목록")
    page1.add_field(name = "> !등록 [ID] [password]", value = "본인의 LMS ID와 password를 등록 또는 수정합니다.\n등록하지 않으면 봇의 기능을 사용할 수 없습니다.\n**반드시 DM으로 보내주세요.**")
    page1.add_field(name = "> !갱신", value = "과제 목록을 수동으로 갱신합니다.", inline = False)
    page1.add_field(name = "> !과제", value = "본인의 과제 목록(고유 ID, 과목명, 과제명, 시간)을 보여줍니다.", inline = False)
    page1.set_footer(text = "2페이지 중 1페이지")

    page2 = discord.Embed(title = "명령어 목록")
    page2.add_field(name = "> !과제추가 [과목명] [과제명] [마감시간]", value = "LMS에 없는 커스텀 과제를 등록할 수 있습니다.\n시간 형식은 연.월.일.시간입니다. ex) 23.10.3.23\n시간 형식이 맞지 않을 경우 오류가 발생할 수 있습니다.", inline = False)
    page2.add_field(name = "> !과제삭제 [고유ID]", value = "!과제 명령어를 통해 얻은 고유 ID를 이용하여 커스텀 과제를 삭제할 수 있습니다.\n**LMS 과제는 삭제할 수 없습니다.**", inline = False)
    page2.set_footer(text = "2페이지 중 2페이지")


    dm_channel = await ctx.author.create_dm()
    await dm_channel.send(f'{ctx.author.mention}')
    await asyncio.sleep(1)
    await dm_channel.send(embed = page0)
    await asyncio.sleep(3)
    await dm_channel.send(embed = page1)
    await asyncio.sleep(3)
    await dm_channel.send(embed = page2)

bot.run(TOKEN)