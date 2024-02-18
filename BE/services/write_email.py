# services.py
import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()  # 환경 변수 로드

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def get_prompt(requests_result):
    email = requests_result.get('buyerEmail')
    
    our_data = requests_result.get('ourData')
    
    buyer_data = requests_result.get('buyerData')

    buyerlanguage = requests_result.get('buyerlanguage')

    prompt = f"""
    Your task is to write a B2B cold email to a buyer using [our data] and [buyer data]. Follow these instructions step by step.

    [instructions]
    1. The email should be structured with an introduction, main body, and conclusion.
    2. In the introduction, include content that forms a connection with the buyer by referencing their recent activities, and make sure it serves as a hook.
    3. The main body should focus on how the buyer's current situation can be improved by using our product, clearly showing the 'as is' and 'to be' scenarios.
    4. The conclusion should contain a request for a reply if they like our proposal.
    5. Do not use bracketed expressions like "[introduction], [Company Name]" in the text.
    6. Do not use any korean words in the email and use the buyer's language.
    6. Your answer must be in the following JSON format:
    {{"title" : "Email Title","content":"content in buyer country's language"}}

    [Buyer Email Address]
    {email}

    [Buyer Country]
    {buyerlanguage}

    [Our data]
    {our_data}

    [Buyer data]
    {buyer_data}
    """
    
    return prompt

def get_response(prompt):
    # Define the API key and URL
    API_KEY = GOOGLE_API_KEY  # replace with your actual API key
    URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

    # Define the headers and data for the POST request
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
        }

    # Send POST request
    response = requests.post(f"{URL}?key={API_KEY}", headers=headers, json=data)

    text_response = response.json()['candidates'][0]['content']['parts'][0]['text']

    return text_response

def write_email(json_data):
    prompt = get_prompt(json_data)

    output = get_response(prompt=prompt)
    
    output = json.loads(output, strict=False)

    return output
    