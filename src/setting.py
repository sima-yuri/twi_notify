import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

LINE_NOTIFY_TOKUN_DEV:str = os.environ.get("LINE_NOTIFY_TOKUN_DEV")
LINE_NOTIFY_TOKUN_PROD:str = os.environ.get("LINE_NOTIFY_TOKUN_PROD")
FEED_BASE_URL:str = os.environ.get("FEED_BASE_URL")