# Tests Directory

This directory contains all unit and integration tests for the Products API.

## Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Pytest fixtures and configuration
├── test_products.py         # API endpoint tests (59 tests)
└── test_connection.py       # MongoDB connection tests (3 tests)
```

## Test Files

### test_products.py
Core API endpoint tests covering:
- **Helper Functions** (7 tests): ObjectId conversion, database connection checks
- **GET /api/products** (6 tests): Retrieve all products or specific product by ID
- **POST /api/products** (13 tests): Create new products with validation
- **PUT /api/products/<id>** (18 tests): Update existing products
- **DELETE /api/products/<id>** (7 tests): Delete products
- **Web UI & Health** (3 tests): Index route and health check endpoints
- **Edge Cases** (5 tests): Various edge case scenarios

### test_connection.py
MongoDB connection handling tests:
- Connection failure scenarios
- Ping failure handling
- Graceful degradation when database is unavailable

### conftest.py
Shared test configuration:
- Registers custom pytest markers (`unit`, `integration`, `slow`)
- Provides shared fixtures for test data and mocking

## Running Tests

### From project root:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=products --cov-report=term-missing

# Run with HTML coverage report
pytest --cov=products --cov-report=html

# Run specific test file
pytest tests/test_products.py

# Run specific test
pytest tests/test_products.py::test_get_all_products_success

# Run by marker
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
```

### From tests directory:

```bash
cd tests

# Run all tests in current directory
pytest .

# Run specific file
pytest test_products.py

# Verbose output
pytest -v
```

## Test Coverage

Current coverage: **100%** (excluding main block)

```
Name          Stmts   Miss  Cover
---------------------------------
products.py     183      0   100%
---------------------------------
TOTAL           183      0   100%
```

## Writing New Tests

### 1. Add test to appropriate file
- API endpoint tests → `test_products.py`
- Connection tests → `test_connection.py`
- New category → Create new `test_*.py` file

### 2. Use existing fixtures
```python
def test_example(client, mock_collection, sample_product):
    # client: Flask test client
    # mock_collection: Mocked MongoDB collection
    # sample_product: Sample product data
    pass
```

### 3. Mark tests appropriately
```python
@pytest.mark.unit
def test_helper_function():
    pass

@pytest.mark.integration
def test_api_endpoint(client):
    pass
```

### 4. Follow naming conventions
- Test files: `test_*.py`
- Test functions: `test_*`
- Test classes: `Test*`

## Test Patterns

### Mocking Database Operations
```python
with patch('products.products_collection', mock_collection):
    with patch('products.check_db_connection', return_value=(True, None, None)):
        response = client.get('/api/products')
        assert response.status_code == 200
```

### Testing Error Cases
```python
def test_invalid_input(client):
    with patch('products.check_db_connection', return_value=(True, None, None)):
        response = client.post('/api/products', json={
            'invalid_field': 'value'
        })
        assert response.status_code == 400
```

### Using Fixtures
```python
def test_with_sample_data(sample_product, mock_collection):
    mock_collection.find_one.return_value = sample_product
    # Test logic here
```

## Dependencies

All test dependencies are listed in `requirements.txt`:
- pytest==7.4.4
- pytest-cov==4.1.0
- pytest-mock==3.15.1

Install with:
```bash
pip install -r requirements.txt
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines:
- Fast execution (< 2 seconds)
- No external dependencies (uses mocking)
- Consistent results (deterministic)
- Clear output and error messages

## Troubleshooting

### Tests not found
```bash
# Check pytest configuration
pytest --collect-only

# Verify test path
pytest tests/ -v
```

### Import errors
```bash
# Run from project root
cd /path/to/product-management-full-stack-python
pytest

# Or set PYTHONPATH
export PYTHONPATH=/path/to/product-management-full-stack-python
pytest
```

### Coverage not working
```bash
# Install coverage
pip install pytest-cov

# Run with explicit source
pytest --cov=products --cov-report=term
```

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure coverage remains at 90%+
3. Test both success and error paths
4. Include edge cases
5. Update this README if adding new test files
