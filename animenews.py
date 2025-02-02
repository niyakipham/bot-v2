import asyncio, os
import requests
from bs4 import BeautifulSoup

# URL Webhook Discord của bạn
WEBHOOK_URL = os.getenv("tk")

# URL trang web
URL = 'https://kodoani.com/'

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

def send_to_discord_via_webhook(posts):
    for post in posts:
        if post['link'] not in sent_posts:
            data = {
                "embeds": [
                    {
                        "title": post['title'],
                        "url": post['link'],
                        "description": "",
                        "color": 5814783,  # Màu xanh dương (decimal)
                        "image": {"url": post['image_url']}
                    }
                ]
            }
            result = requests.post(WEBHOOK_URL, json=data)
            try:
                result.raise_for_status()
            except requests.exceptions.HTTPError as err:
                print(err)
            else:
                print("Payload delivered successfully, code {}.".format(result.status_code))
            sent_posts.add(post['link'])

async def check_for_new_posts():
    while True:
        latest_posts = fetch_latest_news()
        if latest_posts:
            send_to_discord_via_webhook(latest_posts)
        else:
            print("Không có bài viết mới trong vòng 1 phút.")
        await asyncio.sleep(60)

async def main():
    await check_for_new_posts()

if __name__ == "__main__":
    asyncio.run(main())
