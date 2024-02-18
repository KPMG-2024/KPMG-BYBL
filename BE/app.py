# app.py
from flask import Flask, jsonify
from flask_cors import CORS
from controllers.controller import upload_data, clear_data, get_buyer_db, query_archiveQA, search_buyer, email_write, email_send, query_DB_QA

app = Flask(__name__)
CORS(app)

@app.route('/')
def home_route():
    return jsonify({'message': 'Welcome to the API!'})

@app.route('/api/archive/upload', methods=['POST'])
def upload_route():
    return upload_data()

@app.route('/api/archive/clear', methods=['DELETE'])
def clear_route():
    return clear_data()

@app.route('/api/buyer/buyerlist', methods=['GET'])
def buyer_list_route():
    return get_buyer_db()

@app.route('/api/buyer/buyercollect', methods=['GET'])
def search_buyer_list_route():
    return search_buyer()

@app.route('/api/qa/archive', methods=['POST'])
def query_archive():
    return query_archiveQA()

@app.route('/api/qa/db', methods=['POST'])
def query_db():
    return query_DB_QA()

@app.route('/api/email', methods=['POST'])
def email_route():
    return email_write()

@app.route('/api/email/send', methods=['POST'])
def send_email_route():
    return email_send()

if __name__ == '__main__':
    app.run('0.0.0.0', port=3000, debug=True)