import discord
import random

client = discord.Client()

token_file = open("token.txt", "r")
token = token_file.read()
token_file.close()

is_curious = False
channels = []


@client.event
async def on_ready():
    print("Name: "+client.user.name)
    print("ID: "+client.user.id)
    global channels
    channels = client.get_all_channels()
    for channel in channels:
        try:
            await client.send_message(channel, "UnlikeBot, up and running!")
        except:
            print("Cannot access channel: "+channel.name)


@client.event
async def on_message(message):
    print("----- on_message -----")
    print("author name: "+message.author.name)
    print("content: "+message.content)
    if message.content.startswith("."):
        command_str = message.content
        command_words = message.content.split()
        if command_words[0].lower() == ".ping":
            await client.send_message(message.channel, "Pong!")
        elif command_words[0].lower() == ".pong":
            await client.send_message(message.channel, "Ping!")
        elif command_words[0].lower() == ".curious":
            if (len(command_words) < 2
                    or command_words[1].lower() not in ["on", "off"]):
                await client.send_message(message.channel,
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
                    "<:chew:313116045718323211>\n    <:duwang:23205839219615334"
                    +"5>")


@client.event
async def on_typing(channel, user, when):
    if is_curious:
        await client.send_message(channel,"What are you typing, "+user.name+"?")


client.run(token)
