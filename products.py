import random
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.errors import InvalidId
import os


# MongoDB Configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://shhrikatta_db_user:FkHyvvUzwokaS8nl@charan-cluster-aws.idct1pl.mongodb.net/?retryWrites=true&w=majority&appName=charan-cluster-aws')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'products')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'fruits')

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

# MongoDB Connection
try:
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    products_collection = db[COLLECTION_NAME]
    
    # Test the connection
    client.admin.command('ping')
    print(f"✅ Successfully connected to MongoDB at {MONGO_URI}")
    print(f"📁 Using database: {DATABASE_NAME}")
    print(f"📄 Using collection: {COLLECTION_NAME}")
except Exception as e:
    print(f"❌ Failed to connect to MongoDB: {e}")
    print("⚠️  Application will continue but database operations will fail")
    client = None
    db = None
    products_collection = None

# Helper Functions
def convert_objectid_to_str(document):
    """
    Convert MongoDB ObjectId to string for JSON serialization
    """
    if document and '_id' in document:
        document['id'] = str(document['_id'])
        del document['_id']
    return document

def convert_objectid_list_to_str(documents):
    """
    Convert list of MongoDB documents with ObjectId to JSON serializable format
    """
    return [convert_objectid_to_str(doc) for doc in documents]

def check_db_connection():
    """
    Check if database connection is available
    """
    if products_collection is None:
        return False, {'error': 'Database connection not available'}, 500
    return True, None, None

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
        # Check database connection
        connected, error_response, status_code = check_db_connection()
        if not connected:
            return jsonify(error_response), status_code
        
        # Check if id parameter is provided
        product_id = request.args.get('id')
        
        if product_id is not None:
            # Return specific product by ID
            try:
                # Try to convert to ObjectId if it's a valid ObjectId format
                if ObjectId.is_valid(product_id):
                    query = {'_id': ObjectId(product_id)}
                else:
                    # Try to find by custom id field (integer)
                    try:
                        query = {'id': int(product_id)}
                    except ValueError:
                        return jsonify({'error': 'Invalid product ID format'}), 400
                
                product = products_collection.find_one(query)
                if product:
                    return jsonify(convert_objectid_to_str(product)), 200
                else:
                    return jsonify({'error': 'Product not found'}), 404
            except InvalidId:
                return jsonify({'error': 'Invalid product ID format'}), 400
        else:
            # Return all products
            products = list(products_collection.find())
            return jsonify(convert_objectid_list_to_str(products)), 200
            
    except Exception as e:
        print(f"Error in get_all_products: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/products', methods=['POST'])
def create_product():
    """
    Create a new product
    Expects JSON: {'name': '...', 'price': float, 'quantity': int}
    Returns JSON: created product object
    """
    try:
        # Check database connection
        connected, error_response, status_code = check_db_connection()
        if not connected:
            return jsonify(error_response), status_code
            
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
        
        # Generate new ID (find max existing custom ID + 1)
        max_id_doc = products_collection.find_one(sort=[('id', -1)])
        new_id = (max_id_doc['id'] + 1) if max_id_doc and 'id' in max_id_doc else 1
        
        # Create new product document
        new_product = {
            'id': new_id,
            'name': name,
            'price': price,
            'quantity': quantity
        }
        
        # Insert into MongoDB
        result = products_collection.insert_one(new_product)
        
        if result.inserted_id:
            # Retrieve the created product to return
            created_product = products_collection.find_one({'_id': result.inserted_id})
            return jsonify(convert_objectid_to_str(created_product)), 201
        else:
            return jsonify({'error': 'Failed to create product'}), 500
    
    except Exception as e:
        print(f"Error in create_product: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/products/<product_id>', methods=['PUT'])
def update_product(product_id):
    """
    Update an existing product by ID (supports both ObjectId and custom integer ID)
    Expects JSON: {'name': '...', 'price': float, 'quantity': int}
    Returns JSON: updated product object or 404 if not found
    """
    try:
        # Check database connection
        connected, error_response, status_code = check_db_connection()
        if not connected:
            return jsonify(error_response), status_code
            
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Build query for finding the product
        try:
            if ObjectId.is_valid(product_id):
                query = {'_id': ObjectId(product_id)}
            else:
                try:
                    query = {'id': int(product_id)}
                except ValueError:
                    return jsonify({'error': 'Invalid product ID format'}), 400
        except InvalidId:
            return jsonify({'error': 'Invalid product ID format'}), 400
        
        # Check if product exists
        existing_product = products_collection.find_one(query)
        if not existing_product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Prepare update data
        update_data = {}
        
        # Update fields if provided
        if 'name' in data:
            name = str(data['name']).strip()
            if not name:
                return jsonify({'error': 'Product name cannot be empty'}), 400
            update_data['name'] = name
        
        if 'price' in data:
            try:
                price = float(data['price'])
                if price < 0:
                    return jsonify({'error': 'Price cannot be negative'}), 400
                update_data['price'] = price
            except (ValueError, TypeError):
                return jsonify({'error': 'Price must be a valid number'}), 400
        
        if 'quantity' in data:
            try:
                quantity = int(data['quantity'])
                if quantity < 0:
                    return jsonify({'error': 'Quantity cannot be negative'}), 400
                update_data['quantity'] = quantity
            except (ValueError, TypeError):
                return jsonify({'error': 'Quantity must be a valid integer'}), 400
        
        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # Update the product in MongoDB
        result = products_collection.update_one(query, {'$set': update_data})
        
        if result.modified_count > 0 or result.matched_count > 0:
            # Retrieve the updated product
            updated_product = products_collection.find_one(query)
            return jsonify(convert_objectid_to_str(updated_product)), 200
        else:
            return jsonify({'error': 'Failed to update product'}), 500
    
    except Exception as e:
        print(f"Error in update_product: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    """
    Delete a product by ID (supports both ObjectId and custom integer ID)
    Returns JSON: success message or 404 if not found
    """
    try:
        # Check database connection
        connected, error_response, status_code = check_db_connection()
        if not connected:
            return jsonify(error_response), status_code
        
        # Build query for finding the product
        try:
            if ObjectId.is_valid(product_id):
                query = {'_id': ObjectId(product_id)}
            else:
                try:
                    query = {'id': int(product_id)}
                except ValueError:
                    return jsonify({'error': 'Invalid product ID format'}), 400
        except InvalidId:
            return jsonify({'error': 'Invalid product ID format'}), 400
        
        # Find the product first to return it in the response
        product_to_delete = products_collection.find_one(query)
        
        if not product_to_delete:
            return jsonify({'error': 'Product not found'}), 404
        
        # Delete the product
        result = products_collection.delete_one(query)
        
        if result.deleted_count > 0:
            return jsonify({
                'message': 'Product deleted successfully',
                'deleted_product': convert_objectid_to_str(product_to_delete)
            }), 200
        else:
            return jsonify({'error': 'Failed to delete product'}), 500
    
    except Exception as e:
        print(f"Error in delete_product: {e}")
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
    print("\n" + "="*60)
    print("🚀 Products API Starting...")
    print("="*60)
    
    if products_collection is not None:
        try:
            # Get initial products count from database
            total_products = products_collection.count_documents({})
            print(f"📊 Total products in database: {total_products}")
            
            # Display first few products if any exist
            if total_products > 0:
                print("\n📋 Sample products from database:")
                print("-" * 50)
                sample_products = list(products_collection.find().limit(3))
                for product in sample_products:
                    product = convert_objectid_to_str(product)
                    print(f"ID: {product['id']}")
                    print(f"Name: {product['name']}")
                    print(f"Price: ${product['price']:.2f}")
                    print(f"Quantity: {product['quantity']}")
                    print("-" * 30)
                if total_products > 3:
                    print(f"... and {total_products - 3} more products")
            else:
                print("📝 Database is empty - ready to add new products!")
                
        except Exception as e:
            print(f"⚠️  Could not retrieve database statistics: {e}")
    else:
        print("⚠️  Database connection not available")
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
