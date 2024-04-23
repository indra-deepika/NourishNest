# application/frontend/api/ProductClient.py
import requests


class ProductClient:

    @staticmethod
    def get_products():
        r = requests.get('http://cproduct-service:5002/api/products')
        products = r.json()
        return products

    @staticmethod
    def get_product(slug):
        response = requests.request(method="GET", url='http://cproduct-service:5002/api/product/' + slug)
        product = response.json()
        return product
    
    @staticmethod
    def get_product_by_id(product_id):
        response = requests.request(method="GET", url='http://cproduct-service:5002/api/product/' + str(product_id))
        product = response.json()
        return product
    
    
