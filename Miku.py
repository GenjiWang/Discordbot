import discord
from discord.ext import commands, tasks
from youtube_dl import  utils,YoutubeDL
from time import ctime,time
from random import randint,choices,choice
from asyncio import get_event_loop,sleep
import urllib.request as req
from bs4 import BeautifulSoup
from googletrans import Translator
from os import walk, remove
from PIL import Image
from numba import jit

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
status = "あけましておめでとう"
queue = []
loop = False
is_playing=False
voice_lentage=0
time_start=0
value=1.0
time_end=0
vocal_hello=["D:/聲音樣本/hello2.wav","D:/聲音樣本/hello4.wav"]
vocal_i_got_this=["D:/聲音樣本/i got this2.wav","D:/聲音樣本/i got this.wav","D:/聲音樣本/i got this3.wav"]
vocal_Congratulations=["D:/聲音樣本/恭喜1.wav","D:/聲音樣本/恭喜.wav"]
voice_channel=0
sorted=""
player=""
pausing=False
already_play=0
state_count=0

class YTDLSource(discord.PCMVolumeTransformer):
    global value
    def __init__(self, source, *, data):
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
    outFile = open("D:/Discordbot/text.txt", "r", encoding="utf-8")
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
        embed = discord.Embed(title="New chart announcement ", url="https://potato.purplepalette.net/", color=0x0dc6d3)
        embed.set_thumbnail(url=f"https://servers.purplepalette.net{data['cover']['url']}")
        embed.add_field(name="New chart", value=data['title'], inline=False)
        embed.add_field(name="Artists", value=data['artists'], inline=False)
        embed.add_field(name="Author", value=data['author'], inline=False)
        channel = client.get_channel(855263100076425256)
        await channel.send(embed=embed)
        outFile = open("D:/Discordbot/text.txt", "w", encoding="utf-8")
        outFile.write(sliced_root)
        outFile.close()


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


@tasks.loop(seconds=1)
async def tine_to_do():
    time_now =ctime()
    time_now= time_now.split()
    time_now = time_now[3]
    if '23:00:0'in time_now:
        channel = client.get_channel(826086788291624990)
        await channel.send('おやすみ')
        await channel.send('<:miku_sleep:852886846119608340>')
        await sleep(10)
    if '07:00:0'in time_now:
        channel = client.get_channel(826086788291624990)
        await channel.send('おはよう')
        await channel.send('<:good_morning:852914114233761832>')
        await sleep(10)


@client.event
async def on_ready():
    try:
        change_status.start()
        get_rank.start()
        tine_to_do.start()
        new_chart_announcement.start()
        print('Bot is online!')
    except:
        pass


@client.event
async def on_voice_state_update(member, before, after):
    global queue
    global voice_channel
    global is_playing
    global pausing
    global already_play

    vc = before.channel
    if vc is not None and after.channel is None and len(vc.members) == 1:
        await voice_channel.disconnect()
        queue = []
        is_playing=False
        pausing=False
        already_play=0


@client.event
async def on_message(msg):
    if ";" in msg.content:
        pass
    else:
        if not msg.author.bot:
            translator = Translator()
            results = translator.translate(msg.content)
            channel = client.get_channel(867346418079105055)
            await channel.send(f"{msg.author.name}\n{results.text}\nTranslated from:{results.src} " )

        line = msg.content
        line_split=line.split()
        if client.user.mentioned_in(msg) and not msg.author.bot:
            await msg.channel.send("<:ping:832925542768443402><:kanade_ping:858905090731802655><a:FKping:852459756039962634><:snow_ping:852742564582129675>")

        if "hi" in line_split and not msg.author.bot:
            await msg.channel.send(msg.author.mention)

        if "pro" in line_split and not msg.author.bot:
            await msg.channel.send('<a:emoji_32:836411269237702656>')

        if "課長" in msg.content and not msg.author.bot:
            await msg.channel.send('<:giftcard:828158809808699402><a:burndiamond:853952516765253652><a:emoji_32:836411269237702656>')

        if "暴死" in msg.content and not msg.author.bot:
            await msg.channel.send('<a:eat_diamond:852885172583923762>')
    await client.process_commands(msg)


@client.event
async def on_member_join(member):
    await member.send(f'Hello{member.mention}!please use`help` command to view how to use me ')


@client.command(name='ping', help='look for ping')
async def ping(ctx):
    await ctx.send(f'Your ping is: {round(client.latency * 1000)}ms')


@client.command(name='hello', help='Hello miku')
async def hello(ctx):
    if ctx.message.author.voice:
        try:
            voice = ctx.voice_client
            voice.play(discord.FFmpegPCMAudio(choice(vocal_hello)),after=lambda e: print('Player error: %s' % e) if e else None)
        except:
            await ctx.send('Hello')
    else:
        await ctx.send('Hello')


@client.command(name='developer', help='Look for how develop me')
async def developer(ctx):
    await ctx.send('Made by 柑橘Wang\nDebug by 美味的小圓,Python Taiwan,SHELTER ZONE\nVocal by 初音ミク')


@client.command(name='join', help='Let miku go to your voice channel')
async def join(ctx):
    global voice_channel

    if not ctx.message.author.voice:
        await ctx.send("You are not in voice channel")
        return
    else:
        voice_channel = ctx.message.author.voice.channel

    await voice_channel.connect()
    server = ctx.message.guild
    voice_channel = server.voice_client
    voice = ctx.voice_client
    voice.play(discord.FFmpegPCMAudio(choice(vocal_hello)), after=lambda e: print('Player error: %s' % e) if e else None)


@client.command(name='leave', help='Let Miku stop singing and leave the voice channel')
async def leave(ctx):
    global queue

    voice_channel = ctx.message.guild.voice_client
    await voice_channel.disconnect()
    queue=[]


@client.command(name='loop', help='Let Miku keep singing the same song')
async def loop_(ctx):
    global loop
    if loop:
        await ctx.send('Loop mode:disabled')
        loop = False
    else:
        await ctx.send('Loop mode:enabled')
        loop = True


@client.command(name='play', help='Let miku sing')
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
            await ctx.send("You are not in voice channel")
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
                    voice_lentage=dictMeta['duration']
                except:
                    continue
                await ctx.send(f'Miku is singing:{player.title}')
                is_playing = True
                already_play=0
                time_start = time()
                while((time_end-time_start<=voice_lentage-already_play) and is_playing==True):
                    await sleep(1)
                    time_end = time()
                    while(pausing==True):
                        await sleep(1)
                if loop == False:
                    try:
                        del (queue[0])
                    except IndexError:
                        pass
                if len(queue) == 0:
                    is_playing = False
                    break
        else:
            await ctx.send("Miku still don't know what you want to listen for please use `;;queue` let me know")


@client.command(nave="volume",help="Change the volume")
async def volume(ctx,volume):
    global value
    global voice_channel
    volume=float(volume)
    try:
        voice_channel.source = discord.PCMVolumeTransformer(voice_channel.source, 1 /value)
        voice_channel.source = discord.PCMVolumeTransformer(voice_channel.source, 1*volume)
    except:
        pass
    value=volume
    await ctx.send(f"Volume now:{value}")


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


@client.command(name="cancel",help="Cancel the song from queue")
async def cancel(ctx,url):
    global queue
    global is_playing

    if len(queue)<=1 and is_playing==True:
        await ctx.send("You can't delete the song that Miku is singing")
    else:
        if url in queue:
            try:
                queue.remove(url)
                await ctx.send(f"{url} have been delete successfully ")
            except:
                pass
        else:
            await ctx.send(f"{url} is not in queue use `;;view` to look for what you have")


@client.command(name='state', help='Look for Miku state')
async def state(ctx):
  global queue
  global loop
  global value

  if len(queue)==0:
    if loop==False:
      await ctx.send(f"No people order the song\nloop mode:disabled\nvolume {value}")
    else:
      await ctx.send(f"No people order the song\nloop mode:enabled\nvolume {value}")
  else:
     if loop==False:
      await ctx.send(f"It still have {len(queue)} songs\nloop mode:disabled\nvolume {value}")
     else:
      await ctx.send(f"It still have {len(queue)} songs\nloop mode:enabled\nvolume {value}")


@client.command(name='pause', help='Let miku pause to sing')
async def pause(ctx):
    global voice_channel
    global pauseing
    global time_start
    global time_end
    global already_play

    voice_channel.pause()
    pauseing=True
    already_play=time_end-time_start


@client.command(name='keep_playing', help='Let miku keep to sing')
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
    del (queue[0])
    global is_playing
    global pausing

    is_playing=False
    pausing=False
    voice_channel.stop()
    await sleep(0.5)
    voice = ctx.voice_client
    voice.play(discord.FFmpegPCMAudio(choice(vocal_i_got_this)),after=lambda e: print('Player error: %s' % e) if e else None)


@client.command(name='queue',help='Let Miku know what you want to order')
async def queue_(ctx, url):
    global queue
    if "https://www.youtube.com/watch?" not in url:
        await ctx.send("It is no youtube url")
    else:
        queue.append(url)
        await ctx.send(f'`{url}`I got your order!')
        await YTDLSource.from_url(url, loop=client.loop)
        sleep(0.5)
        if ctx.message.author.voice:
            voice = ctx.voice_client
            try:
                voice.play(discord.FFmpegPCMAudio(choice(vocal_i_got_this)),after=lambda e: print('Player error: %s' % e) if e else None)
            except:
                pass


@client.command(name='view', help='Let you know how many songs that Miku still have to sing for')
async def view(ctx):
    global queue
    global player
    play_list=""
    if len(queue)==0:
        await ctx.send('Miku have not get your order')
    else:
        play_list=play_list+f'Miku is singing:{player.title}\n'
        if len(queue)>1:
            for i in range(len(queue)):
                if i>=1:
                    wait_to_play = await YTDLSource.from_url(queue[i], loop=client.loop)
                    try:
                        play_list=play_list+f'Miku have to sing later:{wait_to_play.title}\n'
                    except:
                        break
        await ctx.send(f'```{play_list}```')


@client.command(name="skip",help="Skip the song")
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

    await ctx.send(f'Miku is singing:{player.title}')
    time_start = time()
    voice_lentage=dictMeta['duration']


@client.command(name="rank",help=("Show the event rank of project sekai"))
async def rank(ctx):
    global sorted
    await ctx.send(f"```{sorted}```")


@client.command(name="lottery",help="get a lottery from project sekai")
async def lottery(ctx):
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
    star=((choices(can_get, weights=[3, 85, 885])))

    image_names = list(walk(f"D:/Discordbot/{star[0]}/"))[0][2]
    selected_images = choices(image_names)
    file = discord.File(f"D:/Discordbot/{star[0]}/{selected_images[0]}")
    await ctx.send(f"<@{ctx.author.id}>")
    await ctx.send(file=file)
    if star==["4star"]:
        try:
            voice = ctx.voice_client
            voice.play(discord.FFmpegPCMAudio(choice(vocal_Congratulations)),
                       after=lambda e: print('Player error: %s' % e) if e else None)
        except:
            pass


@client.command(name='lottery*10', help='get a lottery from project sekai 10 times')
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
    start_time=time()
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
    end_time=time()
    print(end_time-start_time)

    if "4star" in gtl:
        try:
            voice = ctx.voice_client
            voice.play(discord.FFmpegPCMAudio(choice(vocal_Congratulations)),after=lambda e: print('Player error: %s' % e) if e else None)
        except:
            pass
    remove(f"D:/Discordbot/result/{message_id}result.png")

@client.command()
async def in_your_dream(ctx):
    send=""
    for i in range(10):
        send=send+'<:4star:828160732318138389>'
        if i==4:
            send=send+"\n"
    await ctx.send(f"<@{ctx.author.id}>\n{send}")


tokenfile = open("token.txt","r")
token=tokenfile.read()
token=eval(token)
TOKEN=token["en"]
tokenfile.close()
client.run(TOKEN)