import unittest
import json
from beer_seller_api import app as reseller_app
from order_service import app as order_app
from beer_seller_mock_api import app as beer_seller_app
from unittest import mock

class ResellerApiTests(unittest.TestCase):

    def setUp(self):
        self.app = reseller_app.test_client()
        self.app.testing = True

    def test_register_valid_reseller(self):
        payload = {
            "cnpj": "12345678901234",
            "business_name": "Test Business",
            "trade_name": "Test Trade",
            "email": "test@example.com",
            "phone": ["1112345678"],
            "contact_name": ["John Doe"],
            "delivery_address": ["Test Address"]
        }
        response = self.app.post('/resellers', json=payload)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.get_data(as_text=True))
        self.assertIn('reseller_id', data)

    def test_register_invalid_reseller_missing_cnpj(self):
        payload = {
            "business_name": "Test Business",
            "trade_name": "Test Trade",
            "email": "test@example.com",
            "phone": ["1112345678"],
            "contact_name": ["John Doe"],
            "delivery_address": ["Test Address"]
        }
        response = self.app.post('/resellers', json=payload)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.get_data(as_text=True))
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'CNPJ is required and must be valid')

class OrderServiceTests(unittest.TestCase):

    def setUp(self):
        self.order_app = order_app.test_client()
        self.order_app.testing = True
        self.beer_seller_app = beer_seller_app.test_client()
        self.beer_seller_app.testing = True

        order_app.config['resellers_data'] = {
            1: {'cnpj': '12345678901234'}
        }
        order_app.resellers_data = order_app.config['resellers_data']


    def test_receive_valid_customer_order(self):
        payload = {
            "customer_identification": "customer123",
            "products": [
                {"product_id": "PROD001", "quantity": 2},
                {"product_id": "PROD002", "quantity": 1}
            ]
        }
        response = self.order_app.post('/resellers/1/orders', json=payload)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.get_data(as_text=True))
        self.assertIn('order_id', data)
        self.assertEqual(data['items_requested'], payload['products'])

    def test_place_beer_seller_order_below_minimum(self):
        payload = {
            "order_items": [
                {"product_id": "ABC001", "quantity": 500},
                {"product_id": "ABC002", "quantity": 499}
            ]
        }
        response = self.order_app.post('/resellers/1/place_beer_seller_order', json=payload)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.get_data(as_text=True))
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Minimum order quantity of 1000 units not met')

    def test_place_beer_seller_order_success(self):
        payload = {
            "order_items": [
                {"product_id": "AMB001", "quantity": 600},
                {"product_id": "AMB002", "quantity": 400}
            ]
        }
        with self.beer_seller_app.patch('/beer_seller/orders', return_value=mock.MagicMock(status_code=201, json=lambda: {"order_number": "BS123", "items_accepted": payload['order_items']})):
            response = self.order_app.post('/resellers/1/place_beer_seller_order', json=payload)
            self.assertEqual(response.status_code, 201)
            data = json.loads(response.get_data(as_text=True))
            self.assertIn('order_number', data)
            self.assertEqual(data['items_accepted'], payload['order_items'])

class BeerSellerApiTests(unittest.TestCase):

    def setUp(self):
        self.app = beer_seller_app.test_client()
        self.app.testing = True

    def test_receive_valid_beer_seller_order(self):
        payload = {
            "reseller_cnpj": "12345678901234",
            "items": [
                {"product_code": "AMB001", "amount": 100}
            ]
        }
        response = self.app.post('/beer_seller/orders', json=payload)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.get_data(as_text=True))
        self.assertIn('order_number', data)
        self.assertEqual(data['items_accepted'], payload['items'])

    def test_receive_invalid_beer_seller_order_missing_cnpj(self):
        payload = {
            "items": [
                {"product_code": "AMB001", "amount": 100}
            ]
        }
        response = self.app.post('/beer_seller/orders', json=payload)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.get_data(as_text=True))
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Reseller CNPJ is required')

if __name__ == '__main__':
    unittest.main()