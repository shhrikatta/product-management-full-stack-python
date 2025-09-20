# Word Count Backend API

A Flask-based REST API for counting words and analyzing word frequency in text.

## Features

- **Word Count**: Get the total number of words in a text
- **Word Breakdown**: Get frequency analysis of each word in the text
- **CORS Enabled**: Supports cross-origin requests from all domains
- **Error Handling**: Proper error responses for invalid requests

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### 1. Word Count - `/api/count`

**Method**: POST  
**Content-Type**: application/json

**Request Body**:
```json
{
  "text": "Your text here"
}
```

**Response**:
```json
{
  "text": "Your text here",
  "count": 10
}
```

**Example**:
```bash
curl -X POST http://localhost:5000/api/count \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world this is a test"}'
```

### 2. Word Breakdown - `/api/breakdown`

**Method**: POST  
**Content-Type**: application/json

**Request Body**:
```json
{
  "text": "Your text here"
}
```

**Response**:
```json
{
  "text": "hello world hello this",
  "breakdown": {
    "hello": 2,
    "world": 1,
    "this": 1
  }
}
```

**Example**:
```bash
curl -X POST http://localhost:5000/api/breakdown \
  -H "Content-Type: application/json" \
  -d '{"text": "hello world hello this"}'
```

### 3. Health Check - `/`

**Method**: GET

**Response**:
```json
{
  "message": "Word Count API is running",
  "endpoints": {
    "/api/count": "POST - Count total words in text",
    "/api/breakdown": "POST - Get word frequency breakdown"
  }
}
```

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `400`: Bad Request (missing or invalid data)
- `500`: Internal Server Error

Error responses include a descriptive message:
```json
{
  "error": "Missing text field in request"
}
```

## Dependencies

- Flask 3.0.2
- Flask-CORS 4.0.1
- pytest 7.4.4 (for testing)
- pytest-cov 4.1.0 (for coverage reporting)

## Testing

The project includes comprehensive unit tests with maximum coverage.

### Running Tests

1. Install test dependencies:
```bash
pip install -r requirements.txt
```

2. Run all tests:
```bash
pytest test_app.py -v
```

3. Run tests with coverage report:
```bash
pytest test_app.py --cov=app --cov-report=term-missing
```

4. Generate HTML coverage report:
```bash
pytest test_app.py --cov=app --cov-report=html
```

### Test Coverage

The test suite achieves **98% code coverage** and includes:

- **Happy Path Tests**: Normal operation with valid inputs
- **Edge Cases**: Empty strings, null values, special characters, unicode text
- **Error Handling**: Invalid JSON, missing fields, malformed requests
- **HTTP Method Tests**: Ensuring correct HTTP methods are enforced
- **Integration Tests**: Consistency between different endpoints
- **Stress Tests**: Very long text inputs and performance edge cases
- **Exception Handling**: Mocked failures and error recovery

### Test Structure

- `test_app.py`: Main test file with comprehensive test cases
- `TestWordCountAPI`: Tests for all API endpoints
- `TestAppConfiguration`: Tests for Flask app setup and configuration

### Test Categories

1. **Health Check Tests**: Verify the root endpoint
2. **Count Endpoint Tests**: `/api/count` functionality
3. **Breakdown Endpoint Tests**: `/api/breakdown` functionality  
4. **HTTP Method Tests**: Proper method enforcement
5. **Edge Cases**: Boundary conditions and special inputs
6. **Integration Tests**: Cross-endpoint consistency
