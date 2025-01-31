import discord
import os
import requests
from bs4 import BeautifulSoup
import asyncio

# Khởi tạo intents
intents = discord.Intents.default()  # Đây là các intents mặc định
intents.messages = True  # Cho phép bot nhận sự kiện tin nhắn

# Khởi tạo client Discord với intents
client = discord.Client(intents=intents)

CHANNEL_ID = '1313488832716603424'  # ID của kênh Discord để gửi thông tin

# URL trang web
URL = 'https://kodoani.com/tin-tuc-anime'

# Tập hợp để lưu trữ các bài viết đã gửi
sent_posts = set()

def fetch_latest_news():
    # Gửi yêu cầu HTTP để lấy dữ liệu trang web
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Lấy tất cả các bài viết trong trang
    posts = soup.find_all('div', class_='col-sm-3 menu-post-item')

    # Lọc ra bài viết trong 1 phút gần nhất
    latest_posts = []

    for post in posts:
        # Lấy thông tin thời gian đăng bài
        time_span = post.find('span')
        if time_span:
            time_text = time_span.get_text().strip()

            # Kiểm tra nếu bài viết đăng từ 1 phút trước
            if 'phút' in time_text:
                minutes_ago = int(time_text.split()[0])
                if minutes_ago <= 1:
                    # Lấy thông tin tiêu đề và ảnh
                    title = post.find('img')['alt']
                    image_url = post.find('img')['data-src']
                    link = post.find('a')['href']

                    # Lưu lại thông tin bài viết
                    latest_posts.append({
                        'title': title,
                        'image_url': image_url,
                        'link': link
                    })

    return latest_posts

async def send_to_discord(posts):
    # Kết nối tới kênh Discord và gửi tin nhắn
    channel = client.get_channel(int(CHANNEL_ID))
    for post in posts:
        # Kiểm tra xem bài viết đã được gửi chưa
        if post['link'] not in sent_posts:
            embed = discord.Embed(
                title=post['title'],
                url=post['link'],
                color=discord.Color.blue()
            )
            embed.set_image(url=post['image_url'])
            await channel.send(embed=embed)
            # Thêm bài viết vào danh sách đã gửi
            sent_posts.add(post['link'])

async def check_for_new_posts():
    while True:
        # Lấy bài viết mới nhất và gửi lên Discord
        latest_posts = fetch_latest_news()
        if latest_posts:
            await send_to_discord(latest_posts)
        else:
            print("Không có bài viết mới trong vòng 1 phút.")
        
        # Chờ 60 giây trước khi kiểm tra lại
        await asyncio.sleep(60)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    # Bắt đầu công việc kiểm tra mỗi phút
    client.loop.create_task(check_for_new_posts())

# Chạy bot Discord
client.run(os.getenv('ANIME_NEWS'))
