from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
import uuid
import json
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Setting secret key for flash messages

# I'm using in-memory storage for this demo - in production, we'd use a proper database
orders = {}
action_logs = []

class Order:
    """Order class to handle order data structure"""
    def __init__(self, order_id, num_items, delivery_date, sender_name, recipient_name, recipient_address):
        self.order_id = order_id
        self.num_items = num_items
        self.delivery_date = delivery_date
        self.sender_name = sender_name
        self.recipient_name = recipient_name
        self.recipient_address = recipient_address
        self.status = "Ongoing"  # Setting default status
        self.created_at = datetime.now()

    def to_dict(self):
        """Converting order object to dictionary for easier handling"""
        return {
            'order_id': self.order_id,
            'num_items': self.num_items,
            'delivery_date': self.delivery_date,
            'sender_name': self.sender_name,
            'recipient_name': self.recipient_name,
            'recipient_address': self.recipient_address,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

def log_action(action_type, performed_by, order_id=None, details=None):
    """I'm creating this function to log all actions happening in the system"""
    log_entry = {
        'action_type': action_type,
        'performed_by': performed_by,
        'order_id': order_id,
        'details': details,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    action_logs.append(log_entry)
    print(f"Action logged: {action_type} for order {order_id} by {performed_by}")  # Debug logging

@app.route('/')
def index():
    """Main page showing all orders - I'm displaying this in a simple table format"""
    return render_template('index.html', orders=orders, logs=action_logs)

@app.route('/add_order', methods=['GET', 'POST'])
def add_order():
    """I'm handling the add new order functionality here"""
    if request.method == 'POST':
        # I'm generating a unique order ID using UUID
        order_id = str(uuid.uuid4())[:8].upper()
        
        # I'm getting all the form data and creating a new order
        num_items = request.form.get('num_items', type=int)
        delivery_date = request.form.get('delivery_date')
        sender_name = request.form.get('sender_name')
        recipient_name = request.form.get('recipient_name')
        recipient_address = request.form.get('recipient_address')
        
        # I'm validating the input data
        if not all([num_items, delivery_date, sender_name, recipient_name, recipient_address]):
            flash('All fields are required!', 'error')
            return render_template('add_order.html')
        
        if num_items <= 0:
            flash('Number of items must be greater than 0!', 'error')
            return render_template('add_order.html')
        
        # I'm creating the new order and storing it
        new_order = Order(order_id, num_items, delivery_date, sender_name, recipient_name, recipient_address)
        orders[order_id] = new_order
        
        # I'm logging this action
        log_action('Created', 'System User', order_id, f'Order with {num_items} items created')
        
        flash(f'Order {order_id} created successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_order.html')

@app.route('/edit_order/<order_id>', methods=['GET', 'POST'])
def edit_order(order_id):
    """I'm handling the edit order functionality here"""
    if order_id not in orders:
        flash('Order not found!', 'error')
        return redirect(url_for('index'))
    
    order = orders[order_id]
    
    if request.method == 'POST':
        # I'm getting the updated data from the form
        old_data = order.to_dict()  # Storing old data for logging
        
        order.num_items = request.form.get('num_items', type=int)
        order.delivery_date = request.form.get('delivery_date')
        order.sender_name = request.form.get('sender_name')
        order.recipient_name = request.form.get('recipient_name')
        order.recipient_address = request.form.get('recipient_address')
        
        # I'm validating the updated data
        if not all([order.num_items, order.delivery_date, order.sender_name, 
                   order.recipient_name, order.recipient_address]):
            flash('All fields are required!', 'error')
            return render_template('edit_order.html', order=order)
        
        if order.num_items <= 0:
            flash('Number of items must be greater than 0!', 'error')
            return render_template('edit_order.html', order=order)
        
        # I'm logging the edit action
        log_action('Edited', 'System User', order_id, 'Order details updated')
        
        flash(f'Order {order_id} updated successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('edit_order.html', order=order)

@app.route('/mark_delivered/<order_id>')
def mark_delivered(order_id):
    """I'm handling the mark as delivered functionality here"""
    if order_id not in orders:
        flash('Order not found!', 'error')
        return redirect(url_for('index'))
    
    order = orders[order_id]
    
    if order.status == 'Delivered':
        flash('Order is already marked as delivered!', 'info')
    else:
        order.status = 'Delivered'
        # I'm logging this action
        log_action('Marked Delivered', 'System User', order_id, 'Order status changed to Delivered')
        flash(f'Order {order_id} marked as delivered!', 'success')
    
    return redirect(url_for('index'))

@app.route('/delete_order/<order_id>')
def delete_order(order_id):
    """I'm handling the delete order functionality here"""
    if order_id not in orders:
        flash('Order not found!', 'error')
        return redirect(url_for('index'))
    
    # I'm storing order details before deletion for logging
    order_details = orders[order_id].to_dict()
    
    # I'm removing the order from our storage
    del orders[order_id]
    
    # I'm logging this action
    log_action('Deleted', 'System User', order_id, f'Order removed from system')
    
    flash(f'Order {order_id} deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/view_logs')
def view_logs():
    """I'm displaying all action logs in a separate page"""
    return render_template('logs.html', logs=action_logs)

@app.route('/api/orders')
def api_orders():
    """I'm providing an API endpoint to get all orders in JSON format"""
    orders_dict = {}
    for order_id, order in orders.items():
        orders_dict[order_id] = order.to_dict()
    return jsonify(orders_dict)

@app.route('/api/logs')
def api_logs():
    """I'm providing an API endpoint to get all logs in JSON format"""
    return jsonify(action_logs)

# I'm creating some sample data for testing purposes
def create_sample_data():
    """I'm adding some sample orders to test the application"""
    sample_orders = [
        {
            'num_items': 5,
            'delivery_date': '2024-12-20',
            'sender_name': 'John Doe',
            'recipient_name': 'Jane Smith',
            'recipient_address': '123 Main St, City, State'
        },
        {
            'num_items': 3,
            'delivery_date': '2024-12-22',
            'sender_name': 'Alice Johnson',
            'recipient_name': 'Bob Wilson',
            'recipient_address': '456 Oak Ave, Town, State'
        }
    ]
    
    for sample in sample_orders:
        order_id = str(uuid.uuid4())[:8].upper()
        new_order = Order(
            order_id,
            sample['num_items'],
            sample['delivery_date'],
            sample['sender_name'],
            sample['recipient_name'],
            sample['recipient_address']
        )
        orders[order_id] = new_order
        log_action('Created', 'System', order_id, 'Sample order created')

if __name__ == '__main__':
    # I'm creating the templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # I'm creating sample data for testing
    create_sample_data()
    
    print("Starting Flask Order Management System...")
    print("Available routes:")
    print("- / : Main page with all orders")
    print("- /add_order : Add new order")
    print("- /edit_order/<id> : Edit existing order")
    print("- /mark_delivered/<id> : Mark order as delivered")
    print("- /delete_order/<id> : Delete order")
    print("- /view_logs : View action logs")
    print("- /api/orders : API endpoint for orders")
    print("- /api/logs : API endpoint for logs")
    
    app.run(debug=True, port=5000)