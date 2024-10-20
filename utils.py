import json
import os
from datetime import datetime, timedelta

import discord
import pytz  # 用來處理時區
import requests

TWITCH_TOKEN = os.environ['TWITCH_TOKEN']
TWITCH_CLIENT_ID = os.environ['TWITCH_CLIENT_ID']


# Get info from Twitch
async def get_twitch_user_info(user_name):
    url = f'https://api.twitch.tv/helix/users?login={user_name}'
    headers = {
        'Client-ID': TWITCH_CLIENT_ID,
        'Authorization': f'Bearer {TWITCH_TOKEN}'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()['data'][0]  # 返回用戶資料
    else:
        print(f"Error fetching user info: {response.status_code}")
        return None


# Get all past streams (VODs)
async def get_all_past_streams(user_id):
    url = f'https://api.twitch.tv/helix/videos?user_id={user_id}&type=archive'
    headers = {
        'Client-ID': TWITCH_CLIENT_ID,
        'Authorization': f'Bearer {TWITCH_TOKEN}'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if 'data' in data and len(data['data']) > 0:
            return data['data']  # 返回所有 VOD 的資料
        else:
            print("No past streams found.")
            return None
    else:
        print(f"Error fetching past streams: {response.status_code}")
        return None


# discord to twitch api datetime converter


def discord_to_twitch_datetime(discord_time) -> datetime:
    """將 Discord 的 message.created_at 轉換為符合 Twitch API 的 UTC datetime 物件。"""
    # 確保時間是 UTC，並刪除微秒部分
    twitch_datetime = discord_time.replace(microsecond=0, tzinfo=pytz.utc)
    return twitch_datetime


# Convert VOD timestamp to datetime object
def parse_duration(duration_str: str) -> timedelta:
    hours = minutes = seconds = 0

    if 'h' in duration_str:
        hours, duration_str = duration_str.split('h', 1)
        hours = int(hours)

    if 'm' in duration_str:
        minutes, duration_str = duration_str.split('m', 1)
        minutes = int(minutes)

    if 's' in duration_str:
        seconds = int(duration_str.replace('s', ''))

    return timedelta(hours=hours, minutes=minutes, seconds=seconds)


# check streaming status and vod
async def check_stream(user_id, target_time_utc: datetime):
    vods = await get_all_past_streams(user_id)

    if not vods:
        return None  # 若無法取得 VOD 資訊，直接返回

    for vod in vods:
        # 將 Twitch API 提供的 ISO 時間轉為 datetime 物件
        start_time_utc = datetime.fromisoformat(vod['created_at'].replace(
            'Z', '+00:00'))

        # 計算 VOD 的結束時間
        duration = parse_duration(vod['duration'])
        end_time_utc = start_time_utc + duration

        # 檢查目標時間是否在直播期間內
        if start_time_utc <= target_time_utc <= end_time_utc:
            timestamp_seconds = int(
                (target_time_utc - start_time_utc).total_seconds())
            return vod['url'], timestamp_seconds, vod['title']

    return None  # 若沒有符合的 VOD，返回 None


# 組裝 vod embed message
def create_vod_embed(user_name: str, user_id: str, avatar_url: str,
                     target_time_utc: datetime, vod_url, timestamp_seconds,
                     vod_title) -> discord.Embed:
    """組裝 Twitch VOD 查詢的 Discord embed 訊息。"""
    # embed = discord.Embed(title=f"{user_name}'s Info")
    embed = discord.Embed(title=f'VOD 時光機@{user_name}')
    embed.set_thumbnail(url=avatar_url)
    embed.add_field(name='UserID is:', value=f'{user_id}', inline=False)
    embed.add_field(name='您查詢的時間是:',
                    value=f'{discord.utils.format_dt(target_time_utc)}',
                    inline=False)

    if vod_url:
        # 如果有開台，添加帶有時間戳的 VOD 連結
        timestamp_url = f"{vod_url}?t={timestamp_seconds}s"
        embed.add_field(name="Stream Status", value="當時正在開台", inline=False)
        embed.add_field(name="實況連結(帶有時間戳記)",
                        value=f"[{vod_title}]({timestamp_url})",
                        inline=False)
    else:
        embed.add_field(name="Stream Status", value="當時沒有開台", inline=False)

    return embed



# 讀取 JSON 檔案中的實況主資料
def load_streamer_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)['streamers']


# 將 HEX 顏色轉換為 Discord 支援的顏色格式
def hex_to_rgb_int(hex_color):
    hex_color = hex_color.lstrip('#')  # 移除 #
    return int(hex_color, 16)  # 將HEX轉為整數
