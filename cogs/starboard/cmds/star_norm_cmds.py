#!/usr/bin/env python3.6
from discord.ext import commands
import discord, importlib, re, datetime, typing
import common.star_utils as star_utils
import common.utils as utils

class StarNormCMDs(commands.Cog, name = "Normal Star"):
    def __init__(self, bot):
        self.bot = bot

    def get_star_rankings(self, ctx):
        def by_stars(elem):
            return elem[1]

        user_star_dict = {}
        guild_entries = [self.bot.starboard[k] for k in self.bot.starboard.keys() 
        if self.bot.starboard[k]["guild_id"] == ctx.guild.id]

        if guild_entries != []:
            for entry in guild_entries:
                if entry["author_id"] in user_star_dict.keys():
                    user_star_dict[entry["author_id"]] += star_utils.get_num_stars(entry)
                else:
                    user_star_dict[entry["author_id"]] = star_utils.get_num_stars(entry)

            user_star_list = list(user_star_dict.items())
            user_star_list.sort(reverse=True, key=by_stars)

            return user_star_list
        else:
            return None

    def get_user_placing(self, user_star_list, author_id):
        author_entry = [e for e in user_star_list if e[0] == author_id]
        if author_entry != []:
            author_index = user_star_list.index(author_entry[0])
            return f"position: #{author_index + 1} with {author_entry[0][1]} ⭐"
        else:
            return "position: N/A - no stars found!"

    
    async def cog_check(self, ctx):
        return self.bot.config[ctx.guild.id]["star_toggle"]        

    @commands.cooldown(1, 5, commands.BucketType.member)
    @commands.command(aliases = ["msgtop"])
    async def msg_top(self, ctx):
        """Allows you to view the top 10 starred messages on a server. Cooldown of once every 5 seconds per user."""

        def by_stars(elem):
            return star_utils.get_num_stars(elem)

        guild_entries = [self.bot.starboard[k] for k in self.bot.starboard.keys() if self.bot.starboard[k]["guild_id"] == ctx.guild.id]
        if guild_entries != []:
            top_embed = discord.Embed(title=f"Top starred messages in {ctx.guild.name}", colour=discord.Colour(0xcfca76), timestamp=datetime.datetime.utcnow())
            top_embed.set_author(name=f"{self.bot.user.name}", icon_url=f"{str(ctx.guild.me.avatar_url_as(format=None,static_format='jpg', size=128))}")
            top_embed.set_footer(text="As of")

            starboard_id = self.bot.config[ctx.guild.id]['starboard_id']

            guild_entries.sort(reverse=True, key=by_stars)

            for i in range(len(guild_entries)):
                if i > 9:
                    break

                entry = guild_entries[i]
                url = f"https://discordapp.com/channels/{ctx.guild.id}/{starboard_id}/{entry['star_var_id']}"
                num_stars = star_utils.get_num_stars(entry)
                member = await utils.user_from_id(self.bot, ctx.guild, entry['author_id'])
                author_str = f"{member.display_name} ({str(member)})" if member != None else f"User ID: {entry['author_id']}"

                top_embed.add_field(name=f"#{i+1}: {num_stars} ⭐ from {author_str}", value=f"[Message]({url})\n", inline=False)

            await ctx.send(embed=top_embed)
        else:
            await ctx.send("There are no starboard entries for this server!")

    @commands.cooldown(1, 5, commands.BucketType.member)
    @commands.command(name = "top", aliases = ["leaderboard", "lb"])
    async def top(self, ctx):
        """Allows you to view the top 10 people with the most stars on a server. Cooldown of once every 5 seconds per user."""

        user_star_list = self.get_star_rankings(ctx)

        if user_star_list != None:
            top_embed = discord.Embed(title=f"Star Leaderboard for {ctx.guild.name}", colour=discord.Colour(0xcfca76), timestamp=datetime.datetime.utcnow())
            top_embed.set_author(name=f"{self.bot.user.name}", icon_url=f"{str(ctx.guild.me.avatar_url_as(format=None,static_format='jpg', size=128))}")

            for i in range(len(user_star_list)):
                if i > 9:
                    break
                entry = user_star_list[i]

                member = await utils.user_from_id(self.bot, ctx.guild, entry[0])
                num_stars = entry[1]
                author_str = f"{member.display_name} ({str(member)})" if member != None else f"User ID: {entry[0]}"

                top_embed.add_field(name=f"#{i+1}: {author_str}", value=f"{num_stars} ⭐\n", inline=False)

            top_embed.set_footer(text=f"Your {self.get_user_placing(user_star_list, ctx.author.id)}")
            await ctx.send(embed=top_embed)
        else:
            await ctx.send("There are no starboard entries for this server!")

    @commands.cooldown(1, 5, commands.BucketType.member)
    @commands.command(aliases = ["position", "place", "placing"])
    async def pos(self, ctx, user_mention: typing.Optional[discord.Member]):
        """Allows you to get either your or whoever you mentioned’s position in the star leaderboard (like the top command, but only for one person)."""

        member = ctx.author if user_mention == None else user_mention

        if member != None:
            user_star_list = self.get_star_rankings(ctx)

            if user_star_list != None:
                if user_mention != None:
                    placing = f"{member.display_name}'s {self.get_user_placing(user_star_list, member.id)}"
                else:
                    placing = f"Your {self.get_user_placing(user_star_list, member.id)}"

                place_embed = discord.Embed(colour=discord.Colour(0xcfca76), description=placing, timestamp=datetime.datetime.utcnow())
                place_embed.set_author(name=f"{self.bot.user.name}", icon_url=f"{str(ctx.guild.me.avatar_url_as(format=None,static_format='jpg',size=128))}")
                place_embed.set_footer(text="Sent")

                await ctx.send(embed=place_embed)
            else:
                await ctx.send("There are no starboard entries for this server!")
        else:
            await ctx.send("I could not get the user you were trying to get. Please try again with a valid user.")

def setup(bot):
    importlib.reload(star_utils)
    importlib.reload(utils)
    
    bot.add_cog(StarNormCMDs(bot))