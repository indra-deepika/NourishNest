# application/frontend/views.py
import requests
from . import forms
from . import frontend_blueprint
from .. import login_manager
from .api.UserClient import UserClient
from .api.ProductClient import ProductClient
from .api.OrderClient import OrderClient
from flask import render_template, session, redirect, url_for, flash, request

from flask_login import current_user

import logging
log = logging.getLogger(__name__)

import sys



@login_manager.user_loader
def load_user(user_id):
    return None


@frontend_blueprint.route('/', methods=['GET'])
def home():
    if current_user.is_authenticated:
        session['order'] = OrderClient.get_order_from_session()

    try:
        products = ProductClient.get_products()
    except requests.exceptions.ConnectionError:
        products = {
            'results': []
        }

    return render_template('home/index.html', products=products)


@frontend_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.RegistrationForm(request.form)
    if request.method == "POST":
        if form.validate_on_submit():
            username = form.username.data

            # Search for existing user
            user = UserClient.does_exist(username)
            if user:
                # Existing user found
                flash('Please try another username', 'error')
                return render_template('register/index.html', form=form)
            else:
                # Attempt to create new user
                user = UserClient.post_user_create(form)
                if user:
                    flash('Thanks for registering, please login', 'success')
                    return redirect(url_for('frontend.login'))

        else:
            flash('Errors found', 'error')

    return render_template('register/index.html', form=form)


@frontend_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('frontend.home'))
    form = forms.LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            api_key = UserClient.post_login(form)
            if api_key:
                session['user_api_key'] = api_key
                user = UserClient.get_user()
                session['user'] = user['result']

                order = OrderClient.get_order()
                if order.get('result', False):
                    session['order'] = order['result']

                flash('Welcome back, ' + user['result']['username'], 'success')
                return redirect(url_for('frontend.home'))
            else:
                flash('Cannot login', 'error')
        else:
            flash('Errors found', 'error')
    return render_template('login/index.html', form=form)


@frontend_blueprint.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('frontend.home'))


@frontend_blueprint.route('/product/<slug>', methods=['GET', 'POST'])
def product(slug):
    response = ProductClient.get_product(slug)
    item = response['result']

    form = forms.ItemForm2(product_id=item['id'], price=item['price'])

    if request.method == "POST":
        if 'user' not in session:
            flash('Please login', 'error')
            return redirect(url_for('frontend.login'))
        order = OrderClient.post_add_to_cart(product_id=item['id'], qty=1)
        session['order'] = order['result']
        flash('Order has been updated', 'success')
    return render_template('product/index.html', product=item, form=form)

# @frontend_blueprint.route('/product/<id>', methods=['GET'])
# def product_by_id(id):
#     response = ProductClient.get_product_by_id(id)
#     item = response['result']

#     print(item, file=sys.stderr)

#     form = forms.ItemForm2(product_id=item['id'], price=item['price'])

#     if request.method == "POST":
#         if 'user' not in session:
#             flash('Please login', 'error')
#             return redirect(url_for('frontend.login'))
#         order = OrderClient.post_add_to_cart(product_id=item['id'], qty=1)
#         session['order'] = order['result']
#         flash('Order has been updated', 'success')
#     return render_template('product/index.html', product=item, form=form)

@frontend_blueprint.route('/checkout', methods=['GET'])
def summary():
    if 'user' not in session:
        flash('Please login', 'error')
        return redirect(url_for('frontend.login'))

    if 'order' not in session:
        flash('No order found', 'error')
        return redirect(url_for('frontend.home'))
    order = OrderClient.get_order()

    print(order, file=sys.stderr)
    if len(order['result']['items']) == 0:
        flash('No order found', 'error')
        return redirect(url_for('frontend.home'))

    # response = OrderClient.post_checkout()
    
    # print(response, file=sys.stderr)
    # return redirect(url_for('frontend.thank_you'))
    # go to cart page
    return redirect(url_for('frontend.cart'))

@frontend_blueprint.route('/order/thank-you', methods=['GET'])
def thank_you():
    if 'user' not in session:
        flash('Please login', 'error')
        return redirect(url_for('frontend.login'))

    if 'order' not in session:
        flash('No order found', 'error')
        return redirect(url_for('frontend.home'))

    session.pop('order', None)
    flash('Thank you for your order', 'success')

    return render_template('order/thankyou.html')


@frontend_blueprint.route('/order/cart', methods=['GET', 'POST' ])
def cart():
    # if 'user' not in session:
    #     flash('Please login', 'error')
    #     return redirect(url_for('frontend.login'))
    
    # order = OrderClient.get_order()
    # if not order or 'items' not in order.get('result', {}):
    #     flash('No items in the cart.', 'error')
    #     return redirect(url_for('frontend.home'))

    # # Extract cart items and total
    # cart = order['result']['items']
    # total = sum(item['price'] * item['quantity'] for item in cart)

    # form = forms.CheckoutForm()  # Ensure this form exists and is properly defined
    order = OrderClient.get_order()
    print(order, file=sys.stderr)
    
    if 'user' not in session:
        flash('Please login', 'error')
        return redirect(url_for('frontend.login'))
    if 'order' not in session:
        flash('No order found', 'error')
        return redirect(url_for('frontend.home'))
    
    if len(order['result']['items']) == 0:
        flash('No order found', 'error')
        return redirect(url_for('frontend.home'))


       # Handle POST requests to update the cart
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        action = request.form.get('action')

        # Increase or decrease the quantity
        if action == 'increase_quantity':
            response = OrderClient.add_item(product_id,  1)
            if not response:
                flash('Failed to increase quantity.', 'error')

        elif action == 'decrease_quantity':
            response = OrderClient.remove_item(product_id, 1)
            if not response:
                flash('Failed to decrease quantity.', 'error')

        elif action == 'confirm_order':
            response = OrderClient.post_checkout()
            if not response:
                flash('Failed to checkout.', 'error')
            return redirect(url_for('frontend.thank_you'))

    # Refresh the order to get the updated cart
    order_response = OrderClient.get_order()

    if not order_response or 'result' not in order_response:
        flash('Error updating the cart.', 'error')
        return redirect(url_for('frontend.home'))

    
    order_items = order_response.get('result', {}).get('items', [])
    
    for item in order_items:
        product = ProductClient.get_product("prod"+str(item['product']))

        print(product, file=sys.stderr)
        item['price'] = product['result']['price']
        item['name'] = product['result']['name']

    print(order_items, file=sys.stderr)

    total_amount = sum(item['price'] * item['quantity'] for item in order_items)

    
    
    # # for loop on order_items and add price based on product id
    # for item in order_items:
    #     product = ProductClient.get_product_by_id(item['product'])
    #     print(product, file=sys.stderr)
    #     item['price'] = product['price']

    return render_template('order/cart.html', order_items=order_items , total_amount=total_amount)
    # return render_template('order/cart.html')