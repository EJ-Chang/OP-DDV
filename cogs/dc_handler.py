import discord
from discord import app_commands
from discord.ext import commands


class Dc_handler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{__name__} is online!')




    # @app_commands.command(name='greet', description='Greet the user.')
    # async def greet(self, interaction: discord.Interaction):
    #   response = 'Hello, I am your discord bot'
    #   await interaction.response.send_message(response)
    @commands.command(name='fetch_reply')
    async def fetch_reply(self, ctx):
        # 檢查是否有回覆某條消息
        if ctx.message.reference:
            # 抓取被回覆的消息的 ID
            replied_message = await ctx.channel.fetch_message(
                ctx.message.reference.message_id)

            # 發送回覆消息的內容和發送時間
            await ctx.send(
                f"Replied message content: {replied_message.content}\nSent at: {replied_message.created_at}"
            )
            await ctx.send(f"Replied message ID: {replied_message.id}")
        else:
            await ctx.send("You did not reply to any message.")


async def setup(bot):
    await bot.add_cog(Dc_handler(bot))
