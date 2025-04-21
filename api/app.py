from flask import Flask, jsonify, request
from mistral_wrapper import MistralAPI

app = Flask(__name__)
mistral_api = MistralAPI()

@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello, World!"})

@app.route('/api/ask', methods=['POST'])
def ask_mistral():
    data = request.get_json()
    
    if not data or 'prompt' not in data:
        return jsonify({"error": "Prompt is required"}), 400
    
    try:
        prompt = data['prompt']
        response = mistral_api.get_response(prompt)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
