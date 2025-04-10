import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()

groq_api_key = os.getenv('GROQ_API_KEY')

llama = ChatGroq(
    model='llama-3.3-70b-versatile',
    api_key=groq_api_key,
    temperature=0
)

prompt_template = ChatPromptTemplate.from_template("""
You are a helpful assistant. You are the marketing team consultant of the company X. you have the following data abou the company, 
only answer to queries which are related to marketing of the company and not anything else. clear your answers short, clear and to the point.

right question to answer:
What is the marketing strategy of the company?

questions not to answer:
who is the winner of 2022 olympics

<data of the company>
Apple Inc.’s marketing sector plays a pivotal role in sustaining its dominance in the global technology market, contributing to a brand valuation of over $880 billion as of 2024, according to Interbrand. The company allocates a significant portion of its annual revenue to marketing, with $6.2 billion spent in fiscal year 2023 alone. Apple’s strategy is data-driven and integrates precision targeting across digital, retail, and experiential channels. Its marketing emphasizes product ecosystems and seamless integration, backed by minimalistic design and high production quality in advertising.

Technically, Apple leverages advanced analytics, machine learning, and consumer behavior modeling to personalize its digital campaigns across platforms like Apple Search Ads, App Store placements, and geo-targeted messaging. The company’s product launch events routinely draw millions of live viewers, creating global spikes in engagement metrics, app downloads, and sales conversions. Moreover, Apple’s customer retention rate exceeds 92% in the smartphone segment, a testament to the effectiveness of its loyalty-building strategies. Overall, Apple’s marketing function is not just brand-building but a tightly integrated, data-optimized engine that fuels its business growth across hardware, software, and services.
{user_input}
""")

chain = prompt_template | llama


def generate_ai_response(user_input: str) -> str:
    """A simple AI response generator for the email bot."""
    user_input = user_input.lower()
    response = chain.invoke({"user_input": user_input})
    return response

print(generate_ai_response("What is the marketing strategy of the company?"))