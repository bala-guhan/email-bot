from fastapi import FastAPI, HTTPException
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
from typing import Dict
import uuid
from models import Email, Reply
from pymongo import MongoClient
from datetime import datetime
from urllib.parse import quote_plus

# Load environment variables
load_dotenv()
app = FastAPI()

# MongoDB Setup
username = "guhan"
password = quote_plus("GS1201bg2004?")  # encode the password
MONGODB_URL = f"mongodb+srv://{username}:{password}@email-bot.70t4ugm.mongodb.net/?retryWrites=true&w=majority&appName=email-bot"
client = MongoClient(MONGODB_URL)
db = client['conversations']
coll = db['threads']

coll.drop()
print("dropped successfully")