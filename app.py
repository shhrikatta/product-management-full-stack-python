from flask import Flask, request, jsonify
from flask_cors import CORS
from collections import Counter
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

@app.route('/api/count', methods=['POST'])
def count_words():
    """
    Endpoint to count total words in the provided text.
    Expects JSON: {'text': '...'}
    Returns JSON: {'text': '...', 'count': number}
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Missing text field in request'}), 400
        
        text = data['text']
        
        # Handle empty or None text
        if not text or not text.strip():
            return jsonify({'text': text or '', 'count': 0})
        
        # Split text into words and count them
        # Using regex to split on whitespace and punctuation for better word separation
        words = re.findall(r'\b\w+\b', text.lower())
        word_count = len(words)
        
        return jsonify({'text': text, 'count': word_count})
    
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/breakdown', methods=['POST'])
def word_breakdown():
    """
    Endpoint to get word frequency breakdown.
    Expects JSON: {'text': '...'}
    Returns JSON: {'text': '...', 'breakdown': {'word1': count1, 'word2': count2, ...}}
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Missing text field in request'}), 400
        
        text = data['text']
        
        # Handle empty or None text
        if not text or not text.strip():
            return jsonify({'text': text or '', 'breakdown': {}})
        
        # Extract words using regex and convert to lowercase for consistency
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Count word frequencies
        word_freq = Counter(words)
        
        # Convert Counter to regular dict for JSON serialization
        return jsonify({'text': text, 'breakdown': dict(word_freq)})
    
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/', methods=['GET'])
def health_check():
    """
    Simple health check endpoint
    """
    return jsonify({
        'message': 'Word Count API is running',
        'endpoints': {
            '/api/count': 'POST - Count total words in text',
            '/api/breakdown': 'POST - Get word frequency breakdown'
        }
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
