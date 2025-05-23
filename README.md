# Email-Bot

A Bot which simulates email-conversations

## Features
- Send emails with AI-generated responses.
- Manage email threads with human and AI message differentiation.
- Query email threads by sender, recipient, or keywords.
- Reply to existing email threads.
- Store conversation history in MongoDB.
```
- email-bot/
├── backend/
│   ├── pycache/             
│   ├── ai_logic.py       # Custom AI response generation logic
│   ├── db.py             # Database connection and testing script (MongoDB)
│   ├── fastapi.py        # Main FastAPI application
│   └── models.py         # Pydantic models for data validation
├── frontend/
│   ├── streamlit_app.py  # Streamlit frontend application
├── .gitignore            # Git ignore file
├── README.md             
└── requirements.txt      # Project dependencies
```
## Prerequisites
- Python 3.10 or higher
- MongoDB Atlas account (for remote database)
- Gmail account with App Password for SMTP (for email sending)

## Installation
1. **Clone the repository**:
   ```bash
   git clone https://github.com/bala-guhan/email-bot.git
   cd email-bot
   ```
2. **Set up env**
   ```bash
    python -m venv env
    .\Scripts\activate or activate.bat
   ```
3. **Install dependencies**
   ```bash
    pip install -r requirements.txt
   ```
4. **Configure env variables**
   ```text
    MONGODB_USERNAME=abc
    MONGODB_PASSWORD=xyz
    SMTP_USER=emailbot949@gmail.com
    SMTP_PASSWORD=**** **** **** ****
    GROQ_API_KEY = ****************
   ```
5. **Start running backend**
    ```text
    cd backend
    uvicorn fastapi:app --reload
   ```
6. **Run the Frontend app**
```text
    cd frontend
    streamlit run streamlit_app.py
 ```
