# Project Structure

## Overview
```
product-management-full-stack-python/
├── .coveragerc                 # Coverage configuration
├── .git/                       # Git repository
├── pytest.ini                  # Pytest configuration
├── requirements.txt            # Python dependencies
├── products.py                 # Main Flask application
├── README.md                   # Project documentation
├── TEST_COVERAGE.md           # Test coverage report
├── WARP.md                    # Warp AI context
├── PROJECT_STRUCTURE.md       # This file
│
├── static/                    # Static web assets
│   ├── css/                   # Stylesheets
│   └── js/                    # JavaScript files
│
├── templates/                 # HTML templates
│   └── index.html            # Main web interface
│
├── tests/                     # ⭐ Test suite directory
│   ├── __init__.py           # Test package initialization
│   ├── README.md             # Tests documentation
│   ├── conftest.py           # Pytest fixtures and markers
│   ├── test_products.py      # API endpoint tests (59 tests)
│   └── test_connection.py    # Connection tests (3 tests)
│
├── venv/                      # Virtual environment (excluded from git)
├── htmlcov/                   # Coverage HTML reports (excluded from git)
└── __pycache__/              # Python cache (excluded from git)
```

## Key Files

### Application Files
- **products.py** (373 lines)
  - Flask application with REST API
  - MongoDB integration
  - CRUD operations for products
  - Health check and web UI routes

### Configuration Files
- **pytest.ini**
  - Test discovery path: `tests/`
  - Custom markers: `unit`, `integration`, `slow`
  - Pytest options and settings

- **.coveragerc**
  - Coverage exclusions
  - Omits `if __name__ == "__main__"` block
  - Excludes test files from coverage

- **requirements.txt**
  - Flask==3.0.2
  - Flask-CORS==4.0.1
  - pymongo==4.15.5
  - pytest==7.4.4
  - pytest-cov==4.1.0
  - pytest-mock==3.15.1

### Test Files (tests/ directory)

#### test_products.py (59 tests)
Comprehensive API endpoint tests:
- Helper functions (7 tests)
- GET /api/products (6 tests)
- POST /api/products (13 tests)
- PUT /api/products/<id> (18 tests)
- DELETE /api/products/<id> (7 tests)
- Web UI & Health (3 tests)
- Edge cases (5 tests)

#### test_connection.py (3 tests)
MongoDB connection scenarios:
- Connection failure handling
- Ping failure scenarios
- Graceful degradation

#### conftest.py
Test configuration:
- Registers custom pytest markers
- Provides shared fixtures:
  - `client`: Flask test client
  - `mock_collection`: Mocked MongoDB collection
  - `sample_product`: Sample product data
  - `sample_products`: List of sample products

## Test Coverage

### Current Status
```
Name          Stmts   Miss  Cover
---------------------------------
products.py     183      0   100%
---------------------------------
TOTAL           183      0   100%
```

- **Total Tests**: 62
- **Coverage**: 100% (excluding main block)
- **Status**: ✅ All passing
- **Execution Time**: ~1.5 seconds

### Coverage Details
- ✅ All API endpoints covered
- ✅ All helper functions tested
- ✅ Input validation tested
- ✅ Error handling tested
- ✅ Edge cases included
- ✅ Database failure scenarios covered

## Running Tests

### Quick Commands
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=products

# Run specific file
pytest tests/test_products.py

# Run by marker
pytest -m unit
pytest -m integration

# Generate HTML report
pytest --cov=products --cov-report=html
```

### From tests directory
```bash
cd tests
pytest .
pytest test_products.py
pytest -v
```

## Development Workflow

### 1. Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Application
```bash
python products.py
```
Access at: http://localhost:5002

### 3. Run Tests
```bash
# Run tests with coverage
pytest --cov=products --cov-report=term-missing

# Watch for changes (requires pytest-watch)
pytest-watch
```

### 4. Check Coverage
```bash
# Terminal report
pytest --cov=products --cov-report=term-missing

# HTML report (view in browser)
pytest --cov=products --cov-report=html
open htmlcov/index.html
```

## Documentation

- **README.md** - Project overview, setup instructions, API documentation
- **TEST_COVERAGE.md** - Detailed test coverage report
- **tests/README.md** - Test directory documentation
- **WARP.md** - Context for Warp AI assistant
- **PROJECT_STRUCTURE.md** - This file

## Technology Stack

### Backend
- **Flask** 3.0.2 - Web framework
- **Flask-CORS** 4.0.1 - CORS support
- **pymongo** 4.15.5 - MongoDB driver

### Database
- **MongoDB** - NoSQL database
- Dual ID system (ObjectId and custom integer ID)
- Collections: configurable via environment variables

### Testing
- **pytest** 7.4.4 - Test framework
- **pytest-cov** 4.1.0 - Coverage plugin
- **pytest-mock** 3.15.1 - Mocking utilities
- **unittest.mock** - Standard library mocking

### Frontend
- Vanilla JavaScript
- HTML5/CSS3
- Dark/Light theme support

## Environment Variables

```bash
# MongoDB Configuration
MONGO_URI="mongodb://localhost:27017/"  # MongoDB connection string
DATABASE_NAME="products"                # Database name
COLLECTION_NAME="fruits"                # Collection name
```

## Git Ignore

Excluded from version control:
- `venv/` - Virtual environment
- `__pycache__/` - Python cache
- `htmlcov/` - Coverage reports
- `.pytest_cache/` - Pytest cache
- `*.pyc` - Compiled Python files
- `.DS_Store` - macOS system files

## Best Practices

### Testing
1. Write tests first (TDD)
2. Maintain 90%+ coverage
3. Test success and error paths
4. Include edge cases
5. Use descriptive test names
6. Mock external dependencies

### Code Organization
1. Keep tests in `tests/` directory
2. One test file per module
3. Use fixtures for reusable data
4. Group related tests with markers
5. Document complex test scenarios

### Development
1. Use virtual environment
2. Keep dependencies updated
3. Run tests before committing
4. Follow existing code patterns
5. Update documentation

## Troubleshooting

### Tests not found
```bash
pytest --collect-only  # Check test discovery
```

### Import errors
```bash
# Ensure you're in project root
export PYTHONPATH=$(pwd)
```

### Coverage issues
```bash
# Reinstall coverage
pip install --upgrade pytest-cov
```

### MongoDB connection
```bash
# Check MongoDB is running
# Set MONGO_URI environment variable
export MONGO_URI="mongodb://localhost:27017/"
```

## Future Enhancements

- [ ] Add authentication tests
- [ ] Add rate limiting tests
- [ ] Add caching tests
- [ ] Add API versioning tests
- [ ] Add integration tests with real MongoDB
- [ ] Add performance tests
- [ ] Add security tests
- [ ] CI/CD pipeline configuration
