import asyncio
import os
import requests
from bs4 import BeautifulSoup

# URL Webhook Discord của bạn (thay thế bằng URL của bạn)
WEBHOOK_URL = os.getenv("tk")  # Lấy từ biến môi trường

# URL trang web cần theo dõi
URL = 'https://kodoani.com/'

# Tập hợp để lưu trữ các bài viết đã gửi, tránh gửi trùng lặp
sent_posts = set()

def fetch_latest_news():
    """
    Hàm lấy tin tức mới nhất từ trang web.

    Returns:
        list: Danh sách các bài viết mới nhất trong vòng 1 phút.
              Mỗi bài viết là một dictionary chứa 'title', 'image_url', và 'link'.
    """
    try:
        # Gửi yêu cầu HTTP để lấy dữ liệu trang web
        response = requests.get(URL)
        response.raise_for_status()  # Kiểm tra lỗi HTTP
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi truy cập trang web: {e}")
        return []

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
                try:
                    minutes_ago = int(time_text.split()[0])
                    if minutes_ago <= 1:
                        # Lấy thông tin tiêu đề, ảnh và link bài viết
                        title = post.find('img')['alt']
                        image_url = post.find('img')['data-src']
                        link = post.find('a')['href']

                        latest_posts.append({
                            'title': title,
                            'image_url': image_url,
                            'link': link
                        })
                except (ValueError, TypeError, KeyError, AttributeError):
                    # Bỏ qua bài viết nếu có lỗi khi lấy thông tin
                    pass

    return latest_posts

def send_to_discord_via_webhook(posts):
    """
    Hàm gửi tin tức đến Discord thông qua webhook.

    Args:
        posts (list): Danh sách các bài viết cần gửi.
                      Mỗi bài viết là một dictionary chứa 'title', 'image_url', và 'link'.
    """
    for post in posts:
        if post['link'] not in sent_posts:
            # Tạo payload cho webhook
            data = {
                "embeds": [
                    {
                        "title": post['title'],
                        "url": post['link'],
                        "description": "",
                        "color": 5814783,  # Màu xanh dương
                        "image": {"url": post['image_url']}
                    }
                ],
                "flags": 4  # Cờ để xuất bản tin nhắn (quan trọng)
            }
            try:
                # Gửi yêu cầu POST đến webhook URL
                result = requests.post(WEBHOOK_URL, json=data)
                result.raise_for_status()  # Kiểm tra lỗi HTTP

            except requests.exceptions.HTTPError as err:
                print(f"Lỗi khi gửi tin nhắn đến Discord: {err}")
                print(f"Response: {result.text}") # Log the server response
            else:
                print("Payload delivered successfully, code {}.".format(result.status_code))
                # Thêm link bài viết vào tập hợp các bài viết đã gửi
                sent_posts.add(post['link'])

async def check_for_new_posts():
    """
    Hàm kiểm tra tin tức mới mỗi 60 giây.
    """
    while True:
        print("Đang kiểm tra tin tức mới...")
        latest_posts = fetch_latest_news()
        if latest_posts:
            send_to_discord_via_webhook(latest_posts)
        else:
            print("Không có bài viết mới trong vòng 1 phút.")
        await asyncio.sleep(60)  # Chờ 60 giây

async def main():
    """
    Hàm main chạy chương trình.
    """
    await check_for_new_posts()

if __name__ == "__main__":
    asyncio.run(main())
