import requests
from bs4 import BeautifulSoup
from discord_webhook import DiscordWebhook, DiscordEmbed
import time
from urllib.parse import urljoin

WEBHOOK_URL = os.getenv("GAME")
BASE_URL = 'https://gamek.vn/'
FILE_NAME = 'posted_titles.txt'
CHECK_INTERVAL = 60  # seconds

def process_title(title):
    """Xóa tất cả dấu \" trong tiêu đề"""
    return title.replace('"', '') if title else ''

def get_existing_titles():
    """Đọc các tiêu đề đã đăng từ file"""
    try:
        with open(FILE_NAME, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        return []

def save_title(title):
    """Lưu tiêu đề mới vào file"""
    with open(FILE_NAME, 'a', encoding='utf-8') as f:
        f.write(f"{title}\n")

def send_webhook(article):
    """Gửi bài viết đến Discord qua webhook"""
    webhook = DiscordWebhook(url=WEBHOOK_URL)
    
    embed = DiscordEmbed(
        title=article['title'],
        url=article['url'],
        color=242424
    )
    
    if article['image']:
        embed.set_image(url=article['image'])
    
    webhook.add_embed(embed)
    webhook.execute()

def check_new_articles():
    # Lấy danh sách tiêu đề cũ
    existing_titles = get_existing_titles()
    
    # Truy cập trang web
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Tìm khối chứa bài viết
    news_block = soup.find('div', {
        'class': 'topleft', 
        'data-boxtype': 'homenewsposition'
    })
    
    if not news_block:
        return
    
    # Lấy tất cả bài viết
    articles = []
    for a_tag in news_block.find_all('a'):
        title = process_title(a_tag.get('title'))
        link = urljoin(BASE_URL, a_tag.get('href'))
        img_tag = a_tag.find('img')
        image = urljoin(BASE_URL, img_tag.get('src')) if img_tag else None
        
        if title and link:
            articles.append({
                'title': title,
                'url': link,
                'image': image
            })
    
    # Kiểm tra và đăng bài mới
    for article in articles:
        if article['title'] not in existing_titles:
            send_webhook(article)
            save_title(article['title'])
            existing_titles.append(article['title'])  # Cập nhật danh sách đã đăng
            time.sleep(1)  # Tránh rate limit

def main():
    while True:
        try:
            check_new_articles()
        except Exception as e:
            print(f"Có lỗi xảy ra: {e}")
        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    main()