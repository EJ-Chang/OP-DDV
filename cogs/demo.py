import discord
from discord import app_commands
from discord.ext import commands


# cog: 創造 Demo
class Demo(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # listen to this cog
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.__class__.__name__} is online!')

    # app commands in this cog
    # 先用 button 選要哪個功能的示範
    # 按照選項，提供相對應的 embed message
    @app_commands.command(name="demo_ddv", description="DDV 的功能示範")
    async def demo_ddv(self, interaction: discord.Interaction):

        # write my embed message here (demo message)
        embed = discord.Embed(title=":compass: DEMO")
        embed.add_field(name=":one: 指令: /select_stream",
                        value="直接送出即可，選擇想要查詢的頻道，\
                        機器人會回傳該實況主最近的三個 VOD。目前列表以子午藝人為多數。",
                        inline=False)
        embed.add_field(name=":two: 指令: /time_travel",
                        value="需要手動輸入實況主的 Twitch 帳號，\
                        也就是頻道連結: twitch.tv/斜線後面這段，\
                        再逐項輸入日期時間即可。須注意時間為24小時制。",
                        inline=False)
        embed.add_field(name=":three: 右鍵選單指令 :new:",
                        value="邀請 DDV 到頻道或私聊後，對任意訊息點右鍵\
                       -->應用程式-->可以選擇直接換算KSP/SEKI在該訊息\
                       當下的 VOD 連結。此訊息只會給你自己看到，不必擔心吵到別人。",
                        inline=False)

        await interaction.response.send_message(embed=embed)


# 將這個 cog 加入到 bot 裡面
async def setup(bot):
    await bot.add_cog(Demo(bot))
