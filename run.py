import discord
from discord.ext import commands

# Thay thế YOUR_BOT_TOKEN bằng token bot thực tế của bạn
TOKEN = 'YOUR_BOT_TOKEN'

# Tiền tố lệnh là những gì bạn nhập trước lệnh.
# Ví dụ: !publish
PREFIX = '!'

# ID của kênh thông báo
ANNOUNCEMENT_CHANNEL_ID = 1334849201422598167

# Tạo một thể hiện bot mới
bot = commands.Bot(command_prefix=PREFIX, intents=discord.Intents.all())

# Hàm này được gọi khi bot đã sẵn sàng
@bot.event
async def on_ready():
    print(f'Đã đăng nhập với tên {bot.user.name}')

# Hàm này được gọi khi có tin nhắn được gửi trong kênh
@bot.event
async def on_message(message):
    # Đảm bảo bot không phản hồi lại tin nhắn của chính nó
    if message.author == bot.user:
        return

    # Kiểm tra xem tin nhắn có nằm trong kênh thông báo cụ thể không
    if message.channel.id == ANNOUNCEMENT_CHANNEL_ID:
        try:
            # Xuất bản tin nhắn
            await message.publish()
            print(f'Đã xuất bản tin nhắn: {message.content}')
        except discord.HTTPException as e:
            print(f'Lỗi khi xuất bản tin nhắn: {e}')

    # Xử lý các lệnh khác
    await bot.process_commands(message)

# Chạy bot
bot.run(os.getenv("TOKEN"))