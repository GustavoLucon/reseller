Requirements

Phyton

To Run This:

Save these three code blocks as reseller_api.py, order_service.py, and beer_seller_mock_api.py in the same directory.
Open three separate terminal windows or tabs.
In the first terminal, navigate to the directory and run: python beer_seller_api.py
In the second terminal, navigate to the directory and run: python order_service.py
In the third terminal, navigate to the directory and run: python beer_seller_mock_api.py

Example of usage

Register a Reseller:

Bash

curl -X POST -H "Content-Type: application/json" -d '{
    "cnpj": "12345678901234",
    "business_name": "Distribuidora Bebidas LTDA",
    "trade_name": "Bebidas Geladas",
    "email": "contato@bebidasgeladas.com.br",
    "phone": ["1199999999", "1188888888"],
    "contact_name": ["João Silva (Principal)", "Maria Souza"],
    "delivery_address": ["Rua das Flores, 123", "Avenida Principal, 456"]
}' http://localhost:5000/resellers
Receive a Customer Order (for reseller with ID 1):

Bash

curl -X POST -H "Content-Type: application/json" -d '{
    "customer_identification": "cliente789",
    "products": [
        {"product_id": "SKU001", "quantity": 5},
        {"product_id": "SKU002", "quantity": 10}
    ]
}' http://localhost:5002/resellers/1/orders
Place an Order with Beer Seller (as reseller with ID 1):

Bash

curl -X POST -H "Content-Type: application/json" -d '{
    "order_items": [
        {"product_id": "ABC001", "quantity": 600},
        {"product_id": "ABC002", "quantity": 450}
    ]
}' http://localhost:5002/resellers/1/place_beer_seller_order

To Run the Tests:

Save this code as tests.py in the same directory as your other Python files.
Open a terminal in that directory.
Run the command: python -m unittest tests.py