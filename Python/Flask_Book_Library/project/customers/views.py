from flask import render_template, Blueprint, request, redirect, url_for, jsonify, escape
from pydantic import ValidationError

from project import db
from project.customers.models import Customer
from project.common.form_models import validate_customer_model
from project.common.error_handlers import handle_validtion_error

# Blueprint for customers
customers = Blueprint('customers', __name__, template_folder='templates', url_prefix='/customers')

# Route to display customers in HTML
@customers.route('/', methods=['GET'])
def list_customers():
    # Fetch all customers from the database
    customers = Customer.query.all()
    print('Customers page accessed')
    return render_template('customers.html', customers=customers)


# Route to fetch customers in JSON format
@customers.route('/json', methods=['GET'])
def list_customers_json():
    # Fetch all customers from the database and convert to JSON
    customers = Customer.query.all()
    customer_list = [{'name': customer.name, 'city': customer.city, 'age': customer.age} for customer in customers]
    return jsonify(customers=customer_list)

# Route to create a new customer
@customers.route('/create', methods=['POST', 'GET'])
def create_customer():
    data = request.form

    try:
        valid_data = validate_customer_model(
            name = escape(data['name']),
            city = escape(data['city']),
            age = escape(data['age'])
        )
        customer = Customer(
            name= valid_data["name"],
            city=valid_data["city"],
            age=valid_data["age"],
        )

        # Add the new customer to the session and commit to save to the database
        db.session.add(customer)
        db.session.commit()
        print('Customer added succesfully')
        return redirect(url_for('customers.list_customers'))
    except ValidationError as e:
        return handle_validtion_error(e)
    except Exception as e:
        # Handle any exceptions, such as database errors
        db.session.rollback()
        print('Error creating customer')
        return jsonify({'error': f'Error creating customer: {str(e)}'}), 500


# Route to fetch customer data for editing
@customers.route('/<int:customer_id>/edit-data', methods=['GET'])
def edit_customer_data(customer_id):
    # Get the customer with the given ID
    customer = Customer.query.get(customer_id)

    if customer:
        # Convert customer data to a dictionary
        customer_data = {
            'name': customer.name,
            'city': customer.city,
            'age': customer.age
        }
        return jsonify({'success': True, 'customer': customer_data}), 200
    else:
        print('Customer not found')
        return jsonify({'error': 'Customer not found'}), 404


# Route to update an existing customer
@customers.route('/<int:customer_id>/edit', methods=['POST'])
def edit_customer(customer_id):
    # Get the customer with the given ID
    customer = Customer.query.get(customer_id)

    # Check if the customer exists
    if not customer:
        print('Customer not found')
        return jsonify({'error': 'Customer not found'}), 404

    try:
        # Get data from the request
        data = request.form
        valid_data = validate_customer_model(
            name=escape(data.get("name", customer.name)),
            city=escape(data.get("city", customer.city)),
            age=escape(data.get("age", customer.age))
        )

        # Update customer details
        customer.name = valid_data['name']
        customer.city = valid_data['city']
        customer.age = valid_data['age']

        # Commit the changes to the database
        db.session.commit()
        print('Customer updated succesfully')
        return redirect(url_for('customers.list_customers'))
    except ValidationError as e:
        return handle_validtion_error(e)
    except Exception as e:
        # Handle any exceptions
        db.session.rollback()
        print('Error updating customer')
        return jsonify({'error': f'Error updating customer: {str(e)}'}), 500


# Route to delete a customer
@customers.route('/<int:customer_id>/delete', methods=['POST'])
def delete_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if not customer:
        print('Customer not found')
        return jsonify({'error': 'Customer not found'}), 404

    try:
        # Delete the customer from the database
        db.session.delete(customer)
        db.session.commit()
        print('Customer deleted successfully')
        return redirect(url_for('customers.list_customers'))
    except Exception as e:
        # Handle any exceptions, such as database errors
        db.session.rollback()
        print('Error deleting customer')
        return jsonify({'error': f'Error deleting customer: {str(e)}'}), 500
