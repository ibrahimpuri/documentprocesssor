from flask import Flask, request, jsonify
from document_processor import DocumentProcessor
import spacy

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")
processor = DocumentProcessor(nlp)

@app.route('/upload', methods=['POST'])
def upload():
    content = request.json['content']
    doc_type = request.json['type']
    document = {'type': doc_type, 'content': content}
    result = process_documents([document], processor)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)