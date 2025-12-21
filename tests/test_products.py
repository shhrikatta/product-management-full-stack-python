import pytest
from unittest.mock import MagicMock, patch
from bson.objectid import ObjectId
from bson.errors import InvalidId
import products
from products import app, convert_objectid_to_str, convert_objectid_list_to_str, check_db_connection


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_collection():
    """Create a mock MongoDB collection"""
    return MagicMock()


@pytest.fixture
def sample_product():
    """Sample product data"""
    return {
        '_id': ObjectId('507f1f77bcf86cd799439011'),
        'id': 1,
        'name': 'Apple',
        'price': 2.50,
        'quantity': 10
    }


@pytest.fixture
def sample_products():
    """Sample list of products"""
    return [
        {
            '_id': ObjectId('507f1f77bcf86cd799439011'),
            'id': 1,
            'name': 'Apple',
            'price': 2.50,
            'quantity': 10
        },
        {
            '_id': ObjectId('507f1f77bcf86cd799439012'),
            'id': 2,
            'name': 'Banana',
            'price': 1.50,
            'quantity': 20
        }
    ]


# ============= Helper Functions Tests =============

@pytest.mark.unit
def test_convert_objectid_to_str_with_valid_document(sample_product):
    """Test converting ObjectId to string in a document"""
    result = convert_objectid_to_str(sample_product.copy())
    assert 'id' in result
    assert '_id' not in result
    assert result['id'] == '507f1f77bcf86cd799439011'
    assert result['name'] == 'Apple'


@pytest.mark.unit
def test_convert_objectid_to_str_without_id():
    """Test converting document without _id field"""
    doc = {'name': 'Test', 'price': 5.0}
    result = convert_objectid_to_str(doc)
    assert result == doc


@pytest.mark.unit
def test_convert_objectid_to_str_with_none():
    """Test converting None document"""
    result = convert_objectid_to_str(None)
    assert result is None


@pytest.mark.unit
def test_convert_objectid_list_to_str(sample_products):
    """Test converting list of documents"""
    result = convert_objectid_list_to_str(sample_products.copy())
    assert len(result) == 2
    assert all('_id' not in doc for doc in result)
    assert all('id' in doc for doc in result)
    assert result[0]['id'] == '507f1f77bcf86cd799439011'


@pytest.mark.unit
def test_convert_objectid_list_to_str_empty_list():
    """Test converting empty list"""
    result = convert_objectid_list_to_str([])
    assert result == []


@pytest.mark.unit
def test_check_db_connection_success():
    """Test database connection check when connected"""
    with patch('products.products_collection', MagicMock()):
        connected, error, code = check_db_connection()
        assert connected is True
        assert error is None
        assert code is None


@pytest.mark.unit
def test_check_db_connection_failure():
    """Test database connection check when disconnected"""
    with patch('products.products_collection', None):
        connected, error, code = check_db_connection()
        assert connected is False
        assert error == {'error': 'Database connection not available'}
        assert code == 500


# ============= GET /api/products Tests =============

@pytest.mark.integration
def test_get_all_products_success(client, sample_products, mock_collection):
    """Test getting all products successfully"""
    mock_collection.find.return_value = sample_products.copy()
    
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            response = client.get('/api/products')
            
            assert response.status_code == 200
            data = response.get_json()
            assert len(data) == 2
            assert data[0]['name'] == 'Apple'
            assert data[1]['name'] == 'Banana'


@pytest.mark.integration
def test_get_all_products_db_disconnected(client):
    """Test getting products when database is disconnected"""
    with patch('products.check_db_connection', return_value=(False, {'error': 'Database connection not available'}, 500)):
        response = client.get('/api/products')
        
        assert response.status_code == 500
        data = response.get_json()
        assert data['error'] == 'Database connection not available'


@pytest.mark.integration
def test_get_product_by_valid_objectid(client, sample_product, mock_collection):
    """Test getting product by valid ObjectId"""
    mock_collection.find_one.return_value = sample_product.copy()
    
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            response = client.get('/api/products?id=507f1f77bcf86cd799439011')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['name'] == 'Apple'
            assert data['id'] == '507f1f77bcf86cd799439011'


@pytest.mark.integration
def test_get_product_by_integer_id(client, sample_product, mock_collection):
    """Test getting product by integer ID"""
    mock_collection.find_one.return_value = sample_product.copy()
    
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            response = client.get('/api/products?id=1')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['name'] == 'Apple'


@pytest.mark.integration
def test_get_product_not_found(client, mock_collection):
    """Test getting non-existent product"""
    mock_collection.find_one.return_value = None
    
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            response = client.get('/api/products?id=999')
            
            assert response.status_code == 404
            data = response.get_json()
            assert data['error'] == 'Product not found'


@pytest.mark.integration
def test_get_product_invalid_id_format(client, mock_collection):
    """Test getting product with invalid ID format"""
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            response = client.get('/api/products?id=invalid')
            
            assert response.status_code == 400
            data = response.get_json()
            assert data['error'] == 'Invalid product ID format'


@pytest.mark.integration
def test_get_all_products_exception(client, mock_collection):
    """Test getting products when an exception occurs"""
    mock_collection.find.side_effect = Exception("Database error")
    
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            response = client.get('/api/products')
            
            assert response.status_code == 500
            data = response.get_json()
            assert data['error'] == 'Internal server error'


# ============= POST /api/products Tests =============

@pytest.mark.integration
def test_create_product_success(client, mock_collection):
    """Test creating a product successfully"""
    mock_collection.find_one.side_effect = [
        {'id': 5},  # max_id_doc
        {'_id': ObjectId(), 'id': 6, 'name': 'Orange', 'price': 3.0, 'quantity': 15}  # created product
    ]
    mock_collection.insert_one.return_value = MagicMock(inserted_id=ObjectId())
    
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            response = client.post('/api/products', json={
                'name': 'Orange',
                'price': 3.0,
                'quantity': 15
            })
            
            assert response.status_code == 201
            data = response.get_json()
            assert data['name'] == 'Orange'
            assert data['price'] == 3.0


@pytest.mark.integration
def test_create_product_first_product(client, mock_collection):
    """Test creating the first product (ID should be 1)"""
    mock_collection.find_one.side_effect = [
        None,  # max_id_doc (no existing products)
        {'_id': ObjectId(), 'id': 1, 'name': 'Apple', 'price': 2.5, 'quantity': 10}  # created product
    ]
    mock_collection.insert_one.return_value = MagicMock(inserted_id=ObjectId())
    
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            response = client.post('/api/products', json={
                'name': 'Apple',
                'price': 2.5,
                'quantity': 10
            })
            
            assert response.status_code == 201


@pytest.mark.integration
def test_create_product_no_json_data(client, mock_collection):
    """Test creating product without JSON data"""
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            with patch('flask.Request.get_json', return_value=None):
                response = client.post('/api/products')
                
                assert response.status_code == 400
                data = response.get_json()
                assert data['error'] == 'No JSON data provided'


@pytest.mark.integration
def test_create_product_missing_required_fields(client):
    """Test creating product with missing required fields"""
    with patch('products.check_db_connection', return_value=(True, None, None)):
        response = client.post('/api/products', json={
            'name': 'Apple'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Missing required field' in data['error']


@pytest.mark.integration
def test_create_product_invalid_price_type(client):
    """Test creating product with invalid price type"""
    with patch('products.check_db_connection', return_value=(True, None, None)):
        response = client.post('/api/products', json={
            'name': 'Apple',
            'price': 'invalid',
            'quantity': 10
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Invalid data types' in data['error']


@pytest.mark.integration
def test_create_product_invalid_quantity_type(client):
    """Test creating product with invalid quantity type"""
    with patch('products.check_db_connection', return_value=(True, None, None)):
        response = client.post('/api/products', json={
            'name': 'Apple',
            'price': 2.5,
            'quantity': 'invalid'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Invalid data types' in data['error']


@pytest.mark.integration
def test_create_product_empty_name(client):
    """Test creating product with empty name"""
    with patch('products.check_db_connection', return_value=(True, None, None)):
        response = client.post('/api/products', json={
            'name': '   ',
            'price': 2.5,
            'quantity': 10
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['error'] == 'Product name cannot be empty'


@pytest.mark.integration
def test_create_product_negative_price(client):
    """Test creating product with negative price"""
    with patch('products.check_db_connection', return_value=(True, None, None)):
        response = client.post('/api/products', json={
            'name': 'Apple',
            'price': -2.5,
            'quantity': 10
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['error'] == 'Price cannot be negative'


@pytest.mark.integration
def test_create_product_negative_quantity(client):
    """Test creating product with negative quantity"""
    with patch('products.check_db_connection', return_value=(True, None, None)):
        response = client.post('/api/products', json={
            'name': 'Apple',
            'price': 2.5,
            'quantity': -10
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['error'] == 'Quantity cannot be negative'


@pytest.mark.integration
def test_create_product_db_disconnected(client):
    """Test creating product when database is disconnected"""
    with patch('products.check_db_connection', return_value=(False, {'error': 'Database connection not available'}, 500)):
        response = client.post('/api/products', json={
            'name': 'Apple',
            'price': 2.5,
            'quantity': 10
        })
        
        assert response.status_code == 500
        data = response.get_json()
        assert data['error'] == 'Database connection not available'


@pytest.mark.integration
def test_create_product_insert_failed(client, mock_collection):
    """Test creating product when insert fails"""
    mock_collection.find_one.return_value = {'id': 5}
    mock_collection.insert_one.return_value = MagicMock(inserted_id=None)
    
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            response = client.post('/api/products', json={
                'name': 'Apple',
                'price': 2.5,
                'quantity': 10
            })
            
            assert response.status_code == 500
            data = response.get_json()
            assert data['error'] == 'Failed to create product'


@pytest.mark.integration
def test_create_product_exception(client, mock_collection):
    """Test creating product when an exception occurs"""
    mock_collection.find_one.side_effect = Exception("Database error")
    
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            response = client.post('/api/products', json={
                'name': 'Apple',
                'price': 2.5,
                'quantity': 10
            })
            
            assert response.status_code == 500
            data = response.get_json()
            assert data['error'] == 'Internal server error'


# ============= PUT /api/products/<id> Tests =============

@pytest.mark.integration
def test_update_product_success(client, sample_product, mock_collection):
    """Test updating a product successfully"""
    mock_collection.find_one.side_effect = [
        sample_product.copy(),  # existing product
        {**sample_product, 'price': 3.0}  # updated product
    ]
    mock_collection.update_one.return_value = MagicMock(modified_count=1, matched_count=1)
    
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            response = client.put('/api/products/1', json={
                'price': 3.0
            })
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['price'] == 3.0


@pytest.mark.integration
def test_update_product_by_objectid(client, sample_product, mock_collection):
    """Test updating product by ObjectId"""
    mock_collection.find_one.side_effect = [
        sample_product.copy(),
        {**sample_product, 'name': 'Green Apple'}
    ]
    mock_collection.update_one.return_value = MagicMock(modified_count=1, matched_count=1)
    
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            response = client.put('/api/products/507f1f77bcf86cd799439011', json={
                'name': 'Green Apple'
            })
            
            assert response.status_code == 200


@pytest.mark.integration
def test_update_product_no_json_data(client, mock_collection):
    """Test updating product without JSON data"""
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            with patch('flask.Request.get_json', return_value=None):
                response = client.put('/api/products/1')
                
                assert response.status_code == 400
                data = response.get_json()
                assert data['error'] == 'No JSON data provided'


@pytest.mark.integration
def test_update_product_invalid_id_format(client):
    """Test updating product with invalid ID format"""
    with patch('products.check_db_connection', return_value=(True, None, None)):
        response = client.put('/api/products/invalid', json={
            'price': 3.0
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['error'] == 'Invalid product ID format'


@pytest.mark.integration
def test_update_product_not_found(client, mock_collection):
    """Test updating non-existent product"""
    mock_collection.find_one.return_value = None
    
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            response = client.put('/api/products/999', json={
                'price': 3.0
            })
            
            assert response.status_code == 404
            data = response.get_json()
            assert data['error'] == 'Product not found'


@pytest.mark.integration
def test_update_product_empty_name(client, sample_product, mock_collection):
    """Test updating product with empty name"""
    mock_collection.find_one.return_value = sample_product.copy()
    
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            response = client.put('/api/products/1', json={
                'name': '   '
            })
            
            assert response.status_code == 400
            data = response.get_json()
            assert data['error'] == 'Product name cannot be empty'


@pytest.mark.integration
def test_update_product_negative_price(client, sample_product, mock_collection):
    """Test updating product with negative price"""
    mock_collection.find_one.return_value = sample_product.copy()
    
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            response = client.put('/api/products/1', json={
                'price': -3.0
            })
            
            assert response.status_code == 400
            data = response.get_json()
            assert data['error'] == 'Price cannot be negative'


@pytest.mark.integration
def test_update_product_invalid_price_type(client, sample_product, mock_collection):
    """Test updating product with invalid price type"""
    mock_collection.find_one.return_value = sample_product.copy()
    
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            response = client.put('/api/products/1', json={
                'price': 'invalid'
            })
            
            assert response.status_code == 400
            data = response.get_json()
            assert data['error'] == 'Price must be a valid number'


@pytest.mark.integration
def test_update_product_negative_quantity(client, sample_product, mock_collection):
    """Test updating product with negative quantity"""
    mock_collection.find_one.return_value = sample_product.copy()
    
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            response = client.put('/api/products/1', json={
                'quantity': -10
            })
            
            assert response.status_code == 400
            data = response.get_json()
            assert data['error'] == 'Quantity cannot be negative'


@pytest.mark.integration
def test_update_product_invalid_quantity_type(client, sample_product, mock_collection):
    """Test updating product with invalid quantity type"""
    mock_collection.find_one.return_value = sample_product.copy()
    
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            response = client.put('/api/products/1', json={
                'quantity': 'invalid'
            })
            
            assert response.status_code == 400
            data = response.get_json()
            assert data['error'] == 'Quantity must be a valid integer'


@pytest.mark.integration
def test_update_product_no_valid_fields(client, sample_product, mock_collection):
    """Test updating product with no valid fields"""
    mock_collection.find_one.return_value = sample_product.copy()
    
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            response = client.put('/api/products/1', json={
                'invalid_field': 'value'
            })
            
            assert response.status_code == 400
            data = response.get_json()
            assert data['error'] == 'No valid fields to update'


@pytest.mark.integration
def test_update_product_matched_not_modified(client, sample_product, mock_collection):
    """Test updating product when matched but not modified"""
    mock_collection.find_one.side_effect = [
        sample_product.copy(),
        sample_product.copy()
    ]
    mock_collection.update_one.return_value = MagicMock(modified_count=0, matched_count=1)
    
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            response = client.put('/api/products/1', json={
                'price': 2.50  # Same as existing
            })
            
            assert response.status_code == 200


@pytest.mark.integration
def test_update_product_db_disconnected(client):
    """Test updating product when database is disconnected"""
    with patch('products.check_db_connection', return_value=(False, {'error': 'Database connection not available'}, 500)):
        response = client.put('/api/products/1', json={
            'price': 3.0
        })
        
        assert response.status_code == 500
        data = response.get_json()
        assert data['error'] == 'Database connection not available'


@pytest.mark.integration
def test_update_product_exception(client, sample_product, mock_collection):
    """Test updating product when an exception occurs"""
    mock_collection.find_one.side_effect = Exception("Database error")
    
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            response = client.put('/api/products/1', json={
                'price': 3.0
            })
            
            assert response.status_code == 500
            data = response.get_json()
            assert data['error'] == 'Internal server error'


# ============= DELETE /api/products/<id> Tests =============

@pytest.mark.integration
def test_delete_product_success(client, sample_product, mock_collection):
    """Test deleting a product successfully"""
    mock_collection.find_one.return_value = sample_product.copy()
    mock_collection.delete_one.return_value = MagicMock(deleted_count=1)
    
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            response = client.delete('/api/products/1')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['message'] == 'Product deleted successfully'
            assert data['deleted_product']['name'] == 'Apple'


@pytest.mark.integration
def test_delete_product_by_objectid(client, sample_product, mock_collection):
    """Test deleting product by ObjectId"""
    mock_collection.find_one.return_value = sample_product.copy()
    mock_collection.delete_one.return_value = MagicMock(deleted_count=1)
    
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            response = client.delete('/api/products/507f1f77bcf86cd799439011')
            
            assert response.status_code == 200


@pytest.mark.integration
def test_delete_product_invalid_id_format(client):
    """Test deleting product with invalid ID format"""
    with patch('products.check_db_connection', return_value=(True, None, None)):
        response = client.delete('/api/products/invalid')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['error'] == 'Invalid product ID format'


@pytest.mark.integration
def test_delete_product_not_found(client, mock_collection):
    """Test deleting non-existent product"""
    mock_collection.find_one.return_value = None
    
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            response = client.delete('/api/products/999')
            
            assert response.status_code == 404
            data = response.get_json()
            assert data['error'] == 'Product not found'


@pytest.mark.integration
def test_delete_product_failed(client, sample_product, mock_collection):
    """Test deleting product when delete operation fails"""
    mock_collection.find_one.return_value = sample_product.copy()
    mock_collection.delete_one.return_value = MagicMock(deleted_count=0)
    
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            response = client.delete('/api/products/1')
            
            assert response.status_code == 500
            data = response.get_json()
            assert data['error'] == 'Failed to delete product'


@pytest.mark.integration
def test_delete_product_db_disconnected(client):
    """Test deleting product when database is disconnected"""
    with patch('products.check_db_connection', return_value=(False, {'error': 'Database connection not available'}, 500)):
        response = client.delete('/api/products/1')
        
        assert response.status_code == 500
        data = response.get_json()
        assert data['error'] == 'Database connection not available'


@pytest.mark.integration
def test_delete_product_exception(client, mock_collection):
    """Test deleting product when an exception occurs"""
    mock_collection.find_one.side_effect = Exception("Database error")
    
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            response = client.delete('/api/products/1')
            
            assert response.status_code == 500
            data = response.get_json()
            assert data['error'] == 'Internal server error'


# ============= Web UI and Health Check Tests =============

@pytest.mark.integration
def test_index_route(client):
    """Test the index route returns HTML"""
    with patch('products.render_template', return_value='<html></html>'):
        response = client.get('/')
        assert response.status_code == 200


@pytest.mark.integration
def test_health_check_connected(client):
    """Test health check when database is connected"""
    with patch('products.products_collection', MagicMock()):
        response = client.get('/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert data['database'] == 'connected'
        assert 'endpoints' in data


@pytest.mark.integration
def test_health_check_disconnected(client):
    """Test health check when database is disconnected"""
    with patch('products.products_collection', None):
        response = client.get('/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert data['database'] == 'disconnected'


# ============= Additional Edge Case Tests =============

@pytest.mark.integration
def test_get_product_with_invalidid_exception(client, mock_collection):
    """Test getting product when InvalidId exception is raised"""
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            with patch('products.ObjectId.is_valid', side_effect=InvalidId()):
                response = client.get('/api/products?id=test')
                
                assert response.status_code == 400
                data = response.get_json()
                assert data['error'] == 'Invalid product ID format'


@pytest.mark.integration
def test_update_product_with_invalidid_exception(client, mock_collection):
    """Test updating product when InvalidId exception is raised"""
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            with patch('products.ObjectId.is_valid', side_effect=InvalidId()):
                response = client.put('/api/products/test', json={'price': 3.0})
                
                assert response.status_code == 400
                data = response.get_json()
                assert data['error'] == 'Invalid product ID format'


@pytest.mark.integration
def test_delete_product_with_invalidid_exception(client, mock_collection):
    """Test deleting product when InvalidId exception is raised"""
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            with patch('products.ObjectId.is_valid', side_effect=InvalidId()):
                response = client.delete('/api/products/test')
                
                assert response.status_code == 400
                data = response.get_json()
                assert data['error'] == 'Invalid product ID format'


@pytest.mark.unit
def test_convert_objectid_to_str_preserves_original():
    """Test that convert_objectid_to_str modifies the document in place"""
    doc = {
        '_id': ObjectId('507f1f77bcf86cd799439011'),
        'name': 'Test',
        'value': 123
    }
    result = convert_objectid_to_str(doc)
    assert result is doc  # Should be same object
    assert 'value' in result
    assert result['value'] == 123


@pytest.mark.integration
def test_update_product_update_failed(client, sample_product, mock_collection):
    """Test updating product when update operation fails"""
    mock_collection.find_one.return_value = sample_product.copy()
    mock_collection.update_one.return_value = MagicMock(modified_count=0, matched_count=0)
    
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            response = client.put('/api/products/1', json={
                'price': 3.0
            })
            
            assert response.status_code == 500
            data = response.get_json()
            assert data['error'] == 'Failed to update product'


@pytest.mark.integration  
def test_create_product_max_id_without_id_field(client, mock_collection):
    """Test creating product when max document doesn't have id field"""
    mock_collection.find_one.side_effect = [
        {'_id': ObjectId()},  # max_id_doc without 'id' field
        {'_id': ObjectId(), 'id': 1, 'name': 'Apple', 'price': 2.5, 'quantity': 10}  # created product
    ]
    mock_collection.insert_one.return_value = MagicMock(inserted_id=ObjectId())
    
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            response = client.post('/api/products', json={
                'name': 'Apple',
                'price': 2.5,
                'quantity': 10
            })
            
            assert response.status_code == 201


@pytest.mark.integration
def test_update_product_all_fields(client, sample_product, mock_collection):
    """Test updating all fields of a product at once"""
    updated_product = {
        '_id': sample_product['_id'],
        'id': 1,
        'name': 'Green Apple',
        'price': 3.5,
        'quantity': 25
    }
    mock_collection.find_one.side_effect = [
        sample_product.copy(),  # existing product
        updated_product  # updated product
    ]
    mock_collection.update_one.return_value = MagicMock(modified_count=1, matched_count=1)
    
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            response = client.put('/api/products/1', json={
                'name': 'Green Apple',
                'price': 3.5,
                'quantity': 25
            })
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['name'] == 'Green Apple'
            assert data['price'] == 3.5
            assert data['quantity'] == 25


@pytest.mark.integration
def test_create_product_with_zero_values(client, mock_collection):
    """Test creating product with zero price and quantity"""
    mock_collection.find_one.side_effect = [
        {'id': 5},  # max_id_doc
        {'_id': ObjectId(), 'id': 6, 'name': 'Free Item', 'price': 0.0, 'quantity': 0}  # created product
    ]
    mock_collection.insert_one.return_value = MagicMock(inserted_id=ObjectId())
    
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            response = client.post('/api/products', json={
                'name': 'Free Item',
                'price': 0.0,
                'quantity': 0
            })
            
            assert response.status_code == 201
            data = response.get_json()
            assert data['price'] == 0.0
            assert data['quantity'] == 0


@pytest.mark.integration
def test_update_product_with_zero_quantity(client, sample_product, mock_collection):
    """Test updating product with zero quantity"""
    updated_product = {**sample_product, 'quantity': 0}
    mock_collection.find_one.side_effect = [
        sample_product.copy(),
        updated_product
    ]
    mock_collection.update_one.return_value = MagicMock(modified_count=1, matched_count=1)
    
    with patch('products.products_collection', mock_collection):
        with patch('products.check_db_connection', return_value=(True, None, None)):
            response = client.put('/api/products/1', json={
                'quantity': 0
            })
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['quantity'] == 0
