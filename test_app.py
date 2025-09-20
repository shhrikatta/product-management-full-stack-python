import pytest
import json
from unittest.mock import patch, Mock
import app


class TestWordCountAPI:
    """Test class for the Word Count API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the Flask application"""
        app.app.config['TESTING'] = True
        with app.app.test_client() as client:
            yield client
    
    # ====================
    # HEALTH CHECK TESTS
    # ====================
    
    def test_health_check_success(self, client):
        """Test the health check endpoint returns correct response"""
        response = client.get('/')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['message'] == 'Word Count API is running'
        assert '/api/count' in data['endpoints']
        assert '/api/breakdown' in data['endpoints']
        assert data['endpoints']['/api/count'] == 'POST - Count total words in text'
        assert data['endpoints']['/api/breakdown'] == 'POST - Get word frequency breakdown'
    
    # ====================
    # COUNT ENDPOINT TESTS
    # ====================
    
    def test_count_words_success_basic(self, client):
        """Test word counting with basic text"""
        response = client.post('/api/count',
                             data=json.dumps({'text': 'hello world'}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['text'] == 'hello world'
        assert data['count'] == 2
    
    def test_count_words_success_complex(self, client):
        """Test word counting with complex text including punctuation"""
        text = "Hello, world! This is a test. It's working great!"
        response = client.post('/api/count',
                             data=json.dumps({'text': text}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['text'] == text
        # Should count: hello, world, this, is, a, test, it, s, working, great = 10 words
        assert data['count'] == 10
    
    def test_count_words_with_numbers(self, client):
        """Test word counting with numbers and mixed content"""
        text = "I have 123 apples and 456 oranges in 2024"
        response = client.post('/api/count',
                             data=json.dumps({'text': text}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] == 9  # i, have, 123, apples, and, 456, oranges, in, 2024
    
    def test_count_words_empty_string(self, client):
        """Test word counting with empty string"""
        response = client.post('/api/count',
                             data=json.dumps({'text': ''}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['text'] == ''
        assert data['count'] == 0
    
    def test_count_words_whitespace_only(self, client):
        """Test word counting with whitespace only"""
        response = client.post('/api/count',
                             data=json.dumps({'text': '   \n\t  '}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['text'] == '   \n\t  '
        assert data['count'] == 0
    
    def test_count_words_null_text(self, client):
        """Test word counting with null text"""
        response = client.post('/api/count',
                             data=json.dumps({'text': None}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['text'] == ''
        assert data['count'] == 0
    
    def test_count_words_special_characters(self, client):
        """Test word counting with special characters and symbols"""
        text = "@#$% hello &*() world !@# 123 $%^"
        response = client.post('/api/count',
                             data=json.dumps({'text': text}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] == 3  # hello, world, 123
    
    def test_count_words_unicode_characters(self, client):
        """Test word counting with unicode characters"""
        text = "Hello 世界 café naïve résumé"
        response = client.post('/api/count',
                             data=json.dumps({'text': text}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] == 5  # hello, 世界, café, naïve, résumé
    
    def test_count_words_missing_text_field(self, client):
        """Test count endpoint with missing text field"""
        response = client.post('/api/count',
                             data=json.dumps({'message': 'hello world'}),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'Missing text field in request'
    
    def test_count_words_no_json_data(self, client):
        """Test count endpoint with no JSON data"""
        response = client.post('/api/count',
                             data=json.dumps({}),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['error'] == 'Missing text field in request'
    
    def test_count_words_invalid_json(self, client):
        """Test count endpoint with invalid JSON"""
        response = client.post('/api/count',
                             data='invalid json',
                             content_type='application/json')
        
        assert response.status_code == 500
        data = response.get_json()
        assert data['error'] == 'Internal server error'
    
    def test_count_words_no_content_type(self, client):
        """Test count endpoint without content type"""
        response = client.post('/api/count',
                             data=json.dumps({'text': 'hello world'}))
        
        assert response.status_code == 500
        data = response.get_json()
        assert data['error'] == 'Internal server error'
    
    @patch('app.re.findall')
    def test_count_words_exception_handling(self, mock_findall, client):
        """Test count endpoint exception handling"""
        mock_findall.side_effect = Exception('Test exception')
        
        response = client.post('/api/count',
                             data=json.dumps({'text': 'hello world'}),
                             content_type='application/json')
        
        assert response.status_code == 500
        data = response.get_json()
        assert data['error'] == 'Internal server error'
    
    # ====================
    # BREAKDOWN ENDPOINT TESTS
    # ====================
    
    def test_breakdown_success_basic(self, client):
        """Test word breakdown with basic text"""
        response = client.post('/api/breakdown',
                             data=json.dumps({'text': 'hello world hello'}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['text'] == 'hello world hello'
        assert data['breakdown']['hello'] == 2
        assert data['breakdown']['world'] == 1
    
    def test_breakdown_success_complex(self, client):
        """Test word breakdown with complex text"""
        text = "The quick brown fox jumps over the lazy dog. The dog was lazy."
        response = client.post('/api/breakdown',
                             data=json.dumps({'text': text}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        breakdown = data['breakdown']
        assert breakdown['the'] == 3
        assert breakdown['lazy'] == 2
        assert breakdown['dog'] == 2
        assert breakdown['quick'] == 1
        assert breakdown['fox'] == 1
    
    def test_breakdown_case_insensitive(self, client):
        """Test that breakdown is case insensitive"""
        text = "Hello HELLO hello"
        response = client.post('/api/breakdown',
                             data=json.dumps({'text': text}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['breakdown']['hello'] == 3
    
    def test_breakdown_with_punctuation(self, client):
        """Test breakdown with punctuation"""
        text = "Hello, world! Hello... world?"
        response = client.post('/api/breakdown',
                             data=json.dumps({'text': text}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        breakdown = data['breakdown']
        assert breakdown['hello'] == 2
        assert breakdown['world'] == 2
    
    def test_breakdown_with_numbers(self, client):
        """Test breakdown with numbers"""
        text = "I have 100 apples and 100 oranges"
        response = client.post('/api/breakdown',
                             data=json.dumps({'text': text}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        breakdown = data['breakdown']
        assert breakdown['100'] == 2
        assert breakdown['i'] == 1
        assert breakdown['have'] == 1
        assert breakdown['apples'] == 1
        assert breakdown['and'] == 1
        assert breakdown['oranges'] == 1
    
    def test_breakdown_empty_string(self, client):
        """Test breakdown with empty string"""
        response = client.post('/api/breakdown',
                             data=json.dumps({'text': ''}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['text'] == ''
        assert data['breakdown'] == {}
    
    def test_breakdown_whitespace_only(self, client):
        """Test breakdown with whitespace only"""
        response = client.post('/api/breakdown',
                             data=json.dumps({'text': '   \n\t  '}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['breakdown'] == {}
    
    def test_breakdown_null_text(self, client):
        """Test breakdown with null text"""
        response = client.post('/api/breakdown',
                             data=json.dumps({'text': None}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['text'] == ''
        assert data['breakdown'] == {}
    
    def test_breakdown_special_characters(self, client):
        """Test breakdown with special characters"""
        text = "@#$% hello &*() world !@# hello $%^"
        response = client.post('/api/breakdown',
                             data=json.dumps({'text': text}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        breakdown = data['breakdown']
        assert breakdown['hello'] == 2
        assert breakdown['world'] == 1
    
    def test_breakdown_missing_text_field(self, client):
        """Test breakdown endpoint with missing text field"""
        response = client.post('/api/breakdown',
                             data=json.dumps({'message': 'hello world'}),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['error'] == 'Missing text field in request'
    
    def test_breakdown_no_json_data(self, client):
        """Test breakdown endpoint with no JSON data"""
        response = client.post('/api/breakdown',
                             data=json.dumps({}),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['error'] == 'Missing text field in request'
    
    def test_breakdown_invalid_json(self, client):
        """Test breakdown endpoint with invalid JSON"""
        response = client.post('/api/breakdown',
                             data='invalid json',
                             content_type='application/json')
        
        assert response.status_code == 500
        data = response.get_json()
        assert data['error'] == 'Internal server error'
    
    @patch('app.Counter')
    def test_breakdown_exception_handling(self, mock_counter, client):
        """Test breakdown endpoint exception handling"""
        mock_counter.side_effect = Exception('Test exception')
        
        response = client.post('/api/breakdown',
                             data=json.dumps({'text': 'hello world'}),
                             content_type='application/json')
        
        assert response.status_code == 500
        data = response.get_json()
        assert data['error'] == 'Internal server error'
    
    # ====================
    # HTTP METHOD TESTS
    # ====================
    
    def test_count_endpoint_get_method_not_allowed(self, client):
        """Test that GET method is not allowed on count endpoint"""
        response = client.get('/api/count')
        assert response.status_code == 405  # Method Not Allowed
    
    def test_breakdown_endpoint_get_method_not_allowed(self, client):
        """Test that GET method is not allowed on breakdown endpoint"""
        response = client.get('/api/breakdown')
        assert response.status_code == 405  # Method Not Allowed
    
    def test_health_check_post_method_not_allowed(self, client):
        """Test that POST method is not allowed on health check endpoint"""
        response = client.post('/')
        assert response.status_code == 405  # Method Not Allowed
    
    # ====================
    # EDGE CASES AND STRESS TESTS
    # ====================
    
    def test_very_long_text(self, client):
        """Test with very long text"""
        # Create a long text with repeated words
        long_text = ' '.join(['word'] * 1000 + ['different'] * 500)
        response = client.post('/api/count',
                             data=json.dumps({'text': long_text}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] == 1500
    
    def test_very_long_text_breakdown(self, client):
        """Test breakdown with very long text"""
        long_text = ' '.join(['word'] * 1000 + ['different'] * 500)
        response = client.post('/api/breakdown',
                             data=json.dumps({'text': long_text}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['breakdown']['word'] == 1000
        assert data['breakdown']['different'] == 500
    
    def test_single_character_words(self, client):
        """Test with single character words"""
        text = "a b c d e f g"
        response = client.post('/api/count',
                             data=json.dumps({'text': text}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] == 7
    
    def test_repeated_whitespace(self, client):
        """Test with repeated whitespace between words"""
        text = "hello    world     test"
        response = client.post('/api/count',
                             data=json.dumps({'text': text}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] == 3
    
    def test_mixed_line_endings(self, client):
        """Test with mixed line endings"""
        text = "hello\nworld\r\ntest\rmore"
        response = client.post('/api/count',
                             data=json.dumps({'text': text}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] == 4
    
    # ====================
    # INTEGRATION TESTS
    # ====================
    
    def test_count_and_breakdown_consistency(self, client):
        """Test that count and breakdown endpoints are consistent"""
        text = "hello world hello test world hello"
        
        # Test count
        count_response = client.post('/api/count',
                                   data=json.dumps({'text': text}),
                                   content_type='application/json')
        
        # Test breakdown
        breakdown_response = client.post('/api/breakdown',
                                       data=json.dumps({'text': text}),
                                       content_type='application/json')
        
        assert count_response.status_code == 200
        assert breakdown_response.status_code == 200
        
        count_data = count_response.get_json()
        breakdown_data = breakdown_response.get_json()
        
        # Count should equal sum of all word frequencies
        total_words_from_breakdown = sum(breakdown_data['breakdown'].values())
        assert count_data['count'] == total_words_from_breakdown
        
        # Text should be identical in both responses
        assert count_data['text'] == breakdown_data['text'] == text


# ====================
# STANDALONE FUNCTION TESTS
# ====================

class TestAppConfiguration:
    """Test Flask app configuration and setup"""
    
    def test_app_exists(self):
        """Test that Flask app is created"""
        assert app.app is not None
        assert hasattr(app.app, 'route')
    
    def test_cors_enabled(self):
        """Test that CORS is enabled"""
        # This is more of a smoke test since CORS setup is hard to test directly
        with app.app.test_client() as client:
            response = client.options('/api/count')
            # OPTIONS should be handled by CORS
            assert response.status_code in [200, 405]  # Either CORS handles it or method not allowed
    
    def test_debug_mode_configuration(self):
        """Test app configuration"""
        # Test that app can be configured for testing
        app.app.config['TESTING'] = True
        assert app.app.config['TESTING'] is True


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])