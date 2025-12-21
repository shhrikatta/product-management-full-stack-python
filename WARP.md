# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

A Flask-based RESTful API for product management with MongoDB persistence and a modern web UI featuring dark/light theme support. This is a full-stack application with a Python backend and vanilla JavaScript frontend.

## Architecture

### Backend Structure
- **products.py**: Monolithic Flask application containing all API routes, database logic, and server configuration
  - MongoDB connection and configuration (lines 9-34)
  - Helper functions for ObjectId conversion (lines 37-58)
  - CRUD endpoints for products (lines 62-299)
  - Web UI and health check routes (lines 301-323)
  - Startup logic with database statistics (lines 326-end)

### Frontend Structure
- **templates/index.html**: Single-page web interface with embedded HTML/CSS/JavaScript
- **static/css/**: Stylesheets for UI theming
- **static/js/**: Client-side JavaScript for API interaction and UI behavior

### Database Design
- **MongoDB**: NoSQL database with flexible schema
- **Dual ID System**: Both MongoDB ObjectId (`_id`) and custom integer ID (`id`) are supported
  - API responses use the custom `id` field for consistency
  - Both ID types can be used for querying products
- **Collections**: Single `products` collection (configurable via `COLLECTION_NAME` env var)

### Key Design Patterns
- Helper functions convert MongoDB ObjectIds to strings for JSON serialization
- Database connection checked on every request with graceful error handling
- Validation logic embedded in route handlers (no separate validation layer)
- Progressive ID generation: finds max ID and increments by 1

## Development Commands

### Running the Application
```bash
python products.py
```
Server starts on `http://0.0.0.0:5001` with debug mode enabled. Web UI accessible at root URL.

### Testing
```bash
# Run all tests with coverage
pytest --cov

# Run tests with verbose output
pytest -v

# Run specific test markers
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m "not slow"    # Exclude slow tests

# Generate HTML coverage report
pytest --cov --cov-report=html
# View at htmlcov/index.html
```

### Database Setup
```bash
# Option 1: Local MongoDB (macOS)
brew install mongodb-community
brew services start mongodb-community

# Option 2: MongoDB in Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Option 3: Set MongoDB Atlas connection
export MONGO_URI="mongodb+srv://username:password@cluster.mongodb.net/"
```

## Environment Configuration

### Required Environment Variables
None - all have defaults

### Optional Environment Variables
```bash
# MongoDB connection string (default: embedded Atlas connection)
export MONGO_URI="mongodb://localhost:27017/"

# Database name (default: "products")
export DATABASE_NAME="products_db"

# Collection name (default: "fruits")
export COLLECTION_NAME="products"
```

**IMPORTANT**: The code currently contains a hardcoded MongoDB Atlas connection string in `products.py:10`. This should be removed before committing any changes or sharing the code.

## API Testing

### Using cURL
```bash
# Health check
curl http://localhost:5001/health

# Get all products
curl http://localhost:5001/api/products

# Get specific product
curl "http://localhost:5001/api/products?id=1"

# Create product
curl -X POST http://localhost:5001/api/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Apple", "price": 2.50, "quantity": 15}'

# Update product
curl -X PUT http://localhost:5001/api/products/1 \
  -H "Content-Type: application/json" \
  -d '{"price": 2.75}'

# Delete product
curl -X DELETE http://localhost:5001/api/products/1
```

## Code Modification Guidelines

### Adding New Product Fields
1. Update the validation logic in `create_product()` (lines 128-148)
2. Add field handling in `update_product()` (lines 214-237)
3. Update the data model documentation in README.md
4. Consider migration strategy for existing products

### Adding New Endpoints
- Follow the existing pattern: check DB connection, validate input, handle errors
- Use `convert_objectid_to_str()` for all responses that include product data
- Return proper HTTP status codes (200, 201, 400, 404, 500)
- Support both ObjectId and custom integer ID in path parameters

### Database Queries
- Use `products_collection.find_one()` for single documents
- Use `list(products_collection.find())` for multiple documents
- Always convert ObjectIds before returning JSON responses
- Check `ObjectId.is_valid()` before attempting ObjectId conversion

### Frontend Modifications
- Theme toggle logic is in index.html (uses localStorage)
- API calls use fetch() with async/await pattern
- Modal dialogs handle form submissions
- Real-time search filters products client-side

## Common Pitfalls

### MongoDB Connection Issues
- The app continues running even if MongoDB connection fails
- All endpoints check connection and return 500 if unavailable
- Connection is established once at startup (not pooled per request)

### ID Confusion
- API accepts both MongoDB ObjectId (24-char hex) and custom integer ID
- Responses always use the custom `id` field, never expose `_id`
- When querying, code attempts ObjectId first, then falls back to integer ID

### CORS Configuration
- CORS enabled for all domains (`CORS(app)`)
- No authentication or rate limiting implemented
- Debug mode is enabled by default (should be disabled in production)

## Dependencies

Install via: `pip install -r requirements.txt`

- Flask 3.0.2: Web framework
- Flask-CORS 4.0.1: Cross-origin resource sharing
- pymongo (implicit): MongoDB driver
- pytest 7.4.4: Testing framework
- pytest-cov 4.1.0: Coverage reporting

**Note**: pymongo is not listed in requirements.txt but is required. Add it with: `pip install pymongo`
