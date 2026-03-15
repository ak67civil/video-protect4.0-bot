import os

class Config:
    API_ID = int(os.environ.get("API_ID", "33401543"))
    API_HASH = os.environ.get("API_HASH", "7cdea5bbc8bd991b4a49807ce86")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    MONGO_DB_URI = os.environ.get("MONGO_DB_URI", "")
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "0"))
    # IDs ko list mein convert karega bina crash huye
    OWNER_IDS = [int(i.strip()) for i in os.environ.get("OWNER_ID", "").split(",") if i.strip()]
    
