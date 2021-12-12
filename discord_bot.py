import os
import random
import discord
import gpt_2_simple as gpt2
from discord.ext.commands import Bot
import asyncio

# Get credentials for local running
from dotenv import load_dotenv
load_dotenv()

from keep_alive import keep_alive

# Load GPT2 locally (download from Google Drive)
sess = gpt2.start_tf_sess()
gpt2.load_gpt2(sess)

# Use Bot instead of Discord Client for commands
client = Bot("!")
task_seconds = 100
task_running = False

@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    await client.change_presence(activity=discord.Game(name="with AI"))


@client.command(aliases=["gen"])
async def generate(ctx):
    if not task_running:
        client.loop.create_task(generateTask(ctx))
    else:
        await generateSentence(ctx)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if "stfu bot" in message.content and message.author.guild_permissions.administrator:
        await client.close()

    ctx = await client.get_context(message)

    # random chance to respond to a message, always respond if mentioned
    if random.randint(0, 100) < 25 or client.user.mentioned_in(message):
        await generateSentence(ctx, message)

    await client.process_commands(message)

# Actual function to generate AI sentences
async def generateSentence(ctx, respond_to=None):
    async with ctx.typing():
        generated = gpt2.generate(sess, return_as_list=True, length=30)[0]
        single_text = generated.split("\n")[0]

    print(single_text)

    # either reply to a user or just send a message
    if respond_to != None:
        await respond_to.reply(single_text)
    else:
        await ctx.send(single_text)

# Asyncio used to create background task
async def generateTask(ctx):
    global task_running
    task_running = True
    while task_running:
        await generateSentence(ctx, None)
        await asyncio.sleep(task_seconds)


# Run bot
keep_alive()
client.run(os.environ["DISCORD_TOKEN"])
