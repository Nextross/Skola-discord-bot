import os
import regex
import discord
from discord.ext import commands
from replit import db

token = os.environ['TOKEN']
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = commands.Bot(command_prefix="!", intents=intents)


def is_date_valid(date_str):
    return bool(regex.fullmatch(r"^(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]|(?:Jan|Mar|May|Jul|Aug|Oct|Dec)))\1|(?:(?:29|30)(\/|-|\.)(?:0?[1,3-9]|1[0-2]|(?:Jan|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec))\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)(?:0?2|(?:Feb))\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9]|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep))|(?:1[0-2]|(?:Oct|Nov|Dec)))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})$", date_str))


# This function will sort all events by date (ascending)
def sort_events():
    sorted_events = {}
    db_sorted_keys = sorted(db, key=lambda x: list(map(int, x.split('.')))[::-1])

    for date in db_sorted_keys:
        sorted_events[date] = db[date]

    return sorted_events


# This function will create an embed window with all sorted events
def create_embed(events: dict):
    embed_window = discord.Embed(title="Všechny události", color=0xfc050d)
    if len(events) != 0:
        for key in events.keys():
            value = ""
            for event in events[key]:
                value += f'{event}\n'
            embed_window.add_field(name=key, value=value, inline=False)

        return embed_window
    else:
        return discord.Embed(title="Všechny události", description="Žádné události k zobrazení")


# Prints a message when the bot successfully connects
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game("Zkus !commands"))
    print("The bot is ready")


# This command will add an event(s) to the database
@client.command()
async def add(ctx, date, *events):
    if len(events) != 0:
        events = ', '.join(events).split(", ")

        if is_date_valid(date):
            if date in db:
                db[date] += events
            else:
                db[date] = events

            await ctx.send(f"Událost přidána ({len(events)}), {ctx.message.author.mention}")
        else:
            await ctx.send(f"Uvedl(a) jsi špatné datum. Datum musí být ve formátu `DD.MM.YYYY`, {ctx.message.author.mention}")
    else:
        await ctx.send(f"Neuvedl(a) jsi datum, {ctx.message.author.mention}")


# This command will show all events for a specified date
@client.command()
async def show(ctx, date):
    try:
        if date != 0:
            embed_window = discord.Embed(title="Zvolená událost", color=0xfc050d)
            value = ""

            for event in db[date]:
                value += f"{event}\n"

            embed_window.add_field(name=date, value=value, inline=False)
            await ctx.send(embed=embed_window)
        else:
            await ctx.send(f"Neuvedl(a) jsi žádné datum, {ctx.message.author.mention}")
    except KeyError:
        await ctx.send(f"Událost pro datum '{date}' neexistuje, {ctx.message.author.mention}")


# This command shows all events in one embed window, events need to be sorted by date
@client.command()
async def showall(ctx):
    await ctx.send(embed=create_embed(sort_events()))


# This command will remove specified dates or events from the database
@commands.has_role("Bot admin")
@client.command()
async def remove(ctx, date, *events):
    try:
        # User provided a date and event(s)
        if len(date) != 0 and len(events) != 0:
            await ctx.send(f"Chystáš se smazat záznamy z databáze ({len(events)}). Jsi si jistý {ctx.message.author.mention}? (A/N)")  # Confirmation from user
            msg = await client.wait_for("message", check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)

            if msg.content.lower() in ("a", "ano"):
                event_list = db.get(date)
                for event in events:
                    if event in event_list:
                        event_list.remove(event)

                if len(db[date]) == 0:
                    del db[date]

                await ctx.send(f"Záznamy smazány, {ctx.message.author.mention}")
            else:
                await ctx.send(f"Akce zrušena, {ctx.message.author.mention}")
        # User provided only a date
        elif len(events) == 0:
            await ctx.send(f"Chystáš se smazat záznamy z databáze ({len(db[date])}). Jsi si jistý {ctx.message.author.mention}? (A/N)")  # Confirmation from user
            msg = await client.wait_for("message", check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)

            if msg.content.lower() in ("a", "ano"):
                del db[date]
            else:
                await ctx.send(f"Akce zrušena, {ctx.message.author.mention}")
        # Nothing provided
        else:
            await ctx.send(f"Neuvedl(a) jsi datum, {ctx.message.author.mention}")
    except KeyError:
        await ctx.send(f"Uvedl(a) jsi špatné datum, {ctx.message.author.mention}")


# This command will delete everything from a database
@commands.has_role("Bot admin")
@client.command()
async def removeall(ctx):
    if len(db) != 0:
        await ctx.send(f"Chystáš se smazat všechny záznamy z databáze ({len(db)}). Jsi si jistý {ctx.message.author.mention}? (A/N)")  # Confirmation from user
        msg = await client.wait_for("message", check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)

        if msg.content.lower() in ["a", "ano"]:
            for date in db.keys():
                del db[date]

            await ctx.send(f"Všechny záznamy smazány, {ctx.message.author.mention}")
        else:
            await ctx.send(f"Akce zrušena, {ctx.message.author.mention}")
    else:
        await ctx.send(f"Žádné záznamy k smazání, {ctx.message.author.mention}")


# This commands shows users how to use this bot
@client.command()
async def commands(ctx):
    embed_window = discord.Embed(title="Jak použít bota", 
                                 description="Bot se používá pomocí commandů. Seznam všech commandů je níže:", 
                                 color=0xfc050d)
    embed_window.add_field(name="!commands", 
                           value="Zobrazí tuto tabulku", 
                           inline=False)
    embed_window.add_field(name="!show DATUM", 
                           value="Zobrazí všechny události pro dané datum. `DATUM` musí být ve formátu `DD.MM.YYYY`", 
                           inline=False)
    embed_window.add_field(name="!showall", 
                           value="Zobrazí všechny události", 
                           inline=False)
    embed_window.add_field(name='!add DATUM "UDÁLOST" ("UDÁLOST_2")',
                           value='Přidá událost, `DATUM` je vyžadováno. `DATUM` musí být ve formátu `DD.MM.YYYY` a `UDÁLOST` musí být v uvozovkách, např.: `!add 25.10.2022 "Test ČJ"`. Více událostí musí být odděleno mezerou',
                           inline=False)
    embed_window.add_field(name='!remove DATUM ("UDÁLOST")',
                           value='Vymaže událost. `DATUM` je vyžadováno, např.: `!remove 13.01.2023` vymaže všechny události pro dané datum, `!remove 13.01.2023 "Test ČJ"` vymaže pouze danou událost pro dané datum',
                           inline=False)
    embed_window.add_field(name="!removeall", 
                           value="Vymaže úplně vše. Vyžaduje speciální roli", 
                           inline=False)

    await ctx.send(embed=embed_window)

client.run(token)
