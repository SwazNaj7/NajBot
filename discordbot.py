import discord
import json
import random
import os
import asyncio
from discord.abc import _Overwrites
from discord.ext.commands import bot
import youtube_dl
import aiofiles
from discord.utils import get
from discord.ext import commands, tasks

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix = '.', intents=intents)
client.warnings = {} #guild_id : {member_id [count, [(admin_id, reason)]]}
client.remove_command("help")

@client.event
async def on_ready():
    for guild in client.guilds:
        async with aiofiles.open(f"{guild.id}.txt", mode="a") as temp:
            pass

        client.warnings[guild.id] = {}

    for guild in client.guilds:
        async with aiofiles.open(f"{guild.id}.txt", mode="r") as file:
            lines = await file.readlines()

            for line in lines:
                data = line.split(" ")
                member_id = int(data[0])
                admin = int(data[1])
                reason = " ".join(data[2:]).strip("\n")

                try:
                    client.warnings[guild.id][member_id][0] += 1
                    client.warnings[guild.id][member_id][1].append((admin_id, reason))

                except KeyError:
                    client.warnings[guild.id][member_id] = [1, [(admin_id, reason)]]

@client.event
async def on_message_delete(message):
    global snipe_message_content
    global snipe_message_author
    snipe_message_content = message.content
    snipe_message_author = message.author.name
    await asyncio.sleep(60)
    snipe_message_author = None
    snipe_message_content = None

@client.command()
async def snipe(message):
    if snipe_message_content==None:
       await message.channel.send("Couldn't find anything to snipe!")    
    else:
        embed = discord.Embed(description=f"{snipe_message_content}")
        embed.set_footer(text=f"Requested By {message.author.name}#{message.author.discriminator}")
        embed.set_author(name = f"Sniped the message deleted by : {snipe_message_author}")
        await message.channel.send(embed=embed)
        return

@client.command()
@commands.has_permissions(administrator=True)
async def warn(ctx, *, member: discord.Member=None, reason=None):
    if member is None:
        return await ctx.send("The provided member could not be found or you forgot to provide one")

    if reason is None:
        return await ctx.send("Please provide a reason for warning the user")

    try:
        first_warning = True
        client.warnings[ctx.guild.id][member.id][0] += 1 
        client.warnings[ctx.guild.id][member.id][1].append((ctx.author.id, reason))

    except KeyError:
        first_warning = True
        client.warnings[ctx.guild.id][member.id] = [1, [(ctx.author.id, reason)]]

    count = client.warnings[ctx.guild.id][member.id][0]

    async with aiofiles.open(f"{ctx.guild.id}.txt", mode="a") as file:
        await file.write(f"{member.id} {ctx.author.id} {reason}\n")

    await ctx.send(f"{member.mention} has {count} {'warning' if first_warning else 'warnings'}.")

@client.command()
@commands.has_permissions(administrator=True)
async def warnings (ctx, member: discord.Member=None, *, reason=None):
    if member is None:
        return await ctx.send("The provided member could not be found or you forgot to provide one")

    embed = discord.Embed(title=f"Displaying warnings for {member.name}", description="", colour=discord.Colour.red())
    try:
        i = 1
        for admin_id, reason in client.warnings[ctx.guild.id][member.id][1]:
            admin = ctx.guild.get_member(admin_id)
            embed.description += f"**Warning {i}** given by: {admin.mention} for: *'{reason}'*.\n"
            i += 1 

        await ctx.send(embed=embed)
        
    except KeyError: # no warnings
        await ctx.send("This user has no warnings")

@client.command(pass_context=True, aliases=['av'])
async def avatar(ctx, *, member: discord.Member = None):
    member = ctx.author if not member else member
    embed = discord.Embed(title = f"{member.name}'s avatar", color = member.color, timestamp= ctx.message.created_at)
    embed.set_image(url=member.avatar_url)
    embed.set_footer(text=f"Requested by : {ctx.author}", icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)

@client.event
async def on_guild_join(guild):
    bot.warnings[guild.id] = {}

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game('Hello there! I am NajBot'))
    print('Bot is ready.')

@client.event
async def on_member_join(member):
    print(f'{member} has joined a server.')

@client.event
async def on_member_remove(member):
    print(f'{member} has left a server.')

@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency * 1000)}ms')

@client.group(invoke_without_command=True)
async def help(ctx):
    em = discord.Embed(title = "Help", description = "Use .help <command> for extended information on a command")

    em.add_field(name = "Moderation", value = "kick, warn, ban, mute, unmute, userinfo, snipe, warnings, ping")
    em.add_field(name = "Fun", value = "8ball, hello")
    em.add_field(name = "Music", value = "join, leave, play")

    await ctx.send(embed = em)

@help.command()
async def kick(ctx):

    em = discord.Embed(title = "Kick", description = "Kicks a member from guild", color = ctx.author.color)

    em.add_field(name = "**Syntax**", value = ".kick <member> [reason]")

    await ctx.send(embed = em)

@help.command()
async def ban(ctx):

    em = discord.Embed(title = "Ban", description = "Bans a member from guild", color = ctx.author.color)

    em.add_field(name = "**Syntax**", value = ".ban <member> [reason]")

    await ctx.send(embed = em)

@help.command()
async def warn(ctx):

    em = discord.Embed(title = "warn", description = "Warns a member in guild", color = ctx.author.color)

    em.add_field(name = "**Syntax**", value = ".warn <member> [reason]")

    await ctx.send(embed = em)

@help.command()
async def mute(ctx):

    em = discord.Embed(title = "Mute", description = "Mutes a member in guild", color = ctx.author.color)

    em.add_field(name = "**Syntax**", value = ".mute <member> [reason]")

    await ctx.send(embed = em)

@help.command()
async def unmute(ctx):

    em = discord.Embed(title = "unmute", description = "Unmutes a member in guild", color = ctx.author.color)

    em.add_field(name = "**Syntax**", value = ".unmute <member>")

    await ctx.send(embed = em)

@help.command()
async def userinfo(ctx):

    em = discord.Embed(title = "userinfo", description = "Gives the user info", color = ctx.author.color)

    em.add_field(name = "**Syntax**", value = ".userinfo <member>")

    await ctx.send(embed = em)

@help.command()
async def _8ball(ctx):

    em = discord.Embed(title = "Ban", description = "Fun _8ball game", color = ctx.author.color)

    em.add_field(name = "**Syntax**", value = ".ban <member> [reason]")

    await ctx.send(embed = em)

@help.command()
async def join(ctx):

    em = discord.Embed(title = "Join", description = "Joins voice channel", color = ctx.author.color)

    em.add_field(name = "**Syntax**", value = ".join")

    await ctx.send(embed = em)

@help.command()
async def leave(ctx):

    em = discord.Embed(title = "Leave", description = "Leaves voice channel", color = ctx.author.color)

    em.add_field(name = "**Syntax**", value = ".leave")

    await ctx.send(embed = em)

@help.command()
async def play(ctx):

    em = discord.Embed(title = "Play", description = "Plays music in voice channel", color = ctx.author.color)

    em.add_field(name = "**Syntax**", value = ".play <link>")

    await ctx.send(embed = em)

@help.command()
async def warnings(ctx):

    em = discord.Embed(title = "Warnings", description = "Display's user warnings", color = ctx.author.color)

    em.add_field(name = "**Syntax**", value = ".warnings <@Mention>")

    await ctx.send(embed = em)

@help.command()
async def snipe(ctx):

    em = discord.Embed(title = "Snipe", description = "Finds last deleted message", color = ctx.author.color)

    em.add_field(name = "**Syntax**", value = ".snipe")

    await ctx.send(embed = em)

@client.command(aliases=['8ball'])
async def _8ball(ctx, *, question):
    responses = ['As I see it, yes.',
                'Ask again later.',
                'Better not tell you now.',
                'Cannot predict now.',
                'Concentrate and ask again.',
                'Don’t count on it.',
                'It is certain.',
                'It is decidedly so.',
                'Maybe',
                'Never',
                'Yes Indeed',
                'Most likely.',
                'My reply is no.',
                'My sources say no.',
                'Outlook not so good.',
                'Outlook good.',
                'Reply hazy, try again.',
                'Signs point to yes.',
                'Very doubtful.',
                'Without a doubt.',
                'Yes.',
                'Yes – definitely.',
                'You may rely on it.',
                'Why would you ask this.',
                'I can neither confirm or deny.',
                'I see this as a realistic outcome.',
                'Goodbye.',
                'I shall ignore you.',
                'Soon',
                'In the near future',
                'Today',
                'Tomorrow',
                'In 10 years',
                'In 30 years',
                'Just give up on it',
                'Probably',
                'No sir.',
                'You need a break?.',
                'I do not have the mental capacity to answer.',]
    await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')


@client.command()
async def kick(ctx, member : discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'Kicked {member.mention}')

@client.command()
async def ban(ctx, member : discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'Banned {member.mention}')

@client.command()
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'Unbanned {user.mention}')
            return

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Invalid command used.')

@client.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount : int):
    await ctx.channel.purge(limit=amount)

def is_it_me(ctx):
    return ctx.author.id == 764364961296154644

@client.command()
@commands.check(is_it_me)
async def whoami(ctx):
    await ctx.send(f'Hi im{ctx.author}')

@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify an amount of messages to delete.')

@client.command()
async def hello(ctx, arg):
    await ctx.message.delete()
    await ctx.send(arg)

@client.command()
async def mute(ctx, member : discord.Member):
    guild = ctx.guild

    for role in guild.roles:
        if role.name == "Muted":
            await member.add_roles(role)
            await ctx.send("{} has been muted by {}" .format(member.mention,ctx.author.mention))
            return

            await new_func()

async def new_func():
    overwrites = discord.PermissionsOverwrite(send_messages=False)
    newRole = await guild.create_role(name="Muted")

    for channel in guild.text_channels:
        await channel.set_permissions(newRole, overwrite=overwrite)

    await member.add_roles(newRole)
    await ctx.send("{} has been muted by {}" .format(member.mention,ctx.author.mention))

@client.command()
async def unmute(ctx, member : discord.Member):
    guild = ctx.guild

    for role in guild.roles:
        if role.name == "Muted":
            await member.remove_roles(role)
            await ctx.send("{} has been unmuted by {}" .format(member.mention,ctx.author.mention))
            return

@client.command(pass_context=True)
async def join(ctx):
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
    await ctx.send(f"Joined {channel}")

@client.command(pass_context=True)
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        await ctx.send(f"Left {channel}")

@client.command(pass_context=True, aliases=['p', 'pla'])
async def play(ctx, url: str):    
    song_there = os.path.isfile("song.mp3")
    try:    
        if song_there:
            os.remove("song.mp3")
            print("Removed old song file")
    except PermissionError:
        print("Trying to delete song file, but it's being played")
        await ctx.send("ERROR: Music Playing")
        return
    
    await ctx.send("Getting everything ready now")

    voice = get(client.voice_clients, guild=ctx.guild)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio now\n")
        ydl.download([url]) 

    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            name = file
            print(f"Renamed File: {file}")
            os.rename(file, "song.mp3")

    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: print(f"{name} has finished playing"))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.20

    nname = name.rsplit("-", 2)
    await ctx.send(f"Playing: {nname}")
    print("playing\n")

@client.command()
async def userinfo(ctx, member: discord.Member):

    roles = [role for role in member.roles]

    roles = []
    for role in member.roles:
        roles.append(role)


    embed = discord.Embed(colour=member.color, timestamp=ctx.message.created_at)

    embed.set_author(name=f"User Info - {member}")
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

    embed.add_field(name="ID:", value=member.id)
    embed.add_field(name="Guild name:", value=member.display_name)

    embed.add_field(name="Created at:", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
    embed.add_field(name="Joined at:", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))

    embed.add_field(name=f"Roles ({len(roles)})", value=" ".join([role.mention for role in roles]))
    embed.add_field(name="Top role:", value=member.top_role.mention)

    embed.add_field(name="Bot?", value=member.bot)

    await ctx.send(embed=embed)

#Enter your bot token in the paremeters
client.run('')
