import discord
import random
import uno

client = discord.Client()

token_file = open("token.txt", "r")
token = token_file.read()
token_file.close()

is_curious = False
channels = []

is_playing_uno = False
uno_players = []
uno_host_channel = None

@client.event
async def on_ready():
    print("Name: " + client.user.name)
    print("ID: " + client.user.id)
    global channels
    channels = client.get_all_channels()
    for channel in channels:
        try:
            await client.send_message(channel, "UnlikeBot, up and running!")
        except:
            print("Cannot access channel: " + channel.name)


@client.event
async def on_message(message):
    print("----- on_message -----")
    print("author name: " + message.author.name)
    print("content: "+message.content)
    print("server: "+str(message.channel))
    if message.author == client.user:
        return

    if message.content.lower() == "ayy":
        await client.send_message(message.channel, "lmao")
    elif "unlike" in message.content.lower():
        await client.send_message(message.channel, "**U N L I K E**")
    
    if message.content.startswith("."):
        command_str = message.content
        command_words = message.content.split()

        global is_playing_uno, uno_players, uno_host_channel

        if command_words[0].lower() == ".help":
            await post_command_list(message.channel)
        elif command_words[0].lower() == ".ping":
            await client.send_message(message.channel, "Pong!")
        elif command_words[0].lower() == ".pong":
            await client.send_message(message.channel, "Ping!")
        elif command_words[0].lower() == ".curious":
            if (len(command_words) < 2 
                    or command_words[1].lower() not in ["on", "off"]):
                await client.send_message(
                        message.channel,
                        "`.curious on` or `.curious off`?")
                return
            global is_curious
            if command_words[1].lower() == "off":
                await client.send_message(
                        message.channel,
                        "Okay, I'll stop disturbing you while you type.")
                is_curious = False
            else:
                is_curious = True
                await client.send_message(
                        message.channel,
                        "<:chew:313116045718323211>\n"
                        + "    <:duwang:232058392196153345>")
        elif command_words[0].lower() == ".unlikesuika":
            await client.send_message(message.channel, "<@119701092731715585>")
        elif is_playing_uno:
            if not await uno.process_message(message):
                # Game ended
                is_playing_uno = False
                uno_players = []
                uno_host_channel = None
        elif command_words[0].lower() == ".uno":
            if uno_players:
                await client.send_message(
                        message.channel,
                        "**"
                        + uno_players[0].name
                        + "** has already hosted the game. Type `.ujoin` to "
                        + "join their game. To start the game, the dealer must "
                        + "type `.ustart`.")
                return
            elif str(discord.PrivateChannel) == str(type(message.channel)):
                await client.send_message(
                        message.channel,
                        "You can't host in a private channel.")
                return
            uno_players.append(message.author)
            uno_host_channel = message.channel
            await client.send_message(
                    message.channel,
                    "**"
                    + message.author.name
                    + "** is the dealer. Type `.ujoin` to join their game. The "
                    + "dealer must type `.ustart` to start the game.")
        elif command_words[0].lower() == ".ujoin":
            if not uno_players:
                await client.send_message(
                        message.channel,
                        "The game has not been hosted yet. Type `.uno` to host "
                        + "a game.")
            elif message.channel != uno_host_channel:
                await client.send_message(
                        message.channel,
                        "The game is being hosted at `#"
                        + str(uno_host_channel)
                        + "`. Please join or start the game at that channel.")
            elif message.author in uno_players:
                await client.send_message(
                        message.channel,
                        "You are already in this game.")
            elif len(uno_players) >= 10:
                await client.send_message(
                        message.channel,
                        "Only up to ten players can join per game.")
            else:
                uno_players.append(message.author)
                await client.send_message(
                        message.channel,
                        message.author.name
                        + " joins as **Player #"
                        + str(len(uno_players))
                        + "**.")
        elif command_words[0].lower() == ".ustart":
            if not uno_players:
                await client.send_message(
                        message.channel,
                        "There is no game being hosted right now. Type `.uno`"
                        + " to host a game.")
            elif message.channel != uno_host_channel:
                await client.send_message(
                        message.channel,
                        "The game is being hosted at `#"
                        + str(uno_host_channel)
                        + "`. Please join or start the game at that channel.")
            elif len(uno_players) == 1:
                await client.send_message(
                        message.channel,
                        "There are not enough players. You need at least two"
                        + " people to play.")
            elif message.author not in uno_players:
                await client.send_message(
                        message.channel,
                        "You are currently not part of this game. Type `.ujoin`"
                        + " to join the game.")
            elif message.author != uno_players[0]:
                await client.send_message(
                        message.channel,
                        "You are not the dealer. The dealer must start the "
                        + "game.")
            else:
                is_playing_uno = True
                await uno.start(uno_players, client, uno_host_channel)
        elif command_words[0].lower() == ".ustop":
            if not uno_players:
                await client.send_message(
                        message.channel,
                        "There is no game being hosted right now.")
            elif message.channel != uno_host_channel:
                await client.send_message(
                        message.channel,
                        "The game is being hosted at `#"
                        + str(uno_host_channel)
                        + "`. Please stop the game at that channel.")
            else:
                await client.send_message(
                        message.channel,
                        "The game is no longer hosted.")
                is_playing_uno = False
                uno_players = []
                uno_host_channel = None
                

@client.event
async def on_typing(channel, user, when):
    if is_curious:
        await client.send_message(
                channel,
                "What are you typing, "
                + user.name
                + "?")


async def post_command_list(channel):
    content = "`.help` - You probably already know this.\n"
    content += "`.uno`- Hosts a game for UNO.\n"
    content += "`.ping` - Responds with Pong.\n"
    content += "`.pong` - Responds with Ping.\n"
    content += "`.curious [on/off]` - Bugs a person whenever they type when "
    content += "toggled on.\n"
    content += "`.unlikesuika` - Pings the master.\n"
    content += "`ayy` - lmao"
    await client.send_message(channel, content)
    

client.run(token)
