import discord
import asyncio
import requests
from bs4 import BeautifulSoup

# Initialize intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

# Initialize Discord client with intents
client = discord.Client(intents=intents)

# Thay thế bằng thông tin của bạn
WEBHOOK_URL = os.getenv("tk")  # URL webhook của kênh thông báo (đã kiểm tra và sửa)
DISCORD_BOT_TOKEN =  os.getenv("TOKEN") # Bot token

# URL trang web
URL = 'https://kodoani.com/'

# Tập hợp để lưu trữ các bài viết đã gửi
sent_posts = set()

def fetch_latest_news():
    print("Fetching latest news...")
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    posts = soup.find_all('div', class_='col-sm-3 menu-post-item')
    latest_posts = []

    for post in posts:
        time_span = post.find('span')
        if time_span:
            time_text = time_span.get_text().strip()
            if 'phút' in time_text:
                minutes_ago = int(time_text.split()[0])
                if minutes_ago <= 1:
                    title = post.find('img')['alt']
                    link = post.find('a')['href']

                    # Lấy ảnh thumbnail từ trang bài viết
                    article_response = requests.get(link)
                    article_soup = BeautifulSoup(article_response.text, 'html.parser')
                    og_image = article_soup.find('meta', property='og:image')
                    image_url = og_image['content'] if og_image else ''

                    latest_posts.append({
                        'title': title,
                        'image_url': image_url,
                        'link': link
                    })

    print(f"Found {len(latest_posts)} new posts")
    return latest_posts

def send_to_discord_via_webhook(posts):
    for post in posts:
        if post['link'] not in sent_posts:
            print(f"Processing post: {post['title']}")
            data = {
                "embeds": [
                    {
                        "title": post['title'],
                        "url": post['link'],
                        "color": 5814783,
                        "image": {"url": post['image_url']}
                    }
                ]
            }

            # Gửi tin qua webhook
            print("Sending message to webhook...")
            result = requests.post(WEBHOOK_URL, json=data)
            print(f'Webhook response: {result.text}')
            print(f'Webhook status code: {result.status_code}')
            if 200 <= result.status_code < 300:
                try:
                    message_info = result.json()
                    message_id = message_info['id']
                    channel_id = message_info['channel_id']
                    print(f'Webhook message_id: {message_id}')
                    print(f'Webhook channel_id: {channel_id}')

                    # Tự động crosspost bài viết
                    crosspost_url = f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/crosspost"
                    print(f"Crosspost URL: {crosspost_url}")
                    headers = {"Authorization": f"Bot {DISCORD_BOT_TOKEN}"}
                    crosspost_response = requests.post(crosspost_url, headers=headers)

                    if crosspost_response.status_code == 200:
                        print(f"Đã phát hành tin: {post['title']}")
                    else:
                        print(f"Lỗi khi crosspost tin nhắn. Trạng thái: {crosspost_response.status_code}, Nội dung: {crosspost_response.text}")
                except requests.exceptions.JSONDecodeError:
                    print(f"Webhook trả về không phải JSON. Trạng thái: {result.status_code}, Nội dung: {result.text}")
            else:
                print(f"Lỗi khi gửi tin nhắn đến webhook. Trạng thái: {result.status_code}, Nội dung: {result.text}")
            sent_posts.add(post['link'])

async def check_for_new_posts():
    await client.wait_until_ready()
    print("check_for_new_posts task started")
    while not client.is_closed():
        latest_posts = fetch_latest_news()
        if latest_posts:
            send_to_discord_via_webhook(latest_posts)
        await asyncio.sleep(60)

@client.event
async def on_ready():
    print(f'Đã đăng nhập với tên: {client.user}')
    print('------')
    asyncio.create_task(check_for_new_posts())

async def main():
    await client.start(DISCORD_BOT_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())