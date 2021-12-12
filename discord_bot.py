import os
import random
import discord
import setuptools
from aitextgen import aitextgen
from discord.ext.commands import Bot
import asyncio

# Get credentials for local running
from dotenv import load_dotenv
load_dotenv()

# Use CPU config because Radeon is silly
from aitextgen.utils import GPT2ConfigCPU

ai = aitextgen(model_folder="trained_model", config=GPT2ConfigCPU())

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

@client.command()
async def prompt(ctx, string: str):
    await generateSentence(ctx, prompt=string)

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
async def generateSentence(ctx, respond_to=None, prompt=""):
    async with ctx.typing():

        generated = ai.generate(n=3,
            batch_size=1,
            max_length=80,
            temperature=1.0,
            top_p=0.9,
            return_as_list=True,
            prompt=prompt
            )
        print(generated)
        # Sort by length and choose the first one
        split_text = generated[0].split("\n")
        split_text.sort(key=lambda item: (-len(item), item))
        single_text = split_text[0]

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
client.run(os.environ["DISCORD_TOKEN"])
