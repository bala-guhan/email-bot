from fastapi import FastAPI, HTTPException
import smtplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv
from pymongo import MongoClient
from urllib.parse import quote_plus
from datetime import datetime
from uuid import uuid4
from typing import List, Dict
from pydantic import BaseModel  
from ai_logic import generate_ai_response
from models import Email, ReplyRequest
from urllib.parse import quote_plus

load_dotenv()
app = FastAPI()

SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

MONGODB_USERNAME = os.getenv('MONGODB_USERNAME')
MONGODB_PASSWORD = quote_plus(os.getenv('MONGODB_PASSWORD'))

MONGODB_URL = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@email-bot.70t4ugm.mongodb.net/?retryWrites=true&w=majority&appName=email-bot"
client = MongoClient(MONGODB_URL)
db = client['conversations']
threads_collection = db['threads']  

def send_email(email: Dict, ai_response: str) -> bool:
    """Helper function to execute sending emails through SMTP
    
        Args : {dictionary containing the email structure and ai_response}
        Send the email
        Returns : True/False 
    """
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_user = SMTP_USERNAME
        smtp_password = SMTP_PASSWORD   

        msg = MIMEText(ai_response)
        msg['Subject'] = email["subject"]
        msg['From'] = email["sender"]
        msg['To'] = email["recipient"]

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


@app.post("/send-email")
async def send_email_endpoint(email: Dict):
    """End point for sending emails
    
        Args : {sender, recipient, subject, body}
        calls the send_email function and takes care of the thread creation and updates
        Returns : AI response and thread id to frontend 
    """
    required_fields = ["sender", "recipient", "subject", "body"]
    if not all(field in email and email[field] for field in required_fields):
        raise HTTPException(status_code=400, detail="Sender, recipient, subject, and body are required")

    # Determine if this is part of an existing thread (match by recipient and subject)
    thread = threads_collection.find_one({
        "recipient": {"$regex": f"^{email['recipient'].strip()}$", "$options": "i"},
        "subject": {"$regex": f"^{email['subject'].strip()}$", "$options": "i"}
    })
    if thread:
        # Update existing thread
        human_message = {
            "sender": email["sender"],
            "body": email["body"],
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "message_type": "human"
        }
        threads_collection.update_one(
            {"_id": thread["_id"]},
            {"$push": {"messages": human_message}}
        )
        print("Updated DB with human message")
    else:
        # Create new thread
        thread_id = str(uuid4())
        new_thread = {
            "_id": thread_id,
            "recipient": email["recipient"],
            "subject": email["subject"],
            "messages": [{
                "sender": email["sender"],
                "body": email["body"],
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "message_type": "human"
            }]
        }
        threads_collection.insert_one(new_thread)
        print("Created new thread in DB")

    # calls the function from another file check : "ai_logic.py"
    ai_response = generate_ai_response(email["body"])

    ai_message = {
        "sender": "emailbot949@gmail.com",
        "body": ai_response.content,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "message_type": "ai"
    }
    threads_collection.update_one(
        {"_id": thread["_id"]} if thread else {"_id": thread_id},
        {"$push": {"messages": ai_message}}
    )
    print("Updated DB with AI response")

    if not send_email(email, ai_response.content):
        raise HTTPException(status_code=500, detail="Email sending failed")

    print(f"AI Response: {ai_response.content}")

    return {"message": "Email sent successfully", "ai_response": ai_response.content, "thread_id": thread["_id"] if thread else thread_id}

@app.get("/thread/{thread_id}")
async def get_thread(thread_id: str):
    """Helper endpoint to get the thread id from the database"""
    thread = threads_collection.find_one({"_id": thread_id})
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    return thread

@app.get("/query-threads")
async def query_threads(
    sender: str = None,
    recipient: str = None,
    keywords: str = None
):
    """
    Query threads by sender, recipient, or keywords in subject or body.
    Args:
        sender (str, optional): Filter by sender email
        recipient (str, optional): Filter by recipient email
        keywords (str, optional): Search keywords in subject or body
    Returns:
        List[Dict]: List of matching thread documents
    """
    query = {}
    
    if sender:
        query["messages.sender"] = {"$regex": f"^{sender.strip()}$", "$options": "i"}
    
    if recipient:
        query["recipient"] = {"$regex": f"^{recipient.strip()}$", "$options": "i"}
    
    if keywords:
        keyword_query = {
            "$or": [
                {"subject": {"$regex": keywords.strip(), "$options": "i"}},
                {"messages.body": {"$regex": keywords.strip(), "$options": "i"}}
            ]
        }
        query.update(keyword_query)

    threads = list(threads_collection.find(query))
    if not threads:
        raise HTTPException(status_code=404, detail="No matching threads found")
    
    return threads


@app.post("/reply-to-thread")
async def reply_to_thread(reply_data: ReplyRequest):
    """
    Add a reply to an existing thread.
    Args:
        reply_data (ReplyRequest): Contains thread_id, sender, and reply_body
    Returns:
        Dict: Confirmation message and updated thread_id
    """
    thread_id = reply_data.thread_id
    sender = reply_data.sender
    reply_body = reply_data.reply_body

    thread = threads_collection.find_one({"_id": thread_id})
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    reply_message = {
        "sender": sender,
        "body": reply_body,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "message_type": "human"
    }
    threads_collection.update_one(
        {"_id": thread_id},
        {"$push": {"messages": reply_message}}
    )
    print("Updated DB with reply message")

    return {"message": "Reply added successfully", "thread_id": thread_id}