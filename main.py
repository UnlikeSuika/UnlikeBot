import discord
import random

client = discord.Client()

token_file = open("token.txt", "r")
token = token_file.read()
token_file.close()

@client.event
async def on_ready():
    print("Name: "+client.user.name)
    print("ID: "+client.user.id)
    print("Now up and running!")
    print("----------")

client.run(token)
