import requests
import datetime
import json
import logging
import sys
import random as r
from urllib.parse import urlparse
import re
import os
from config import GOOGLE_API_KEY
import natural
from natural import date

import discord
from discord.ext import commands
from discord.utils import get

FORMAT = "%Y-%m-%dT%H:%M:%SZ"
FORMAT2 = "%B %d, %H:%M UTC"

async def checkCalendar(message):
    today = datetime.datetime.utcnow()
    to_check = today.strftime(FORMAT)
    api_key = GOOGLE_API_KEY
    args = message.content.split(" ")
    if "!tournaments" in args:
        r = requests.get(f"https://www.googleapis.com/calendar/v3/calendars/rlbotofficial@gmail.com/events?maxResults=3&timeMin={to_check}&key={api_key}")
        jsons = r.json()
        if len(jsons["items"]) != 0:
            tournaments_embed = discord.Embed(color=discord.Color.green())
            events = []
            for raw_event in jsons["items"]:
                name, some_time, time_until = date_time_check(today, raw_event)
                verb_tense = "Will Begin in" if "now" in time_until else "Began"
                events.append({"name": name,
                               "some_time": some_time,
                               "time_until": time_until,
                               "verb_tense": verb_tense})
            events.sort(key=lambda ev: ev["time_until"])
            for event in events:
                tournaments_embed.add_field(name=event["name"],
                                            value=f'{event["verb_tense"]} {event["time_until"]}. ({event["some_time"]})',
                                            inline=False)
        else:
            tournaments_embed = discord.Embed(
                description=f"No tournaments currently scheduled, if any are, they will appear here!",
                color=discord.Color.red())

        tournaments_embed.set_author(name="Upcoming Tournaments",
                                     icon_url="https://cdn.discordapp.com/avatars/474703464199356447/720a25621983c452cf71422a51b733a1.png?size=128",
                                     url="http://rlbot.org/tournament/")
        tournaments_embed.set_footer(text="http://rlbot.org/tournament/")
        tournaments_embed.url = "http://rlbot.org/tournament/"
        await message.channel.send(" ", embed=tournaments_embed)


def date_time_check(today, event):
    names = event["summary"]
    start = event["start"]["dateTime"]
    new_date = datetime.datetime.strptime(start, FORMAT)
    try:
        recurrence = event["recurrence"][0].split(";")
        rec_type = recurrence[0].split("=")[1]
        num_recs = recurrence[2].split("=")[1]
        if rec_type == "WEEKLY":
            for i in range(int(num_recs)):
                if new_date > today:
                    break
                new_date += datetime.timedelta(days=7)
        elif rec_type == "MONTHLY":
            for i in range(int(num_recs)):
                if new_date > today:
                    break
                new_date += datetime.timedelta(weeks=4)
    except:
        pass
    some_times = new_date.strftime(FORMAT2)
    time_untils = date.duration(new_date, now=today, precision=3)
    return (names, some_times, time_untils)
