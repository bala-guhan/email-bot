from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Pydantic models
class Reply(BaseModel):
    sender: str
    body: str
    timestamp: datetime = datetime.utcnow()

class Email(BaseModel):
    sender: str
    recipient: str
    subject: str
    body: str
    timestamp: Optional[datetime] = None

class ReplyRequest(BaseModel):
    thread_id: str
    sender: str
    reply_body: str
