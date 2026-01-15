# Products API

A RESTful Flask API for managing products with full CRUD (Create, Read, Update, Delete) operations. This API provides endpoints to manage a product inventory system with features for adding, retrieving, updating, and deleting products.

## Overview

The Products API is built using Flask, Flask-CORS, and PyMongo, providing a robust backend for product management with persistent storage. It uses MongoDB as the database backend and offers JSON-based API endpoints for all operations. The API supports both MongoDB ObjectIds and custom integer IDs for maximum flexibility.

## Features

- ✅ **Full CRUD Operations**: Create, Read, Update, and Delete products
- ✅ **MongoDB Integration**: Persistent storage with MongoDB database
- ✅ **Modern Web UI**: Beautiful, responsive web interface for product management
- ✅ **Dark/Light Theme**: Toggle between dark and light themes with system preference detection
- ✅ **Flexible ID Support**: Works with both MongoDB ObjectIds and custom integer IDs
- ✅ **RESTful Design**: Clean, intuitive API endpoints
- ✅ **Data Validation**: Comprehensive input validation and error handling
- ✅ **CORS Support**: Cross-origin resource sharing enabled
- ✅ **Health Check**: Built-in status endpoint
- ✅ **JSON Responses**: All responses in JSON format
- ✅ **Error Handling**: Proper HTTP status codes and error messages
- ✅ **Environment Configuration**: Configurable via environment variables
- ✅ **Connection Resilience**: Graceful handling of database connection issues
- ✅ **Real-time Search**: Instant product search and filtering
- ✅ **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- ✅ **100% Test Coverage**: Comprehensive test suite with 62 tests
- ✅ **CI/CD Pipeline**: Automated testing on every push with GitHub Actions

## Installation

### Prerequisites

1. **Python Dependencies**:
   ```bash
   pip install flask flask-cors pymongo
   ```

2. **MongoDB Setup**:
   
   **Option A: Local MongoDB Installation**
   ```bash
   # macOS (using Homebrew)
   brew install mongodb-community
   brew services start mongodb-community
   
   # Ubuntu/Debian
   sudo apt-get install mongodb
   sudo systemctl start mongod
   
   # Windows - Download from https://www.mongodb.com/try/download/community
   ```
   
   **Option B: MongoDB Atlas (Cloud)**
   1. Create a free account at [MongoDB Atlas](https://www.mongodb.com/atlas)
   2. Create a new cluster
   3. Get your connection string
   4. Set the `MONGO_URI` environment variable
   
   **Option C: Docker**
   ```bash
   docker run -d -p 27017:27017 --name mongodb mongo:latest
   ```

### Configuration

The API uses environment variables for configuration:

```bash
# Optional - defaults shown
export MONGO_URI="mongodb://localhost:27017/"
export DATABASE_NAME="products_db"
export COLLECTION_NAME="products"
```

For MongoDB Atlas or remote instances:
```bash
export MONGO_URI="mongodb+srv://username:password@cluster.mongodb.net/"
```

### Running the API

```bash
python products.py
```

The server will start on `http://0.0.0.0:5001` with debug mode enabled.

**Note**: The API will automatically create the database and collection if they don't exist.

## Web UI Features

The application includes a modern, responsive web interface accessible at the root URL (`http://localhost:5001`). The UI provides:

### 🎨 Theme Support
- **Dark Theme**: Professional dark mode for comfortable viewing in low-light environments
- **Light Theme**: Clean, bright theme for daytime use
- **Automatic Detection**: Respects system theme preference by default
- **Manual Toggle**: Easy one-click theme switching with persistent storage
- **Smooth Transitions**: Seamless animations when switching themes

### 📏 Product Management
- **Add Products**: Intuitive form with real-time validation
- **View Products**: Card-based layout with all product details
- **Edit Products**: In-place editing with modal dialogs
- **Delete Products**: Safe deletion with confirmation prompts
- **Search & Filter**: Real-time search by product name

### 📱 User Experience
- **Responsive Design**: Optimized for all screen sizes (mobile, tablet, desktop)
- **Keyboard Shortcuts**: ESC to close modals, Enter to submit forms
- **Loading States**: Visual feedback during API operations
- **Error Handling**: User-friendly error messages and validation
- **Success Notifications**: Confirmation messages for completed actions
- **Empty States**: Helpful guidance when no products exist

### 🔧 Technical Features
- **Progressive Enhancement**: Works without JavaScript (basic functionality)
- **Local Storage**: Theme preferences saved between sessions
- **System Integration**: Respects OS-level theme preferences
- **Accessibility**: ARIA labels, keyboard navigation, screen reader friendly
- **Performance**: Optimized loading and smooth animations

## Data Model

Each product has the following structure:

```json
{
  "id": 1,
  "name": "Product Name",
  "price": 9.99,
  "quantity": 50
}
```

### Field Descriptions

- **id**: `string` - Unique identifier (auto-generated integer, converted to string in responses)
- **name**: `string` - Product name (required, non-empty)
- **price**: `float` - Product price (required, non-negative)
- **quantity**: `integer` - Stock quantity (required, non-negative)

**Note**: The API uses MongoDB for storage. Products are stored with both a MongoDB `_id` (ObjectId) and a custom `id` field (integer). API responses use the custom `id` field for consistency, but both can be used for querying.

## API Endpoints

### 1. Health Check

**GET** `/`

Returns API status and available endpoints.

**Response:**
```json
{
  "message": "Products API is running",
  "endpoints": {
    "/api/products": "GET - Get all products (optional ?id=<id> for specific product), POST - Create new product",
    "/api/products/<id>": "PUT - Update product, DELETE - Delete product"
  }
}
```

### 2. Get All Products or Specific Product

**GET** `/api/products` or **GET** `/api/products?id=<product_id>`

Retrieves all products in the inventory or a specific product by ID.

**Query Parameters:**
- `id` (optional): Integer ID of a specific product to retrieve

**Response:**
- **200 OK**: Array of product objects (all products) or single product object (specific product)
- **404 Not Found**: Product not found (when using id parameter)
- **500 Internal Server Error**: Server error

**Example Response (All Products):**
```json
[
  {
    "id": 1,
    "name": "Apple",
    "price": 2.50,
    "quantity": 25
  },
  {
    "id": 2,
    "name": "Banana",
    "price": 1.25,
    "quantity": 40
  }
]
```

**Example Response (Specific Product with ?id=1):**
```json
{
  "id": 1,
  "name": "Apple",
  "price": 2.50,
  "quantity": 25
}
```

### 3. Create New Product

**POST** `/api/products`

Creates a new product in the inventory.

**Request Body:**
```json
{
  "name": "Product Name",
  "price": 9.99,
  "quantity": 50
}
```

**Validation Rules:**
- `name`: Required, non-empty string
- `price`: Required, non-negative number
- `quantity`: Required, non-negative integer

**Response:**
- **201 Created**: Created product object
- **400 Bad Request**: Validation errors
- **500 Internal Server Error**: Server error

**Example Response:**
```json
{
  "id": 3,
  "name": "Product Name",
  "price": 9.99,
  "quantity": 50
}
```

### 4. Update Product

**PUT** `/api/products/<int:product_id>`

Updates an existing product. Only provided fields will be updated.

**Parameters:**
- `product_id` (path parameter): Integer ID of the product to update

**Request Body** (all fields optional):
```json
{
  "name": "Updated Name",
  "price": 12.99,
  "quantity": 30
}
```

**Validation Rules:**
- `name`: If provided, must be non-empty string
- `price`: If provided, must be non-negative number
- `quantity`: If provided, must be non-negative integer

**Response:**
- **200 OK**: Updated product object
- **400 Bad Request**: Validation errors
- **404 Not Found**: Product not found
- **500 Internal Server Error**: Server error

### 5. Delete Product

**DELETE** `/api/products/<int:product_id>`

Deletes a product from the inventory.

**Parameters:**
- `product_id` (path parameter): Integer ID of the product to delete

**Response:**
- **200 OK**: Success message with deleted product details
- **404 Not Found**: Product not found
- **500 Internal Server Error**: Server error

**Example Response:**
```json
{
  "message": "Product deleted successfully",
  "deleted_product": {
    "id": 1,
    "name": "Apple",
    "price": 2.50,
    "quantity": 25
  }
}
```

## Error Responses

All errors follow a consistent format:

```json
{
  "error": "Error message description"
}
```

### Common Error Codes

- **400 Bad Request**: Invalid input data or missing required fields
- **404 Not Found**: Requested product doesn't exist
- **500 Internal Server Error**: Server-side error

## Usage Examples

### Using cURL

#### 1. Health Check
```bash
# Check if the API is running
curl -X GET http://localhost:5001/
```

#### 2. Get All Products or Specific Product
```bash
# Retrieve all products in the inventory
curl -X GET http://localhost:5001/api/products

# With pretty-printed JSON output
curl -X GET http://localhost:5001/api/products | jq .

# Get a specific product by ID using query parameter
curl -X GET "http://localhost:5001/api/products?id=1"

# Get specific product with error handling for non-existent product
curl -X GET "http://localhost:5001/api/products?id=999"

# Multiple ways to get specific product (URL encoding)
curl -X GET 'http://localhost:5001/api/products?id=1'
```

#### 3. Create New Product
```bash
# Create a simple product
curl -X POST http://localhost:5001/api/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Orange", "price": 3.00, "quantity": 20}'

# Create multiple products (run separately)
curl -X POST http://localhost:5001/api/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Apple", "price": 2.50, "quantity": 15}'

curl -X POST http://localhost:5001/api/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Banana", "price": 1.25, "quantity": 30}'

curl -X POST http://localhost:5001/api/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Grapes", "price": 4.25, "quantity": 25}'

# Example with validation error (missing required field)
curl -X POST http://localhost:5001/api/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Incomplete Product", "price": 5.00}'
```

#### 4. Update Product
```bash
# Update only the price
curl -X PUT http://localhost:5001/api/products/1 \
  -H "Content-Type: application/json" \
  -d '{"price": 2.75}'

# Update only the quantity
curl -X PUT http://localhost:5001/api/products/1 \
  -H "Content-Type: application/json" \
  -d '{"quantity": 50}'

# Update multiple fields at once
curl -X PUT http://localhost:5001/api/products/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Red Apple", "price": 3.25, "quantity": 40}'

# Update non-existent product (will return 404)
curl -X PUT http://localhost:5001/api/products/999 \
  -H "Content-Type: application/json" \
  -d '{"price": 1.00}'
```

#### 5. Delete Product
```bash
# Delete a specific product
curl -X DELETE http://localhost:5001/api/products/1

# Try to delete non-existent product (will return 404)
curl -X DELETE http://localhost:5001/api/products/999
```

#### Complete Workflow Example
```bash
# 1. Check API status
echo "=== Checking API Status ==="
curl -X GET http://localhost:5001/

# 2. Get initial products list (should be empty)
echo -e "\n\n=== Initial Products List ==="
curl -X GET http://localhost:5001/api/products

# 3. Create some products
echo -e "\n\n=== Creating Products ==="
curl -X POST http://localhost:5001/api/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Apple", "price": 2.50, "quantity": 15}'

echo -e "\n"
curl -X POST http://localhost:5001/api/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Banana", "price": 1.25, "quantity": 30}'

# 4. Get all products (should now show 2 products)
echo -e "\n\n=== Products After Creation ==="
curl -X GET http://localhost:5001/api/products

# 5. Get specific product
echo -e "\n\n=== Get Product by ID ==="
curl -X GET "http://localhost:5001/api/products?id=1"

# 6. Update a product
echo -e "\n\n=== Update Product ==="
curl -X PUT http://localhost:5001/api/products/1 \
  -H "Content-Type: application/json" \
  -d '{"price": 2.75, "quantity": 20}'

# 7. Verify update
echo -e "\n\n=== Verify Update ==="
curl -X GET "http://localhost:5001/api/products?id=1"

# 8. Delete a product
echo -e "\n\n=== Delete Product ==="
curl -X DELETE http://localhost:5001/api/products/2

# 9. Final products list
echo -e "\n\n=== Final Products List ==="
curl -X GET http://localhost:5001/api/products
```

#### Advanced cURL Options
```bash
# Include response headers
curl -i -X GET http://localhost:5001/api/products

# Show request and response details (verbose)
curl -v -X GET http://localhost:5001/api/products

# Save response to file
curl -X GET http://localhost:5001/api/products -o products.json

# Follow redirects and show only HTTP status
curl -L -w "%{http_code}\n" -s -o /dev/null http://localhost:5001/api/products

# Set custom timeout
curl --max-time 30 -X GET http://localhost:5001/api/products

# Pretty print JSON response using jq (if available)
curl -s -X GET http://localhost:5001/api/products | jq .
```

### Using Python Requests

```python
import requests

base_url = "http://localhost:5001/api/products"

# Get all products
response = requests.get(base_url)
products = response.json()

# Create a product
new_product = {
    "name": "Grapes",
    "price": 4.25,
    "quantity": 15
}
response = requests.post(base_url, json=new_product)
created_product = response.json()

# Update a product
update_data = {"quantity": 25}
response = requests.put(f"{base_url}/1", json=update_data)
updated_product = response.json()

# Delete a product
response = requests.delete(f"{base_url}/1")
result = response.json()
```

## Configuration

The API runs with the following default configuration:

### Server Configuration
- **Host**: `0.0.0.0` (accessible from all network interfaces)
- **Port**: `5001`
- **Debug Mode**: `True` (should be disabled in production)
- **CORS**: Enabled for all domains

### Database Configuration (Environment Variables)
- **MONGO_URI**: `mongodb://localhost:27017/` (MongoDB connection string)
- **DATABASE_NAME**: `products_db` (Database name)
- **COLLECTION_NAME**: `products` (Collection name)

### Example Environment Setup
```bash
# Local MongoDB
export MONGO_URI="mongodb://localhost:27017/"

# MongoDB Atlas
export MONGO_URI="mongodb+srv://username:password@cluster.mongodb.net/"

# Custom database/collection names
export DATABASE_NAME="my_store_db"
export COLLECTION_NAME="inventory"
```

## Notes

- **persistent Storage**: Products are stored in MongoDB and persist across server restarts
- **ID Support**: Supports both MongoDB ObjectIds and custom integer IDs for queries
- **Auto-Indexing**: MongoDB automatically creates indexes for efficient querying
- **Connection Handling**: API gracefully handles database connection failures
- **Data Consistency**: Uses MongoDB's ACID properties for data integrity
- **Scalability**: MongoDB provides horizontal scaling capabilities for production use

## Development

The API includes comprehensive logging and debug information when run in debug mode. All endpoints include proper error handling and validation to ensure data integrity.

For production deployment, consider:
- Using a persistent database (PostgreSQL, MySQL, etc.)
- Implementing authentication and authorization
- Adding rate limiting
- Setting up proper logging
- Configuring environment-specific settings
- Disabling debug mode

## Dependencies

- `Flask`: Web framework for API endpoints
- `Flask-CORS`: Cross-origin resource sharing support
- `PyMongo`: MongoDB driver for Python
- `MongoDB`: NoSQL database for persistent storage
- `BSON`: Binary JSON format used by MongoDB

### MongoDB Requirements

- MongoDB Server 4.0+ (local installation, Atlas, or Docker)
- Network connectivity to MongoDB instance
- Sufficient disk space for data storage

---

**Author**: Generated from products.py  
**Version**: 1.0  
**Last Updated**: 2025-09-20

## Project Screenshots

![Jenkins Stages](images/1.jenkins-stages.png)
![Jenkins Pipeline](images/2.jenkins-pipeline.png)
![GitHub Actions Test Coverage](images/3.github-actions-test-coverage.png)
![GitHub Actions Docker](images/4.github-actions-docker.png)