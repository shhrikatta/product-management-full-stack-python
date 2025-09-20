import random

# Products list with 10 random fruits
products = [
    {
        "id": 1,
        "name": "Apple",
        "price": 2.50,
        "quantity": random.randint(10, 100)
    },
    {
        "id": 2,
        "name": "Banana",
        "price": 1.25,
        "quantity": random.randint(10, 100)
    },
    {
        "id": 3,
        "name": "Orange",
        "price": 3.00,
        "quantity": random.randint(10, 100)
    },
    {
        "id": 4,
        "name": "Strawberry",
        "price": 4.75,
        "quantity": random.randint(10, 100)
    },
    {
        "id": 5,
        "name": "Mango",
        "price": 3.50,
        "quantity": random.randint(10, 100)
    },
    {
        "id": 6,
        "name": "Pineapple",
        "price": 5.00,
        "quantity": random.randint(10, 100)
    },
    {
        "id": 7,
        "name": "Grapes",
        "price": 4.25,
        "quantity": random.randint(10, 100)
    },
    {
        "id": 8,
        "name": "Watermelon",
        "price": 6.50,
        "quantity": random.randint(10, 100)
    },
    {
        "id": 9,
        "name": "Peach",
        "price": 3.25,
        "quantity": random.randint(10, 100)
    },
    {
        "id": 10,
        "name": "Blueberry",
        "price": 5.50,
        "quantity": random.randint(10, 100)
    }
]

# Display the products
if __name__ == "__main__":
    print("Products List:")
    print("-" * 50)
    for product in products:
        print(f"ID: {product['id']}")
        print(f"Name: {product['name']}")
        print(f"Price: ${product['price']:.2f}")
        print(f"Quantity: {product['quantity']}")
        print("-" * 30)
    
    print(f"\nTotal products: {len(products)}")