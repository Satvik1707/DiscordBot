import os
import io
import asyncio
import random
import fortune

import discord
from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = bot.client

    @commands.command(name='advice')
    async def advice(self, ctx):
        """Random Advice generator"""
        url = os.environ['HexApi'] + 'advice'
        async with ctx.typing():
            async with self.client.get(url) as r:
                if r.status != 200:
                    return ctx.send('Unable to generate advice :disappointed_relieved')
                data = await r.json()

        await ctx.send(data['slip']['advice'])

    @commands.command(name='bored', aliases=['suggest'])
    async def suggest(self, ctx):
        """Random Suggestions"""
        url = os.environ['HexApi'] + 'activity'
        async with ctx.typing():
            async with self.client.get(url) as r:
                if r.status != 200:
                    return await ctx.send('Unable to get suggestions :disappointed_relieved:')
                data = await r.json()

        desc = []
        desc.append(f"**Type:** `{data['type'].title()}`")
        desc.append(f"**Participants:** `{data['participants']}`")
        desc.append(f"**Price:** `{data['price']}`")
        desc.append(f"**Accessibility:** `{data['accessibility']}`")
        em = discord.Embed(color=discord.Color(0xAAF0D1), description='\n'.join(desc))
        em.set_author(name=data['activity'], url=data['link'])
        em.set_footer(text=f"Suggestion for {ctx.message.author.display_name}", icon_url=ctx.message.author.avatar_url)

        await ctx.send(embed=em)

    @commands.command(name='comic', aliases=['comics', 'comicstrip'])
    async def comic(self, ctx, cid=None):
        """Get comic strip"""
        if not cid:
            return await ctx.send('Please specify comic id\nType `~comic --list` for list.')
        url = os.environ['HexApi'] + 'comic'
        if cid.lower()=='--list':
            params = {'list': 1}
            async with ctx.typing():
                async with self.client.get(url, params=params) as r:
                    if r.status != 200:
                        return await ctx.send('Failed to get comic list :x:')
                    result = await r.json()

            data = [f"**{i}** {comic_name.title()}" for i, comic_name in enumerate(result['comics'], 1) if comic_name in result['featured']]
            em = discord.Embed(color=discord.Color(0xFF5470), title="Comic list:")
            em.description= '**Popular:**\n' + '\n'.join(data)
            em.set_footer(text="Click next for complete list")
            cmsg = await ctx.send(embed=em)

            result = result['comics']
            data = [f"**{i}** {comic_name.title()}" for i, comic_name in enumerate(result, 1)]
            page = 0
            for i in ['⬅', '❌', '➡']:
                await cmsg.add_reaction(i)
            def check(reaction, user):
                return (
                    (user != self.bot.user) 
                    and (str(reaction.emoji) in ['⬅', '➡', '❌']) 
                    and (reaction.message.id == cmsg.id)
                    )
            while True:
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
                except asyncio.TimeoutError:
                    await cmsg.clear_reactions()
                    return
                else:
                    if str(reaction.emoji) == '➡':
                        await cmsg.remove_reaction(reaction, user)
                        if page < 0--len(result)//15:
                            page += 1
                    elif str(reaction.emoji) == '⬅':
                        await cmsg.remove_reaction(reaction, user)
                        if page > 1:
                            page -= 1
                    else:
                        await cmsg.delete(delay=0.0)
                        return

                    if page < 1:
                        page = 1
                    start = (page-1) * 15
                    end = start + 15
                    page_data = data[start:end]
                    em.description = '\n'.join(page_data)
                    em.set_footer(text=f"Page {page}/{0--len(result)//15}")
                    await cmsg.edit(embed=em)

        else:
            params = {'id': cid}
            async with ctx.typing():
                async with self.client.get(url, params=params) as r:
                    if r.status != 200:
                        return await ctx.send('Failed to get comic :x:\nMaybe id is invalid\nType `~comic --list` for list.')
                    data = io.BytesIO(await r.read())

            await ctx.send(file=discord.File(data, 'comic.png'))

    @commands.command(name='filter', aliases=['blur', 'invert', 'b&w', 'deepfry', 'sepia', 'pixelate', 'magik', 'jpegify', 'wide', 'snow', 'gay', 'communist'])
    async def filter(self, ctx, arg='', image_link=''):
        """Deepfry avatar"""
        filters = ['b&w', 'blur', 'charcoal', 'communist', 'deepfry', 'edge', 'emboss', 'gay', 'glitch', 'implode', 'invert', 
                   'jpegify', 'magik', 'pixelate', 'primitive', 'sepia', 'sketch', 'snow', 'spread', 'swirl', 'wave', 'wide']
        if arg == '--list':
            return await ctx.send(embed=discord.Embed(title='Filters', description='\n'.join(filters)))
        if arg not in filters:
            return await ctx.send("Invalid filter name\nUse `~filter --list` for all options")
        
        if not image_link:
            user = ctx.message.author
            image_link = user.avatar_url_as(format='png', size=512)
        try:
            user = ctx.message.mentions[0]
            image_link = user.avatar_url_as(format='png', size=512)
        except IndexError:
            pass

        url = os.environ['HexApi'] + 'filter'
        params = {'name': arg, 'image': str(image_link)}
        async with ctx.typing():
            async with self.client.get(url, params=params) as r:
                if r.status != 200:
                    return await ctx.send("Failed :x:\nMaybe url is wrong :link:")
                data = io.BytesIO(await r.read())

        await ctx.send(file=discord.File(data, 'filter.png'))

    @commands.command(name='fortune', aliases=['cookie', 'quote', 'fact', 'factoid'])
    async def fortune(self, ctx, category='random'):
        """Fortune Cookie! (You can also specify category[factoid,fortune,people])"""
        categories = ['fortune', 'factoid', 'people']
        if category in categories:
            await ctx.send(f"```fix\n{fortune.get_random_fortune(f'fortunes/{category}')}\n```")
        else:
            await ctx.send(f"```fix\n{fortune.get_random_fortune(f'fortunes/{random.choice(categories)}')}\n```")


    @commands.command(name='uselessweb', aliases=['website'])
    async def uselessweb(self, ctx):
        """Get a random website"""
        url = os.environ['HexApi'] + "uselesssites"
        async with ctx.typing():
            async with self.client.get(url) as r:
                if r.status != 200:
                    return await ctx.send('Failed to get website :x:')
                data = await r.json()
        await ctx.send(data['url'])

    @commands.command(name='wallpaper', aliases=['wall'])
    async def _wallpaper(self, ctx, *query: str):
        """Get wallpaper from Unsplash"""
        headers = {'Authorization': os.environ['Unsplash_Token']}
        params = {'count': 1}
        if query:
            params['query'] = query
        else:
            params['count'] = 3
            params['featured'] = 'yes'
        url = 'https://api.unsplash.com/photos/random'
        async with self.client.get(url, params=params, headers=headers) as r:
            if r.status != 200:
                return await ctx.send('Error getting wallpaper :disappointed_relieved:')
            results = await r.json()
        for r in results:
            em = discord.Embed(color=discord.Color(0xFF355E))
            em.set_author(name=r['user']['name'], url=f"{r['user']['links']['html']}?utm_source=HexBot&utm_medium=Discord", icon_url=r['user']['profile_image']['small'])
            em.set_image(url=r['urls']['raw'])
            em.set_footer(text='Source: Unsplash')
            await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Fun(bot))
