import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MY_TELEGRAM_ID = int(os.getenv("MY_TELEGRAM_ID"))
PROXY_SERVER = f"http://{os.getenv('PROXY_USER')}:{os.getenv('PROXY_PASSWORD')}@{os.getenv('PROXY_IP')}:{os.getenv('PROXY_PORT')}"
