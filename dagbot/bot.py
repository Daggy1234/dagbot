import asyncio
import os
import random
from datetime import datetime

import yaml

import aiohttp
import asyncpg
import discord
import sentry_sdk
from asyncdagpi.client import Client
from discord import AsyncWebhookAdapter, Webhook
from discord.ext import commands, menus, tasks
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from utils.badwordcheck import bword
from utils.caching import caching


async def get_prefix(bot, message):
    id = message.guild.id
    for e in bot.prefdict:
        if e["server_id"] == str(id):
            prefix = e["command_prefix"]
            break

    return commands.when_mentioned_or(prefix)(bot, message)


class Dagbot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix=get_prefix,
            description='The number 1 wanna be meme bot',
            case_insensitive=True,
            allowed_mentions=discord.AllowedMentions(
                roles=False,
                everyone=False))
        with open('./dagbot/data/credentials.yml', 'r') as file:
            self.data = yaml.load(file, Loader=yaml.FullLoader)
        self.caching = caching(self)
        self.dagpi = Client(self.data['dagpitoken'])
        self.bwordchecker = bword()
        self.bwordchecker.loadbword()
        self.useage = {}
        self.commands_called = 0
        # self.add_cog(Help(bot))
        self.load_extension("jishaku")
        extensions = [
            "text",
            "fun",
            "newimag",
            "reddit",
            "games",
            "util",
            "whysomart",
            "animals",
            "memes",
            "tags",
            "misc",
            "settings",
            "ai",
            "events",
            "errors",
            "developer",
            "help"
        ]
        for extension in extensions:
            try:
                self.load_extension(f"extensions.{extension}")
            except Exception as error:
                print(f"{extension} cannot be loaded due to {error}")
            else:
                print(f"loaded extension {extension}")
        self.before_invoke(self.starttyping)
        self.after_invoke(self.exittyping)
        self.loop.create_task(self.startdagbot())
        self.sentry = sentry_sdk.init(
            dsn=self.data['sentryurl'], integrations=[
                AioHttpIntegration()])
        self.run(self.data['token'])

    async def startdagbot(self):
        await self.makesession()
        await self.dbconnect()
        self.launch_time = datetime.utcnow()
        await self.caching.prefixcache()
        await self.get_cog("reddit").memecache()
        await self.caching.cogcache()
        await self.caching.getkeydict()

    async def makesession(self):
        self.session = aiohttp.ClientSession()
        print('made session')

    async def postready(self):
        webhook = Webhook.from_url(
            self.data['onreadyurl'],
            adapter=AsyncWebhookAdapter(
                self.session))
        await webhook.send('Dagbot is Online')

    async def dbconnect(self):
        self.pg_con = await asyncpg.connect(
            host=self.data['dbhost'],
            database=self.data['database'],
            user=self.data['user'],
            password=self.data['dbpassword'],
        )

    async def starttyping(self, ctx):
        ctx.typing = ctx.typing().__enter__()

    async def exittyping(self, ctx):
        ctx.typing.__exit__(None, None, None)

    async def on_command_completion(self, ctx):
        self.commands_called += 1
        try:
            self.useage[ctx.command.qualified_name] += 1
        except KeyError:
            self.useage[ctx.command.qualified_name] = 1

    async def on_ready(self):
        print('Dagbot is ready to roll')
