import discord
from aioftp import server
from discord.ext import commands, tasks
from discord.voice_client import VoiceClient
import youtube_dl
import time
import random
from random import choice
import asyncio


youtube_dl.utils.bug_reports_message = lambda: ''

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

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

status = ['等待指令中!', '正在和william玩', 'Sleeping!']
queue = []
loop = False
is_playing=False
voice_lentage=0
time_start=0
value=1.0
time_end=0

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data):
        global value
        super().__init__(source,value)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')


    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

def is_connected(ctx):
    voice_client = ctx.message.guild.voice_client
    return voice_client and voice_client.is_connected()


client = commands.Bot(command_prefix=';;')



@client.event
async def on_ready():
    change_status.start()
    print('Bot is online!')


@client.event
async def on_message(msg):
    if ";" in msg.content or":" in msg.content:
       pass
    else:
        if client.user.mentioned_in(msg) and not msg.author.bot:
            await msg.channel.send("<:ping:832925542768443402><:kanade_ping:837493288504262707>")
        if "hi" in msg.content and not msg.author.bot:

            await msg.channel.send(msg.author.mention)

    await client.process_commands(msg)


@client.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name='general')
    await channel.send(f'你好{member.mention}!準備好和Miku玩了嗎? 歐逆醬請用`;;help`怎麼玩弄我')


@client.command(name='ping', help='看你家網路有多爛(沒')
async def ping(ctx):
    await ctx.send(f'你的網路延遲是: {round(client.latency * 1000)}ms')


@client.command(name='hello', help='miku安安')
async def hello(ctx):
    if ctx.message.author.voice:
        voice = ctx.voice_client
        voice.play(discord.FFmpegPCMAudio("D:/聲音樣本/hello2.wav"),after=lambda e: print('Player error: %s' % e) if e else None)

    else:
        await ctx.send('歐逆醬安安')


'''@client.command(name='die', help='This command returns a random last words')
async def die(ctx):
    responses = ['why have you brought my short life to an end', 'i could have done so much more',
                 'i have a family, kill them instead']
    await ctx.send(choice(responses))'''


@client.command(name='developer', help='讓你知道Miku的開發者')
async def credits(ctx):
    await ctx.send('Made by 柑橘Wang')
    await ctx.send('Debug by 美味的小圓,Python Taiwan,SHELTER ZONE')
    await ctx.send('Vocal by 初音ミク')


@client.command(name='join', help='讓miku加入語音頻道')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("你沒有加入語音頻道")
        return
    else:
        channel = ctx.message.author.voice.channel

    await channel.connect()
    voice = ctx.voice_client
    voice.play(discord.FFmpegPCMAudio("D:/聲音樣本/hello2.wav"), after=lambda e: print('Player error: %s' % e) if e else None)


@client.command(name='leave', help='讓miku停止唱歌並離開語音頻道')
async def leave(ctx):
    global queue
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()
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
    global time_start
    global voice_lentage
    global is_playing
    global time_end


    if not ctx.message.author.voice:
        await ctx.send("你不在語音頻道內")
        return

    else:
        channel = ctx.message.author.voice.channel

    try:
        await channel.connect()
    except:
        pass

    server = ctx.message.guild
    voice_channel = server.voice_client

    if len(queue) > 0:
        while (True):

            player = await YTDLSource.from_url(queue[0], loop=client.loop)
            with youtube_dl.YoutubeDL(ytdl_format_options) as ydl:
                dictMeta = ydl.extract_info(f"{queue[0]}", download=False)
            try:
                voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
                is_playing=True
                voice_lentage=dictMeta['duration']
            except:
                continue


            await ctx.send('**為主人獻上:** {}'.format(player.title))
            time_start = time.time()
            while(time_end-time_start<=voice_lentage):
                await asyncio.sleep(1)
                time_end = time.time()
            if loop == False:
                try:
                    del (queue[0])
                except IndexError:
                    pass
            if len(queue) == 0 and loop == False:
                break
                is_playing=False


    else:
        await ctx.send("Miku還不知道主人想聽什麼,用\";;queue\"讓我知道")



@client.command(nave="volume",help="調整音量")
async def volume(ctx,volume):
    global value
    value=float(volume)
    await ctx.send(f"目前音量為{value}")



@client.command(name="schedule",help="讓主人知道現在Miku唱到哪了")
async def schedule(ctx):
    global time_start
    global queue
    global voice_lentage
    global time_end
    time_sch=time_end-time_start
    time_sch=int(time_sch)
    lentage_min=voice_lentage//60
    lentage_sec=voice_lentage%60
    time_sch_sec=time_sch%60
    time_sch_min=time_sch//60
    if lentage_sec<10:
        await ctx.send(f"目前播放進度:  {time_sch_min}:{time_sch_sec}/{lentage_min}:0{lentage_sec}")
    elif lentage_sec<10 and time_sch_sec<10:
        await ctx.send(f"目前播放進度:  {time_sch_min}:0{time_sch_sec}/{lentage_min}:0{lentage_sec}")
    elif time_sch_sec<10:
        await ctx.send(f"目前播放進度:  {time_sch_min}:0{time_sch_sec}/{lentage_min}:{lentage_sec}")
    else:
        await ctx.send(f"目前播放進度:  {time_sch_min}:{time_sch_sec}/{lentage_min}:{lentage_sec}")


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
    if loop==False:
      await ctx.send(f"目前還沒人點歌\n重撥模式:關閉\n目前音量{value}")
    else:
      await ctx.send(f"目前還沒人點歌\n重撥模式:開啟\n目前音量{value}")
  else:
     if loop==False:
      await ctx.send(f"目前還有{len(queue)}首歌\n重撥模式:關閉\n目前音量{value}")
     else:
      await ctx.send(f"目前還有{len(queue)}首歌\n重撥模式:開啟\n目前音量{value}")


@client.command(name='pause', help='讓miku先不要唱歌')
async def pause(ctx):
    voice_channel = server.voice_client
    voice_channel.pause()


@client.command(name='resume', help='讓Miku重唱一次')
async def resume(ctx,voice_client):
    voice_channel = server.voice_client
    voice_channel.resume()



@client.command(name='stop', help='讓miku停止唱歌!')
async def stop(ctx):
    global queue
    del (queue[0])
    server = ctx.message.guild
    voice_channel = server.voice_client
    voice_channel.stop()
    time.sleep(0.5)
    voice = ctx.voice_client
    voice.play(discord.FFmpegPCMAudio("D:/聲音樣本/i got this2.wav"),after=lambda e: print('Player error: %s' % e) if e else None)



@client.command(name='queue',help='讓Miku知道主人想聽什麼')
async def queue_(ctx, url):
    global queue
    queue.append(url)
    await ctx.send(f'`{url}`我已經收到主人需求!')
    time.sleep(0.5)
    if ctx.message.author.voice:
        voice = ctx.voice_client
        try:

            voice.play(discord.FFmpegPCMAudio("D:/聲音樣本/i got this2.wav"),after=lambda e: print('Player error: %s' % e) if e else None)
        except:
            pass


@client.command(name='view', help='讓主人知道miku還有多少歌還沒唱完')
async def view(ctx):
    global queue
    if len(queue)==0:
        await ctx.send('主人還沒點歌喔')
    else:
        player = await YTDLSource.from_url(queue[0], loop=client.loop)
        await ctx.send('**Miku正在唱:** {}'.format(player.title))
        if len(queue)>1:
            for i in range(len(queue)):
                if i>=1:
                    player = await YTDLSource.from_url(queue[i], loop=client.loop)
                    try:
                        await ctx.send('**Miku還要唱:** {}'.format(player.title))
                    except:
                        break



@tasks.loop(seconds=20)
async def change_status():
    await client.change_presence(activity=discord.Game(choice(status)))



@client.command(name="skip",help="跳過這首歌")
async def skip(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client
    voice_channel.stop()
    global queue
    global time_start
    global voice_lentage
    del(queue[0])

    player = await YTDLSource.from_url(queue[0], loop=client.loop)
    with youtube_dl.YoutubeDL(ytdl_format_options) as ydl:
        dictMeta = ydl.extract_info(f"{queue[0]}", download=False)
        voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    await ctx.send('**為主人獻上:** {}'.format(player.title))
    time_start = time.time()
    voice_lentage=dictMeta['duration']


@client.command(name="抽卡",help="讓miku決定你是非洲人還是歐洲人")

async def 抽卡(ctx):
    random.seed(time.time())
    a = random.sample(range(1, 1000), 115)
    b = []
    for i in range(85):
        b.append(a[i])
    for i in range(85):
        a.remove(b[i])
    gt = random.randint(1, 1000)
    if gt in a:
        await ctx.send(f"<@{ctx.author.id}>\n" + " <:4star:828160732318138389>")
    elif gt in b:
        await ctx.send(f"<@{ctx.author.id}> \n" + "<:3star:828160732419063818>")
    else:
        await ctx.send(f"<@{ctx.author.id}> \n" + "<:2star:828160732512256010>")



@client.command(name='十抽', help='讓miku抽十次看你是真歐洲還是真非洲')
async def 十抽(ctx):
    if not ctx.message.author.voice:
        pass

    else:
        channel = ctx.message.author.voice.channel

    try:
        await channel.connect()
    except:
        pass

    server = ctx.message.guild
    random.seed(time.time())
    a = random.sample(range(1, 1000), 115)
    b = []
    gtl=[]
    for i in range(85):
        b.append(a[i])
    for i in range(85):
        a.remove(b[i])
    for i in range(10):
        gt = random.randint(1, 1000)
        if gt in a:
            gtl.append("<:4star:828160732318138389>")
        elif gt in b:
            gtl.append("<:3star:828160732419063818>")
        else:
            gtl.append("<:2star:828160732512256010>")
    if "<:4star:828160732318138389>"and"<:3star:828160732419063818>"not in gtl:
        replace=random.randint(0,9)

        gt = random.randint(1, 100)
        if 1<=gt<=3:
            gtl[replace]=("<:4star:828160732318138389>")
        else:
            gtl[replace]=("<:3star:828160732419063818>")
    await ctx.send(f"<@{ctx.author.id}>\n{gtl} ")
    if (gtl.count("<:4star:828160732318138389>")>=1 or gtl.count("<:3star:828160732419063818>")>=3):

        try:
            voice = ctx.voice_client
            voice.play(discord.FFmpegPCMAudio("D:/聲音樣本/恭喜.wav"),after=lambda e: print('Player error: %s' % e) if e else None)
        except:
            pass


@client.command()
async def 歐洲人(ctx):
    gtl= ["<:4star:828160732318138389>"*10]
    await ctx.send(f"<@{ctx.author.id}>\n{gtl}")





client.run('TOKEN')
