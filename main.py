import discord
from discord.ext import commands
import regex
# from data import *

token = ""
intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix="!", intents=intents)


def is_date_valid(date_str):
    return bool(regex.fullmatch(r"^(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]|(?:Jan|Mar|May|Jul|Aug|Oct|Dec)))\1|(?:(?:29|30)(\/|-|\.)(?:0?[1,3-9]|1[0-2]|(?:Jan|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec))\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)(?:0?2|(?:Feb))\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9]|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep))|(?:1[0-2]|(?:Oct|Nov|Dec)))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})$", date_str))


def date_already_exists(date_str, events_dict):
    return date_str in events_dict.keys()


def sort_events(all_events_dict, all_sorted_events_dict):
    sorted_event_keys = sorted(all_events_dict, key=lambda x: list(map(int, x.split('.')))[::-1])
    for date in sorted_event_keys:
        all_sorted_events_dict[date] = all_events_dict.get(date)

    return all_sorted_events_dict


@client.event
async def on_ready():
    print("The bot is ready")
    global all_events, sorted_events
    all_events = {}
    sorted_events = {}


@client.command()
@commands.has_role("Bot admin")
async def test(ctx, *arg):
    if len(arg) != 0:
        arguments = ", ".join(arg)
        await ctx.send(arguments)


@client.command()
@commands.has_role("Bot admin")
async def add(ctx, *args):
    if len(args) != 0:
        arguments = ', '.join(args).split(", ")
        date = arguments[0]

        if is_date_valid(date):
            if date_already_exists(date, all_events):
                all_events[date] += arguments[1:]
            else:
                all_events[date] = arguments[1:]

            await ctx.send(sort_events(all_events, sorted_events))
            # await ctx.send(all_events)
        else:
            await ctx.send(f"Uvedl(a) jsi špatné datum. Datum musí být ve formátu `YYYY-MM-DD`, {ctx.message.author.mention}")
    else:
        await ctx.send(f"Neuvedl(a) jsi žádné argumenty, {ctx.message.author.mention}")


@client.command()
async def commands(ctx):
    embed_window = discord.Embed(title="Jak použít bota", description="Bot se používá pomocí commandů. Seznam všech commandů je níže:", color=0xfc050d)
    embed_window.add_field(name="`!commands`", value="Zobrazí tuto tabulku", inline=False)
    embed_window.add_field(name='`!add DATUM "UDÁLOST"`',
                           value='Přidá událost. `DATUM` musí být ve formátu `DD.MM.YYYY`, např.: `!add 25.10.2022 "Test ČJ"`. Více událostí musí být odděleno čárkou',
                           inline=False)
    embed_window.add_field(name='`!remove DATUM ("UDÁLOST")`',
                           value='Vymaže událost. `DATUM` je vyžadováno, např.: `!remove 13.01.2023` vymaže všechny události, `!remove 13.01.2023 "Test ČJ"` vymaže pouze danou událost',
                           inline=False)
    await ctx.send(embed=embed_window)


client.run(token)
