# import psycopg2
# from dotenv import load_dotenv
# import os
# load_dotenv()  # Load environment variables from .env file

# USER = os.getenv('DB_USER')
# PASSWORD = os.getenv('DB_PASSWORD')
# DBNAME = os.getenv('DB_NAME')
# HOST = os.getenv('DB_HOST')
# PORT = os.getenv('DB_PORT')

# connection = psycopg2.connect(
#     user=USER,
#     password=PASSWORD,
#     host=HOST,
#     port=PORT,
#     dbname=DBNAME
# )
# cursor = connection.cursor()

import psycopg2
import os

# 1. 從 Render 的環境中讀取 DATABASE_URL
#    Render 會自動為您設定這個變數。
DATABASE_URL = os.environ.get('DATABASE_URL')

# 2. 檢查變數是否存在
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Did you link the database in Render?")

# 3. psycopg2 可以直接使用這整個 URL 字串來連線
try:
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()
    print("Database connection successful!")  # 方便您在日誌中確認
except Exception as e:
    print(f"Database connection failed: {e}")
    raise e

# ... 這裡接您檔案中其他的程式碼 (如果有的話)