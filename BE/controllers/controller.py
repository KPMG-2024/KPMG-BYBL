# controllers.py

from flask import jsonify, request
from models.database import Database
from services.archive_QA import archive_QA
from services.db_QA import db_QA
from services.write_email import write_email
from services.send_email import send_email
from langchain_openai import OpenAIEmbeddings
from bson import json_util  # MongoDB의 ObjectId를 처리하기 위해 필요
import json
from werkzeug.utils import secure_filename
import os

db = Database()

def upload_data():
    try:
        data = request.json

        #process_embedding(data)으로 하면 작동이 안됨.
        embeddings = OpenAIEmbeddings()

        for item in data:
            text_embedding = embeddings.embed_query(item['text'])
            item['embedding'] = text_embedding
        
        db.insert_archive(data)

        return jsonify({"message": "Data uploaded successfully"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def clear_data():
    try:
        db.clear_archive()
        return jsonify({"message": "All data cleared successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_buyer_db():
    buyers = db.get_buyers()
    buyers_list = [{item: data[item] for item in data if item != '_id'} for data in buyers]
    return jsonify(buyers_list)

def search_buyer():
    buyers = db.get_buyers()  # 예를 들어, 이 함수가 MongoDB 컬렉션에서 문서를 가져옵니다.
    search_query = request.args.get('search', '').lower()
    
    if search_query:
        filtered_buyers = [buyer for buyer in buyers if 'trgtpsnNm' in buyer and search_query in buyer['trgtpsnNm'].lower()]
    else:
        filtered_buyers = buyers

    # MongoDB의 ObjectId를 JSON으로 직렬화 가능한 형태로 변환
    return json.dumps(filtered_buyers, default=json_util.default)

def query_archiveQA():
    request_data = request.json
    query_text = request_data.get('query')
    try:
        docs = archive_QA(query_text)
        return jsonify(docs), 200
    except Exception as e:
        error_message = {"error": str(e)}
        return jsonify(error_message), 500
    
def query_DB_QA():
    request_data = request.json
    query_text = request_data.get('query')
    try:
        docs = db_QA(query_text)
        return jsonify(docs), 200
    except Exception as e:
        error_message = {"error": str(e)}
        return jsonify(error_message), 500

def email_write():
    request_data = request.json
    try:
        result = write_email(request_data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
def email_send():
    buyer_email = request.form.get('buyerEmail')
    title = request.form.get('title')
    content = request.form.get('content')
    attachment_file = request.files.get('file')

    if not buyer_email or not title or not content:
        return jsonify({'error': 'Missing required data'}), 400
    

    # 파일 첨부 처리
    if attachment_file:
        filename = secure_filename(attachment_file.filename)
        filepath = os.path.join('/Users/taewonyun/Documents/GitHub/FE/server/attachments', filename)
        try:
            attachment_file.save(filepath)
            # 파일 저장 성공 시, 해당 파일을 이메일에 첨부하는 로직 추가
        except Exception as e:
            return jsonify({'error': f'Failed to save file: {str(e)}'}), 500
    print(filepath if attachment_file else None)
    try:
        # send_email 함수 수정 필요: 파일 경로를 인자로 전달
        send_email(buyer_email, title, content, filepath if attachment_file else None)
        return jsonify({'message': 'Email sent successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500