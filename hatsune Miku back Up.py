#import區
import discord
from discord.ext import commands, tasks
from youtube_dl import utils,YoutubeDL
from time import ctime,time
from random import randint,choices,choice
from asyncio import get_event_loop,sleep
import urllib.request as req
from bs4 import BeautifulSoup
from os import  remove,walk
from PIL import Image
import re
import json

intents=discord.Intents.all()


utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {'options': '-vn'}

ytdl = YoutubeDL(ytdl_format_options)

#全域變數區
status = "Happy new year"
queue = []
loop = False
is_playing = False
voice_lentage=0
time_start=0
value=1.0
time_end=0
vocal_hello=["D:/聲音樣本/hello2.wav","D:/聲音樣本/hello4.wav"]
vocal_i_got_this=["D:/聲音樣本/i got this2.wav","D:/聲音樣本/i got this.wav","D:/聲音樣本/i got this3.wav"]
vocal_Congratulations=["D:/聲音樣本/恭喜1.wav","D:/聲音樣本/恭喜.wav"]
voice_channel = 0
sorted = ""
player = ""
pausing = False
already_play = 0
pick = False
amount = 0

#bot設定區
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data):
        global value

        super().__init__(source,value)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

def is_connected(ctx):
    voice_client = ctx.message.guild.voice_client
    return voice_client and voice_client.is_connected()

client = commands.Bot(command_prefix=';;',intents=intents)

@client.event
async def on_ready():
    try:
        change_status.start()
        get_rank.start()
        tine_to_do.start()
        new_chart_announcement.start()
        print('Bot is online!')
    except:
        print('Bot is online!')

@tasks.loop(seconds=20)
async def change_status():
    await client.change_presence(activity=discord.Game(status))

@tasks.loop(seconds=30)
async def new_chart_announcement():
    url = "https://servers.purplepalette.net/levels/list"
    request = req.Request(url, headers=
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
    })
    with req.urlopen(request) as response:
        data = response.read().decode("utf-8")
    root = BeautifulSoup(data, "html.parser")
    outFile = open("D:/Discordbot/chart.txt", "r", encoding="utf-8")
    text = outFile.read()
    outFile.close()
    root = root.prettify()
    str1 = root[root.find("\"useSkin\""):]
    str2 = root[root.find('mp3"},"data":'):]

    round_count = len(str1) - len(str2)
    sliced_root = "{"
    for i in range(round_count):
        sliced_root = sliced_root + str1[i]
    sliced_root = sliced_root + "\"}}"
    sliced_root = sliced_root.replace("true", "True")
    data = eval(sliced_root)
    if sliced_root != text:
        embed = discord.Embed(title="新譜面通知", url="https://potato.purplepalette.net/", color=0x0dc6d3)
        embed.set_thumbnail(url=f"https://servers.purplepalette.net{data['cover']['url']}")
        embed.add_field(name="譜面", value=data['title'], inline=False)
        embed.add_field(name="音樂作者", value=data['artists'], inline=False)
        embed.add_field(name="譜師", value=data['author'], inline=False)
        channel = client.get_channel(913080900114341959)
        await channel.send(embed=embed)
        outFile = open("D:/Discordbot/chart.txt", "w", encoding="utf-8")
        outFile.write(sliced_root)
        outFile.close()

#排名查詢區
@tasks.loop(seconds=600)
async def get_rank():
    global sorted
    sorted=""
    url = "https://api.sekai.best/event/live"
    request = req.Request(url, headers=
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
    })
    with req.urlopen(request) as response:
        data = response.read().decode("utf-8")
    root = BeautifulSoup(data, "html.parser")
    slice_rooted = []
    slice_root = root.prettify()
    slice_root = slice_root[45:]
    while (True):
        if '}' not in slice_root:
            break
        else:
            str1 = slice_root[:slice_root.find(',"userCard"')]
            str1 = str1 + "}"
            slice_rooted.append(str1)
            str2 = slice_root[slice_root.find('},{'):]
            slice_root = str2
            slice_root = slice_root[2:]
    for i in range(len(slice_rooted)):
        data = str(slice_rooted[i])
        try:
            data = eval(data)
            c=f'Rank:{data["rank"]:<7}player:{data["userName"]:<15}\nscore now:{data["score"]:<10}\n\n'
            sorted=sorted+c
        except:
            continue
    time_now = ctime()
    time_now = time_now.split()
    sorted=sorted+f"Update at{time_now[2]} {time_now[3]}"

@client.command(name="rank",help=("顯示目前本期project sekai的活動排名"))
async def rank(ctx):
    global sorted
    await ctx.send(f"```{sorted}```")



@tasks.loop(seconds=1)
async def tine_to_do():
    time_now = ctime()
    time_now= time_now.split()
    time_now1 = time_now[3]
    if '23:00:0'in time_now1:
        channel = client.get_channel(844419400589115403)
        await channel.send('歐逆醬該睡了喔')
        await channel.send('<:miku_sleep:852886846119608340>')
        channel = client.get_channel(839784321191772251)
        await channel.send('歐逆醬該睡了喔')
        await channel.send('<:miku_sleep:852886846119608340>')
        channel = client.get_channel(913080900114341959)
        await channel.send('歐逆醬該睡了喔')
        await channel.send('<:miku_sleep:852886846119608340>')
        await sleep(10)
    if '07:00:0'in time_now1:
        channel = client.get_channel(844419400589115403)
        await channel.send('早安歐逆醬')
        await channel.send('<:good_morning:852914114233761832>')
        channel = client.get_channel(839784321191772251)
        await channel.send('早安歐逆醬')
        await channel.send('<:good_morning:852914114233761832>')
        channel = client.get_channel(913080900114341959)
        await channel.send('早安歐逆醬')
        await channel.send('<:good_morning:852914114233761832>')
        await sleep(10)

#來賓好
@client.event
async def on_member_join(member):
    print(member)
    print(type(member))
    await member.send(f'你好{member.mention}!準備好和Miku玩了嗎? 歐逆醬請用`;;help`查詢怎麼玩弄我')

#聊天觸發
@client.event
async def on_message(msg):
    global pick
    global amount

    if ";" in msg.content:
        pass
    else:
        if pick != True and msg.channel.id==913080900114341959:
            give = randint(1, 20)
            if give == 10:
                amount = randint(1, 20)
                await msg.channel.send(f"出現了{amount}顆<:4star:828160732318138389> 請使用;;pick來取得")
                pick = True
        line = msg.content
        line_split = line.split()
        if client.user.mentioned_in(msg) and not msg.author.bot:
            await msg.channel.send("<:ping:832925542768443402><:kanade_ping:837493288504262707><a:FKping:852459756039962634><:snow_ping:852742564582129675>")

        if "hi" in line_split and not msg.author.bot:
            await msg.channel.send(msg.author.mention)

        if "佬" in msg.content and not msg.author.bot:
            await msg.channel.send('<a:emoji_32:836411269237702656>')

        if "課長" in msg.content and not msg.author.bot:
            await msg.channel.send(
                '<:giftcard:828158809808699402><a:burndiamond:853952516765253652><a:emoji_32:836411269237702656>')

        if "暴死" in msg.content and not msg.author.bot:
            await msg.channel.send('<a:eat_diamond:852885172583923762>')
    await client.process_commands(msg)

#彩球使用區
@client.command(name="pick")
async def pick(ctx):
    global pick
    if pick!=False:
        pick = False
        with open('pick.json', 'r', encoding='utf-8') as f:
            pick_deta = json.load(f)

        if str(ctx.author.id) not in pick_deta:
            pick_deta[str(ctx.author.id)]=amount
        else:
            pick_deta[str(ctx.author.id)]=amount+pick_deta[str(ctx.author.id)]
        await ctx.send(f"你已獲得{amount}顆<:4star:828160732318138389>現在你已獲得\n總共擁有{pick_deta[str(ctx.author.id)]}顆")
        with open('pick.json', 'w', encoding='utf-8') as f:
            json.dump(pick_deta, f)


@client.command(name="give", help="轉移你的彩球")
async def give(ctx, id, amount):
    with open('pick.json', 'r', encoding='utf-8') as f:
        pick_deta = json.load(f)
    try:
        if pick_deta[str(ctx.author.id)] < int(amount):
            await ctx.send(f"<@{ctx.author.id}>你的<:4star:828160732318138389>不足")
            return 0
        if int(amount) < 0:
            await ctx.send(f"<@{ctx.author.id}>還想利用bug洗數量阿")
            return 0
        else:
            to_give_user_id = re.findall(r"\d+\.?\d*", id)
            to_give_user_id = str(to_give_user_id[0])
            if to_give_user_id not in pick_deta:
                pick_deta[to_give_user_id] = 0

            pick_deta[str(ctx.author.id)] -= int(amount)
            pick_deta[to_give_user_id] += int(amount)

            await ctx.send(
                f"<@{ctx.author.id}> 你已給 {id} {amount}顆<:4star:828160732318138389>\n 現在你剩{pick_deta[str(ctx.author.id)]}顆")

            with open('pick.json', 'w', encoding='utf-8') as f:
                json.dump(pick_deta, f)
    except:
        await ctx.send(f"<@{ctx.author.id}>你目前沒有<:4star:828160732318138389>")


#語音+點歌區
@client.event
async def on_voice_state_update(member, before, after):
    global queue
    global voice_channel
    global is_playing
    global pausing
    global already_play
    global loop
    vc = before.channel

    if vc is not None and after.channel is None and len(vc.members) == 1:
        await voice_channel.disconnect()
        queue = []
        is_playing=False
        pausing=False
        already_play=0
        loop=False

@client.command(name='hello', help='miku安安')
async def hello(ctx):
    if ctx.message.author.voice:
        voice = ctx.voice_client
        voice.play(discord.FFmpegPCMAudio(choice(vocal_hello)),after=lambda e: print('Player error: %s' % e) if e else None)
    else:
        await ctx.send('歐逆醬安安')



@client.command(name='join', help='讓miku加入語音頻道')
async def join(ctx):
    global voice_channel
    if not ctx.message.author.voice:
        await ctx.send("你沒有加入語音頻道")
        return
    else:
        voice_channel = ctx.message.author.voice.channel

    await voice_channel.connect()
    server = ctx.message.guild
    voice_channel = server.voice_client
    voice = ctx.voice_client
    voice.play(discord.FFmpegPCMAudio(choice(vocal_hello)), after=lambda e: print('Player error: %s' % e) if e else None)


@client.command(name='leave', help='讓miku停止唱歌並離開語音頻道')
async def leave(ctx):
    global queue

    voice_channel = ctx.message.guild.voice_client
    await voice_channel.disconnect()
    queue=[]


@client.command(name='loop', help='讓Miku一直重唱')
async def loop_(ctx):
    global loop

    if loop:
        await ctx.send('重唱模式已關閉')
        loop = False

    else:
        await ctx.send('重唱模式已開啟')
        loop = True



@client.command(name='play', help='讓Miku唱歌')
async def play(ctx):
    global queue
    global voice_channel
    global time_start
    global voice_lentage
    global is_playing
    global time_end
    global player
    global already_play

    if is_playing==True:
        pass

    else:
        if not ctx.message.author.voice:
            await ctx.send("你不在語音頻道內")
            return
        else:
            voice_channel = ctx.message.author.voice.channel

        try:
            await voice_channel.connect()
        except:
            pass

        server = ctx.message.guild
        voice_channel = server.voice_client

        if len(queue) > 0:
            while (True):
                player=""
                player = await YTDLSource.from_url(queue[0], loop=client.loop)
                with YoutubeDL(ytdl_format_options) as ydl:
                    dictMeta = ydl.extract_info(f"{queue[0]}", download=False)
                try:
                    voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
                    is_playing=True
                    voice_lentage=dictMeta['duration']
                except:
                    continue
                await ctx.send(f'Miku正在唱:{player.title}')
                already_play = 0
                time_start = time()
                while ((time_end - time_start <= voice_lentage - already_play) and is_playing == True):
                    await sleep(1)
                    time_end = time()
                    while (pausing == True):
                        await sleep(1)
                if loop == False:
                    try:
                        del (queue[0])
                    except IndexError:
                        pass

                if (len(queue) == 0 and loop == False) or is_playing==False:
                    is_playing = False
                    break
        else:
            await ctx.send("Miku還不知道主人想聽什麼,用\";;queue\"讓我知道")


@client.command(nave="volume",help="調整音量")
async def volume(ctx,volume):
    global value
    global voice_channel
    volume = float(volume)
    try:
        voice_channel.source = discord.PCMVolumeTransformer(voice_channel.source, 1 / value)
        voice_channel.source = discord.PCMVolumeTransformer(voice_channel.source, 1 * volume)
    except:
        pass
    value = volume
    await ctx.send(f"目前音量為{value}")


@client.command(name="schedule",help="Let you know where Miku is singing")
async def schedule(ctx):
    global queue
    global voice_lentage
    global time_end
    global time_start

    lentage_min=voice_lentage//60
    lentage_sec=voice_lentage%60
    time_sch_sec=(time_end-time_start)%60
    time_sch_min=(time_end-time_start)//60
    if lentage_sec<10:
        await ctx.send(f"schedule:  {int(time_sch_min)}:{int(time_sch_sec)}/{int(lentage_min)}:0{int(lentage_sec)}")
    elif lentage_sec<10 and time_sch_sec<10:
        await ctx.send(f"schedule:  {int(time_sch_min)}:0{int(time_sch_sec)}/{int(lentage_min)}:0{int(lentage_sec)}")
    elif time_sch_sec<10:
        await ctx.send(f"schedule:  {int(time_sch_min)}:0{int(time_sch_sec)}/{int(lentage_min)}:{int(lentage_sec)}")
    else:
        await ctx.send(f"schedule:  {int(time_sch_min)}:{int(time_sch_sec)}/{int(lentage_min)}:{int(lentage_sec)}")



@client.command(name="cancel",help="刪除你點的歌")
async def cancel(ctx,url):
    global queue
    global is_playing

    if len(queue)<=1 and is_playing==True:
        await ctx.send("你無法刪除正在唱的歌")
    else:
        if url in queue:
            try:
                queue.remove(url)
                await ctx.send(f"{url} 已成功刪除")
            except:
                pass
        else:
            await ctx.send(f"{url} 不再清單中，請使用```view```來檢視你點過的歌")


@client.command(name='state', help='查看Miku目前的狀態')
async def state(ctx):
  global queue
  global loop
  global value

  if len(queue)==0:
      await ctx.send(f"目前還沒人點歌\n重撥模式:{loop}\n目前音量{value}")
  else:
      await ctx.send(f"目前還有{len(queue)}首歌\n重撥模式:{loop}\n目前音量{value}")


@client.command(name='pause', help='讓miku先不要唱歌')
async def pause(ctx):
    global voice_channel
    global pauseing
    global time_start
    global time_end
    global already_play

    voice_channel.pause()
    pauseing=True
    already_play=time_end-time_start

@client.command(name='keep_playing', help='讓miku繼續唱歌')
async def keep_playing(ctx):
    global voice_channel
    global pausing

    voice_channel.resume()
    pausing=False


@client.command(name='resume', help='Let miku sing again')
async def resume(ctx):
    global queue
    global is_playing
    global voice_lentage
    global time_start
    global voice_channel
    global already_play
    global pausing


    voice_channel.stop()
    sleep(0.5)
    already_play = 0
    pausing = False
    player = await YTDLSource.from_url(queue[0], loop=client.loop)

    with YoutubeDL(ytdl_format_options) as ydl:
        dictMeta = ydl.extract_info(f"{queue[0]}", download=False)
    try:
        voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        is_playing = True
        voice_lentage = dictMeta['duration']
        time_start = time()
    except:
        pass


@client.command(name='stop', help='Let Miku stop singing!')
async def stop(ctx):
    global queue
    global voice_channel
    global is_playing
    global pausing
    del (queue[0])

    is_playing=False
    pausing=False
    voice_channel.stop()
    await sleep(0.5)
    voice = ctx.voice_client
    voice.play(discord.FFmpegPCMAudio(choice(vocal_i_got_this)),after=lambda e: print('Player error: %s' % e) if e else None)


@client.command(name='queue',help='讓Miku知道主人想聽什麼')
async def queue_(ctx, url):
    global queue
    if "https://www.yout" not in url:
        await ctx.send("此不為youtube網址")

    else:
        queue.append(url)
        await ctx.send(f'`{url}`我已經收到主人需求!')
        await YTDLSource.from_url(url, loop=client.loop)
        if ctx.message.author.voice:
            voice = ctx.voice_client
            try:

                voice.play(discord.FFmpegPCMAudio(choice(vocal_i_got_this)),after=lambda e: print('Player error: %s' % e) if e else None)
            except:
                pass


@client.command(name='view', help='讓主人知道miku還有多少歌還沒唱完')
async def view(ctx):
    global queue
    global player
    play_list=""
    if len(queue)==0:
        await ctx.send('主人還沒點歌喔')
    else:
        play_list=play_list+f'Miku正在唱:{player.title}\n'
        if len(queue)>1:
            for i in range(len(queue)):
                if i>=1:
                    wait_to_play = await YTDLSource.from_url(queue[i], loop=client.loop)
                    try:
                        play_list=play_list+f'Miku還要唱:{wait_to_play.title}\n'
                    except:
                        break

        await ctx.send(f'```{play_list}```')



@client.command(name="skip",help="跳過這首歌")
async def skip(ctx):
    global queue
    global time_start
    global voice_lentage
    global player
    global pausing
    global already_play
    del(queue[0])

    voice_channel.stop()

    pausing=False
    already_play=0
    player = await YTDLSource.from_url(queue[0], loop=client.loop)
    with YoutubeDL(ytdl_format_options) as ydl:
        dictMeta = ydl.extract_info(f"{queue[0]}", download=False)
        voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    await ctx.send(f'Miku正在唱:{player.title}')
    time_start = time()
    voice_lentage=dictMeta['duration']

#抽卡區
@client.command(name="抽卡",help="讓miku決定你是非洲人還是歐洲人")
async def 抽卡(ctx):
    global voice_channel
    can_get = ["4star", "3star", "2star"]

    if not ctx.message.author.voice:
        pass
    else:
        voice_channel = ctx.message.author.voice.channel
    try:
        await voice_channel.connect()
    except:
        pass
    server = ctx.message.guild
    voice_channel = server.voice_client
    star = ((choices(can_get, weights=[3, 85, 885])))

    image_names = list(walk(f"D:/Discordbot/{star[0]}/"))[0][2]
    selected_images = choices(image_names)
    file = discord.File(f"D:/Discordbot/{star[0]}/{selected_images[0]}")
    await ctx.send(f"<@{ctx.author.id}>")
    await ctx.send(file=file)
    if star == ["4star"]:
        try:
            voice = ctx.voice_client
            voice.play(discord.FFmpegPCMAudio(choice(vocal_Congratulations)),
                       after=lambda e: print('Player error: %s' % e) if e else None)
        except:
            pass



@client.command(name='十抽', help='讓miku抽十次看你是真歐洲還是真非洲')

async def 十抽(ctx):
    global voice_channel
    can_get = ["4star", "3star", "2star"]
    get=[]

    if not ctx.message.author.voice:
        pass
    else:
        voice_channel = ctx.message.author.voice.channel

    try:
        await voice_channel.connect()
    except:
        pass
    server = ctx.message.guild
    voice_channel = server.voice_client
    gtl=(choices(can_get, weights=[3, 8.5, 88.5],k=10))

    if "4star"and"3star"not in gtl:
        replace=randint(0,9)
        can_get = ["4star", "3star"]
        gtl[replace]=(((choices(can_get, weights=[3, 97 ]))))[0]
    if "4star" in gtl:
        message=await ctx.send(f"<@{ctx.author.id}>\n<:4star:828160732318138389> ")
    else:
        message=await ctx.send(f"<@{ctx.author.id}>\n<:3star:828160732419063818> ")
    for i in range(10):
        card = gtl[i]
        image_names = list(walk(f"D:/Discordbot/{card}/"))[0][2]
        selected_images = choices(image_names)
        selected_images=Image.open(f"D:/Discordbot/{card}/{selected_images[0]}")
        get.append(selected_images)


    target = Image.new('RGB', (128 * 5, 128 * 2))
    for row in range(2):
        for col in range(5):
            target.paste(get[5*row+col], (0 + 128*col, 0 + 128*row))
    message_id=str(ctx)
    message_id = message_id[message_id.find("0x"):]
    message_id=message_id[:-1]
    target.save(f"D:/Discordbot/result/{message_id}result.png", quality=100)
    embed = discord.Embed(title="You got:", color=0x03cafc)
    embed.add_field(name="4star", value=f"{gtl.count('4star')}", inline=True)
    embed.add_field(name="3star", value=f"{gtl.count('3star')}", inline=True)
    embed.add_field(name="2star", value=f"{gtl.count('2star')}", inline=True)
    file = discord.File(f"D:/Discordbot/result/{message_id}result.png")
    embed.set_image(url="attachment://image.png")
    await message.edit(embed=embed)
    await ctx.send(file=file)
    if "4star" in gtl:
        try:
            voice = ctx.voice_client
            voice.play(discord.FFmpegPCMAudio(choice(vocal_Congratulations)),after=lambda e: print('Player error: %s' % e) if e else None)
        except:
            pass
    remove(f"D:/Discordbot/result/{message_id}result.png")

@client.command()
async def 歐洲人(ctx):
    gtl= ["<:4star:828160732318138389>"*10]
    await ctx.send(f"<@{ctx.author.id}>\n{gtl}")


#雜項區
@client.command(name='developer', help='讓你知道Miku的開發者')
async def credits(ctx):
    await ctx.send('Made by 柑橘Wang\nDebug by 美味的小圓,Python Taiwan,SHELTER ZONE\nVocal by 初音ミク')

@client.command(name='ping', help='看你家網路有多爛(沒')
async def ping(ctx):
    await ctx.send(f'你的網路延遲是: {round(client.latency * 1000)}ms')


#管理員指令區
@client.command(name="mute")
@commands.has_permissions(manage_messages=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name="Muted")

    if not mutedRole:
        mutedRole = await guild.create_role(name="Muted")

        for channel in guild.channels:
            await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=False , view_channel=False)
    embed = discord.Embed(title="muted", description=f"{member.mention} was muted ", colour=discord.Colour.light_gray())
    embed.add_field(name="reason:", value=reason, inline=False)
    await ctx.send(embed=embed)
    await member.add_roles(mutedRole, reason=reason)
    await member.send(f" you have been muted from: {guild.name} reason: {reason}")



tokenfile = open("token.txt","r")
token=tokenfile.read()
token=eval(token)
TOKEN=token["ch"]
tokenfile.close()
client.run(TOKEN)
