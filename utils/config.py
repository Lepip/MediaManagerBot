import os


cfg = {
    "db_host": os.environ["DB_HOST"],
    "db_port": int(os.environ["DB_PORT"]),
    "db_user": os.environ["DB_USER"],
    "db_name": os.environ["DB_NAME"],
    "db_password": os.environ["DB_PASSWORD"],
    "bot_token": os.environ["BOT_TOKEN"]
}
