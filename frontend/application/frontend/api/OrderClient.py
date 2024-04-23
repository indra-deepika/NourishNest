# application/frontend/api/OrderClient.py
from flask import session
import requests
import sys


class OrderClient:
    @staticmethod
    def get_order():
        print("get order")
        headers = {
            'Authorization': 'Basic ' + session['user_api_key']
        }
        url = 'http://corder-service:5003/api/order'
        response = requests.request(method="GET", url=url, headers=headers)
        order = response.json()

        print(response.status_code)
        return order

    @staticmethod
    def post_add_to_cart(product_id, qty=1):
        payload = {
            'product_id': product_id,
            'qty': qty
        }
        url = 'http://corder-service:5003/api/order/add-item'

        headers = {
            'Authorization': 'Basic ' + session['user_api_key']
        }
        response = requests.request("POST", url=url, data=payload, headers=headers)
        if response:
            order = response.json()
            return order

    @staticmethod
    def post_checkout():
        url = 'http://corder-service:5003/api/order/checkout'

        headers = {
            'Authorization': 'Basic ' + session['user_api_key']
        }
        response = requests.request("POST", url=url, headers=headers)
        order = response.json()
        print(order, file=sys.stderr)
        return order


    @staticmethod
    def get_order_from_session():
        default_order = {
            'items': {},
            'total': 0,
        }
        return session.get('order', default_order)


    @staticmethod
    def update_item_quantity(product_id, new_qty):
        payload = {
            'product_id': product_id,
            'qty': new_qty
        }
        url = 'http://corder-service:5003/api/order/add-item'
        headers = {
            'Authorization': 'Basic ' + session.get('user_api_key', '')
        }
        response = requests.post(url, data=payload, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return {'message': 'Failed to update item quantity'}

    @staticmethod
    def add_item(product_id , qty):
        payload = {
            'product_id': product_id,
            'qty': qty
        }
        url = 'http://corder-service:5003/api/order/add-item'
        headers = {
            'Authorization': 'Basic ' + session.get('user_api_key', '')
        }
        response = requests.post(url, data=payload, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return {'message': 'Failed to add item'}
    @staticmethod
    def remove_item(product_id , qty):
        payload = {
            'product_id': product_id,
            'qty': qty
        }
        url = 'http://corder-service:5003/api/order/remove-item'
        headers = {
            'Authorization': 'Basic ' + session.get('user_api_key', '')
        }
        response = requests.post(url, data=payload, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return {'message': 'Failed to remove item'}