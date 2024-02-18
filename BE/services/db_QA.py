# services.py

from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
import os
from dotenv import load_dotenv

load_dotenv()  # 환경 변수 로드

def db_QA(query_text):
    try:
        # 환경 변수와 초기 설정 로직...
        MONGO_URI = os.getenv("MONGO_URI")
        if not MONGO_URI:
            raise ValueError("MONGO_URI 환경 변수를 설정하세요.")

        embedding_fn = OpenAIEmbeddings(disallowed_special=())

        # 아래 DB 만 변경
        vector_search = MongoDBAtlasVectorSearch.from_connection_string(
            MONGO_URI, "hscode.commodity", embedding_fn, index_name="default",
        )

        qa_retriever = vector_search.as_retriever(search_type="similarity", search_kwargs={"k": 2})

        llm = ChatGoogleGenerativeAI(model="gemini-pro", convert_system_message_to_human=True)

        prompt_template = """
        Instructions:
        1.Based on the provided [Information], you must complete the [Task].
        2. If you cannot perform the Task with the given [Information], you must state that it cannot be solved with the provided [Information] and find a solution on your own.
        3. Please answer in Korean.

        [Information]
        {context}

        [Task]
        {question}
        """

        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )

        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=qa_retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT},
            verbose=True,
        )

        # 실제 쿼리 처리 로직
        docs = qa({"query": query_text})

        docs['source_documents'] = [doc.page_content for doc in docs['source_documents']]
        
        return docs
    
    except Exception as e:
        return f"오류 발생: {e}"