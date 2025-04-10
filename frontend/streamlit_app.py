import streamlit as st
import requests
st.set_page_config(layout="wide")

BASE_URL = "http://localhost:8000"  # FastAPI server URL

st.title("Company X Email Bot")

col1, col2, col3 = st.columns(3)

with col1:
    st.header("Send an Email")
    sender = st.text_input("From (Sender Email)", value="emailbot949@gmail.com")
    to = st.text_input("To (Recipient Email)")
    subject = st.text_input("Subject")
    message = st.text_area("Message")

    if st.button("Submit"):
        if not to or not subject or not message:
            st.error("Please fill in all fields!")
        else:
            payload = {
                "sender": sender,
                "recipient": to,
                "subject": subject,
                "body": message,
            }
            try:
                response = requests.post(f"{BASE_URL}/send-email", json=payload)
                if response.status_code == 200:
                    st.success(response.json()["message"])
                    st.code(f"AI Response: {response.json()['ai_response']}\nThread ID: {response.json()['thread_id']}", language="json")
                else:
                    st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to connect to server: {str(e)}")

with col2:
    st.header("Query Email Threads")
    query_sender = st.text_input("Filter by Sender (optional)")
    query_recipient = st.text_input("Filter by Recipient (optional)")
    query_keywords = st.text_input("Search Keywords (optional)")

    if st.button("Search Threads"):
        params = {}
        if query_sender:
            params["sender"] = query_sender
        if query_recipient:
            params["recipient"] = query_recipient
        if query_keywords:
            params["keywords"] = query_keywords

        try:
            response = requests.get(f"{BASE_URL}/query-threads", params=params)
            if response.status_code == 200:
                threads = response.json()
                if threads:
                    for thread in threads:
                        st.subheader(f"Thread ID: {thread['_id']}")
                        st.code(f"Recipient: {thread['recipient']}")
                        st.code(f"Subject: {thread['subject']}")
                        st.write("Messages:")
                        for msg in thread["messages"]:
                            prefix = "Human: " if msg["message_type"] == "human" else "AI: "
                            st.code(f"  [{msg['timestamp']}] {prefix} {msg['body']}")
                else:
                    st.warning("No threads found matching your criteria.")
            else:
                st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to connect to server: {str(e)}")

with col3:
    st.header("Reply to Thread")
    reply_thread_id = st.text_input("Thread ID to Reply To")
    reply_sender = st.text_input("Reply Sender Email")
    reply_body = st.text_area("Reply Message")

    if st.button("Send Reply"):
        if not reply_thread_id or not reply_sender or not reply_body:
            st.error("Please fill in all fields for the reply!")
        else:
            payload = {
                "thread_id": reply_thread_id,
                "sender": reply_sender,
                "reply_body": reply_body
            }
            try:
                response = requests.post(f"{BASE_URL}/reply-to-thread", json=payload)
                if response.status_code == 200:
                    st.success(response.json()["message"])
                    st.code(f"Thread ID: {response.json()['thread_id']}", language="json")
                    thread_response = requests.get(f"{BASE_URL}/thread/{reply_thread_id}")
                    if thread_response.status_code == 200:
                        thread_data = thread_response.json()
                        st.subheader("Updated Thread:")
                        for msg in thread_data["messages"]:
                            prefix = "Human: " if msg["message_type"] == "human" else "AI: "
                            st.code(f"  [{msg['timestamp']}] {prefix} {msg['body']}")
                else:
                    st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to connect to server: {str(e)}")