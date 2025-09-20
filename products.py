import random
from flask import Flask, request, jsonify
from flask_cors import CORS

# Products list with 10 random fruits
# products = [
#     {
#         "id": 1,
#         "name": "Apple",
#         "price": 2.50,
#         "quantity": random.randint(10, 100)
#     },
#     {
#         "id": 2,
#         "name": "Banana",
#         "price": 1.25,
#         "quantity": random.randint(10, 100)
#     },
#     {
#         "id": 3,
#         "name": "Orange",
#         "price": 3.00,
#         "quantity": random.randint(10, 100)
#     },
#     {
#         "id": 4,
#         "name": "Strawberry",
#         "price": 4.75,
#         "quantity": random.randint(10, 100)
#     },
#     {
#         "id": 5,
#         "name": "Mango",
#         "price": 3.50,
#         "quantity": random.randint(10, 100)
#     },
#     {
#         "id": 6,
#         "name": "Pineapple",
#         "price": 5.00,
#         "quantity": random.randint(10, 100)
#     },
#     {
#         "id": 7,
#         "name": "Grapes",
#         "price": 4.25,
#         "quantity": random.randint(10, 100)
#     },
#     {
#         "id": 8,
#         "name": "Watermelon",
#         "price": 6.50,
#         "quantity": random.randint(10, 100)
#     },
#     {
#         "id": 9,
#         "name": "Peach",
#         "price": 3.25,
#         "quantity": random.randint(10, 100)
#     },
#     {
#         "id": 10,
#         "name": "Blueberry",
#         "price": 5.50,
#         "quantity": random.randint(10, 100)
#     }
# ]:

products = []

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

# CRUD Routes for Products

@app.route('/api/products', methods=['GET'])
def get_all_products():
    """
    Get all products or a specific product by ID
    Query parameters:
    - id (optional): Filter by product ID, returns single product object or 404 if not found
    Returns JSON array of all products or single product object
    """
    try:
        # Check if id parameter is provided
        product_id = request.args.get('id', type=int)
        
        if product_id is not None:
            # Return specific product by ID
            product = next((p for p in products if p['id'] == product_id), None)
            if product:
                return jsonify(product), 200
            else:
                return jsonify({'error': 'Product not found'}), 404
        else:
            # Return all products
            return jsonify(products), 200
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/products', methods=['POST'])
def create_product():
    """
    Create a new product
    Expects JSON: {'name': '...', 'price': float, 'quantity': int}
    Returns JSON: created product object
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Validate required fields
        required_fields = ['name', 'price', 'quantity']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate data types
        try:
            price = float(data['price'])
            quantity = int(data['quantity'])
            name = str(data['name']).strip()
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid data types. Price must be a number, quantity must be an integer'}), 400
        
        if not name:
            return jsonify({'error': 'Product name cannot be empty'}), 400
        
        if price < 0:
            return jsonify({'error': 'Price cannot be negative'}), 400
        
        if quantity < 0:
            return jsonify({'error': 'Quantity cannot be negative'}), 400
        
        # Generate new ID (max existing ID + 1)
        new_id = max(p['id'] for p in products) + 1 if products else 1
        
        # Create new product
        new_product = {
            'id': new_id,
            'name': name,
            'price': price,
            'quantity': quantity
        }
        
        # Add to products list
        products.append(new_product)
        
        return jsonify(new_product), 201
    
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """
    Update an existing product by ID
    Expects JSON: {'name': '...', 'price': float, 'quantity': int}
    Returns JSON: updated product object or 404 if not found
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Find the product
        product = next((p for p in products if p['id'] == product_id), None)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Update fields if provided
        if 'name' in data:
            name = str(data['name']).strip()
            if not name:
                return jsonify({'error': 'Product name cannot be empty'}), 400
            product['name'] = name
        
        if 'price' in data:
            try:
                price = float(data['price'])
                if price < 0:
                    return jsonify({'error': 'Price cannot be negative'}), 400
                product['price'] = price
            except (ValueError, TypeError):
                return jsonify({'error': 'Price must be a valid number'}), 400
        
        if 'quantity' in data:
            try:
                quantity = int(data['quantity'])
                if quantity < 0:
                    return jsonify({'error': 'Quantity cannot be negative'}), 400
                product['quantity'] = quantity
            except (ValueError, TypeError):
                return jsonify({'error': 'Quantity must be a valid integer'}), 400
        
        return jsonify(product), 200
    
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """
    Delete a product by ID
    Returns JSON: success message or 404 if not found
    """
    try:
        # Find the product index
        product_index = next((i for i, p in enumerate(products) if p['id'] == product_id), None)
        
        if product_index is None:
            return jsonify({'error': 'Product not found'}), 404
        
        # Remove the product
        deleted_product = products.pop(product_index)
        
        return jsonify({
            'message': 'Product deleted successfully',
            'deleted_product': deleted_product
        }), 200
    
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/', methods=['GET'])
def health_check():
    """
    Health check endpoint with API documentation
    """
    return jsonify({
        'message': 'Products API is running',
        'endpoints': {
            '/api/products': 'GET - Get all products (optional ?id=<id> for specific product), POST - Create new product',
            '/api/products/<id>': 'PUT - Update product, DELETE - Delete product'
        }
    })

# Display the products
if __name__ == "__main__":
    # Print initial products list
    print("Products API Starting...")
    print("Initial Products List:")
    print("-" * 50)
    for product in products:
        print(f"ID: {product['id']}")
        print(f"Name: {product['name']}")
        print(f"Price: ${product['price']:.2f}")
        print(f"Quantity: {product['quantity']}")
        print("-" * 30)
    
    print(f"\nTotal products: {len(products)}")
    print("\nStarting Flask server on http://0.0.0.0:5001...")
    print("Available endpoints:")
    print("  GET    /                     - Health check")
    print("  GET    /api/products         - Get all products")
    print("  GET    /api/products?id=<id> - Get product by ID")
    print("  POST   /api/products         - Create new product")
    print("  PUT    /api/products/<id>    - Update product")
    print("  DELETE /api/products/<id>    - Delete product")
    print("-" * 50)
    
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5001)
