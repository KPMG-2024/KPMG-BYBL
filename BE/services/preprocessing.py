from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()  # 환경 변수 로드

def process_embedding(data):

    embeddings = OpenAIEmbeddings()
    
    for item in data:
        text_embedding = embeddings.embed_query(item['text'])
        item['embedding'] = text_embedding
    
    return data