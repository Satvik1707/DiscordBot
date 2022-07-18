import os
import io
import ksoftapi
from googletrans import Translator, LANGUAGES
from textwrap import TextWrapper

import discord
from discord.ext import commands

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = bot.client
        self.kclient = bot.kclient
        self.trans = Translator()

    @commands.command(name='define')
    async def _define(self, ctx, word=None):
        """Word Dictionary"""
        if not word:
            return await ctx.send('Please specify word :pager:')
        url = os.environ['HexApi'] + 'dictionary?word=' + word
        async with ctx.typing():
            async with self.client.get(url) as r:
                if r.status != 200:
                    return await ctx.send('Definition not found :bookmark_tabs:')
                results = await r.json()
            description = []
            emoji = ''
            for r in results:
                res = []
                if r['type']:
                    res.append(f"`{r['type']}`")
                res.append(f"{r['definition']}")
                if r['example']:
                    res.append(f"\n*{r['example'].replace('<b>', '**').replace('</b>', '**')}*")
                if r['image_url']:
                    async with self.client.get(r['image_url']) as r1:
                        if r1.status == 200:
                            image = io.BytesIO(await r1.read())
                            image = discord.File(image, 'image.png')
                if r['emoji']:
                    emoji = r['emoji'] + ' '

                description.append(' '.join(res))
            em = discord.Embed(title=f"{emoji}{word}", description='\n'.join(description), color=discord.Color(0xFF9933))
        try:
            em.set_thumbnail(url='attachment://image.png')
            await ctx.send(embed=em, file=image)
        except:
            await ctx.send(embed=em)

    @commands.command(name='trace', aliases=['ip'])
    async def trace(self, ctx, ip: str=""):
        """Trace ip"""
        if ip=="":
            return await ctx.send("Please enter an `IP` address :satellite:")

        try:
            async with ctx.typing():
                info = await self.kclient.kumo.trace_ip(ip)
        except (ksoftapi.NoResults, ksoftapi.errors.APIError):
            await ctx.send('Unable to locate :x:\nEnter valid IP')
        else:
            details = [['City', 'city'], ['Continent code', 'continent_code'], ['Continent name', 'continent_name'], ['Country code', 'country_code'], ['Country_name', 'country_name'], ['DMA code', 'dma_code'], ['Latitude', 'latitude'], ['Longitude', 'longitude'], ['Postal code', 'postal_code'], ['Region', 'region'], ['Timezone', 'time_zone']]
            description = []
            for i in details:
                description.append(f'{i[0]}: `{getattr(info, i[1])}`')
            description.append(f':map:Map: [GoogleMaps]({info.gmap})')

            embed = discord.Embed(title=":satellite_orbital: IP information:", colour=discord.Colour(0xff00cc), description="\n".join(description))
            embed.set_footer(text=ip, icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)

    @commands.command(name='translate')
    async def translate(self, ctx, *args):
        """Translator"""
        if len(args)>0:
            if args[0]=='--list':
                lang = ''
                for l in LANGUAGES:
                    lang = lang+str(l)+' ('+str(LANGUAGES[l]).title()+')\n'
                embed = discord.Embed(title='List of supported languages', description=str(lang), color=discord.Color(0x5DADEC))
                await ctx.send(embed=embed)
            elif len(args)>1:
                destination = args[0]
                try:
                    toTrans = ' '.join(args[1:len(args)])
                except IndexError:
                    await ctx.send('No text to translate :x:')
                try:
                    async with ctx.typing():
                        translation = self.trans.translate(toTrans, dest=destination)
                    embed = discord.Embed(description=translation.text, color=discord.Color(0x5DADEC))
                    embed.set_footer(text=f'Translated {LANGUAGES[translation.src]} to {LANGUAGES[translation.dest]}.', icon_url='https://i.ibb.co/1np1s8P/translate.png')
                    await ctx.send(embed=embed)
                except:
                    return await ctx.send('Unable to translate :x:\nMaybe language id was wrong')
            else:
                await ctx.send(content='Please add a language id\nType `~translate --list` for the list')
        else:
            await ctx.send(content='Please add translations\neg.`~translate en Hola`\nType `~translate --list` for supported languages.')

    @commands.command(name='sinfo', aliases=['server'])
    async def serverinfo(self, ctx, *, name:str = ""):
        """Get server info"""
        if name:
            server = None
            try:
                server = self.bot.get_guild(int(name))
                if not server:
                    return await ctx.send('Server not found :satellite_orbital:')
            except:
                for i in self.bot.guilds:
                    if i.name.lower() == name.lower():
                        server = i
                        break
                if not server:
                    return await ctx.send("Server not found :satellite_orbital: or maybe I'm not in it")
        else:
            server = ctx.guild

        # Count channels
        tchannel_count = len([x for x in server.channels if type(x) == discord.channel.TextChannel])
        vchannel_count = len([x for x in server.channels if type(x) == discord.channel.VoiceChannel])
        # Count roles
        role_count = len(server.roles)
        # Count emojis
        emojis = len(server.emojis)
        # Count bots
        bot_count = len([x for x in server.members if x.bot])

        # Create embed
        em = discord.Embed(color=0x00CC99)
        em.set_author(name='Server Info:', icon_url=server.owner.avatar_url)
        em.add_field(name='Name', value=f'`{server.name}`')
        em.add_field(name='Owner', value=f'`{server.owner}`', inline=False)
        em.add_field(name='Members', value=f'`{server.member_count - bot_count}`')
        em.add_field(name='Bots', value=f'`{bot_count}`')
        em.add_field(name='Emojis', value=f'`{emojis}`')
        em.add_field(name='Text Channels', value=f'`{tchannel_count}`')
        em.add_field(name='Voice Channels', value=f'`{vchannel_count}`')
        em.add_field(name='Verification Level', value=f'`{str(server.verification_level).title()}`')
        em.add_field(name='Number of roles', value=f'`{role_count}`')
        em.add_field(name='Highest role', value=f'`{server.roles[-1]}`')
        em.add_field(name='Region', value=f'`{str(server.region).title()}`')
        em.add_field(name='Created At', value=f"`{server.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S')}`", inline=False)
        em.set_thumbnail(url=server.icon_url)
        em.set_footer(text='Server ID: %s' % server.id)

        await ctx.send(embed=em)

    @commands.command(name = 'userinfo', aliases=['user', 'uinfo', 'ui'])
    async def userinfo(self, ctx, *, name=""):
        """Get user info. Ex: ~user @user"""
        if name:
            try:
                user = ctx.message.mentions[0]
            except IndexError:
                user = ctx.guild.get_member_named(name)
            try:
                if not user:
                    user = ctx.guild.get_member(int(name))
                if not user:
                    user = self.bot.get_user(int(name))
            except ValueError:
                pass
            if not user:
                await ctx.send('User not found :man_frowning_tone1:')
                return
        else:
            user = ctx.message.author

        if isinstance(user, discord.Member):
            role = user.top_role.name
            if role == "@everyone":
                role = "N/A"
            voice_state = None if not user.voice else user.voice.channel

        em = discord.Embed(colour=0x00CC99)
        em.add_field(name='User ID', value=f'`{user.id}`')
        if isinstance(user, discord.Member):
            if isinstance(user.activity, discord.Spotify):
                activity = "Listening " + user.activity.title
            elif user.activity is not None: 
                activity = str(user.activity.type)[13:].title() + ' ' + user.activity.name
            else:
                activity = None

            em.add_field(name='Nick', value=f'`{user.nick}`')
            em.add_field(name='Status', value=f'`{user.status}`')
            em.add_field(name='In Voice', value=f'`{voice_state}`')
            em.add_field(name='Activity', value=f'`{activity}`')
            em.add_field(name='Highest Role', value=f'`{role}`')
        em.add_field(name='Account Created', value=f"`{user.created_at.__format__('%A, %d %B %Y @ %H:%M:%S')}`", inline=False)
        if isinstance(user, discord.Member):
            em.add_field(name='Join Date', value=f"`{user.joined_at.__format__('%A, %d %B %Y @ %H:%M:%S')}`", inline=False)
        em.set_thumbnail(url=user.avatar_url)
        em.set_author(name=user, icon_url=user.avatar_url)
        
        try:
            await ctx.send(embed=em)
        except Exception:
            await ctx.send("I don't have permission to send embeds here :disappointed_relieved:")

    @commands.command(name='weather')
    async def weather(self, ctx, *, location=None):
        """Get weather"""
        if not location:
            return await ctx.send('Please provide location :map:')
        url = os.environ['HexApi'] + f'weather?location={location}'
        await ctx.trigger_typing()
        async with self.client.get(url) as r:
            if r.status != 200:
                return await ctx.send('Failed to get weather :x:')
            data = await r.json()

        em = discord.Embed(title="Weather", color=discord.Color.random())
        icon = "https://" + data["current"]["condition"]["icon"][2:]
        em.set_thumbnail(url=icon)

        location = ', '.join([data["location"][i] for i in ["name", "region", "country"]])
        gmap = f"[🗺](https://www.google.com/maps/search/?api=1&query='{location}')"
        gmap = gmap.replace("'", "%22");gmap = gmap.replace(" ", "%20")
        infos = [["temp_c", "Temperature", "°C"], ["feelslike_c", "Feels like", "°C"], ["humidity", "Humidity", "%"],
                ["pressure_mb", "Pressure", "mbar"], ["cloud", "Cloud", "%"], ["precip_mm", "Precipitation", "mm"], ["uv", "UV", ""]]
        info = [f'{gmap} **{location}**\n']

        for i in infos:
            info.append(f"{i[1]}: `{data['current'][i[0]]} {i[2]}`")
        info.append(f"Wind: `{data['current']['wind_kph']}({data['current']['wind_dir']}) Km/h`")
        em.description = '\n'.join(info)

        await ctx.send(embed=em)

    @commands.command(name='wordinfo', aliases=['pronunciation', 'pron', 'word'])
    async def wordinfo(self, ctx, word=""):
        if not word:
            return await ctx.send("Specify a word :thought_balloon:")

        url = os.environ['HexApi'] + 'wordinfo?word=' + word.strip()
        async with ctx.typing():
            async with self.client.get(url) as r:
                if r.status != 200:
                    return ctx.send('Failed to get info :x:')
                data = await r.json()
            result = [f"**Word:** {data['word']}"]
            result.append(f"**Pronunciation:** {data['ipa']}")
            result.append(f"**Frequency:** {data['freq']}")
            if 'a' in data['flags']:
                result.append("**Offensive:** Yes")
            else:
                result.append("**Offensive:** No")
        await ctx.send('\n'.join(result))


def setup(bot):
    bot.add_cog(Utility(bot))
