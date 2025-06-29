from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key' # Replace with a strong secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    completed = db.Column(db.Boolean, default=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer = db.Column(db.String(100), nullable=False)
    product = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(50), nullable=False) # e.g., 'deposit', 'withdrawal'
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class SalesData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.String(20), nullable=False, unique=True)
    amount = db.Column(db.Float, nullable=False)

class UserStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    new_users = db.Column(db.Integer, nullable=False)
    returning_users = db.Column(db.Integer, nullable=False)
    inactive_users = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class RevenueSource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organic = db.Column(db.Float, nullable=False)
    referral = db.Column(db.Float, nullable=False)
    direct = db.Column(db.Float, nullable=False)
    social = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class DashboardStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_users = db.Column(db.Integer, nullable=False)
    total_revenue = db.Column(db.Float, nullable=False)
    new_orders = db.Column(db.Integer, nullable=False)
    messages = db.Column(db.Integer, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def dashboard():
    return render_template('index.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/wallet')
@login_required
def wallet():
    transactions = Transaction.query.order_by(Transaction.timestamp.desc()).all()
    current_balance = sum(t.amount if t.type == 'deposit' else -t.amount for t in transactions)
    return render_template('wallet.html', transactions=transactions, current_balance=current_balance)

@app.route('/analytics')
@login_required
def analytics():
    return render_template('analytics.html')

@app.route('/tasks')
@login_required
def tasks():
    tasks_data = Task.query.all()
    return render_template('tasks.html', tasks=tasks_data)

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@app.route('/dashboard_input', methods=['GET', 'POST'])
@login_required
def dashboard_input():
    stats = DashboardStats.query.first()
    if request.method == 'POST':
        if not stats:
            stats = DashboardStats(
                total_users=int(request.form['total_users']),
                total_revenue=float(request.form['total_revenue']),
                new_orders=int(request.form['new_orders']),
                messages=int(request.form['messages'])
            )
            db.session.add(stats)
        else:
            stats.total_users = int(request.form['total_users'])
            stats.total_revenue = float(request.form['total_revenue'])
            stats.new_orders = int(request.form['new_orders'])
            stats.messages = int(request.form['messages'])
        db.session.commit()
        flash('Dashboard statistics updated successfully!', 'success')
        return redirect(url_for('dashboard_input'))
    return render_template('dashboard_input.html', stats=stats)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# API Endpoints
@app.route('/api/tasks', methods=['GET', 'POST'])
def api_tasks():
    if request.method == 'POST':
        data = request.get_json()
        new_task = Task(name=data['name'], due_date=datetime.datetime.strptime(data['due_date'], '%Y-%m-%d').date())
        db.session.add(new_task)
        db.session.commit()
        return jsonify({'message': 'Task added successfully!', 'id': new_task.id}), 201
    tasks_data = Task.query.all()
    return jsonify([{'id': task.id, 'name': task.name, 'due_date': task.due_date.strftime('%Y-%m-%d'), 'completed': task.completed} for task in tasks_data])

@app.route('/api/tasks/<int:task_id>', methods=['PUT', 'DELETE'])
def api_task(task_id):
    task = Task.query.get_or_404(task_id)
    if request.method == 'PUT':
        data = request.get_json()
        task.name = data.get('name', task.name)
        task.due_date = datetime.datetime.strptime(data['due_date'], '%Y-%m-%d').date() if 'due_date' in data else task.due_date
        task.completed = data.get('completed', task.completed)
        db.session.commit()
        return jsonify({'message': 'Task updated successfully!'}), 200
    elif request.method == 'DELETE':
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Task deleted successfully!'}), 200

@app.route('/api/orders')
def api_orders():
    orders_data = Order.query.order_by(Order.order_date.desc()).all()
    return jsonify([{'id': order.id, 'customer': order.customer, 'product': order.product, 'amount': order.amount, 'status': order.status, 'order_date': order.order_date.strftime('%Y-%m-%d %H:%M:%S')} for order in orders_data])

@app.route('/api/activities')
def api_activities():
    activities_data = Activity.query.order_by(Activity.timestamp.desc()).all()
    return jsonify([{'id': activity.id, 'description': activity.description, 'timestamp': activity.timestamp.strftime('%Y-%m-%d %H:%M:%S')} for activity in activities_data])

@app.route('/api/transactions', methods=['GET', 'POST'])
def api_transactions():
    if request.method == 'POST':
        data = request.get_json()
        new_transaction = Transaction(description=data['description'], amount=data['amount'], type=data['type'])
        db.session.add(new_transaction)
        db.session.commit()
        return jsonify({'message': 'Transaction added successfully!', 'id': new_transaction.id}), 201
    transactions_data = Transaction.query.order_by(Transaction.timestamp.desc()).all()
    return jsonify([{'id': t.id, 'description': t.description, 'amount': t.amount, 'type': t.type, 'timestamp': t.timestamp.strftime('%Y-%m-%d %H:%M:%S')} for t in transactions_data])

@app.route('/api/sales_data', methods=['GET', 'POST'])
def api_sales_data():
    if request.method == 'POST':
        data = request.get_json()
        new_sales_data = SalesData(month=data['month'], amount=data['amount'])
        db.session.add(new_sales_data)
        db.session.commit()
        return jsonify({'message': 'Sales data added successfully!', 'id': new_sales_data.id}), 201
    sales_data = SalesData.query.order_by(SalesData.id).all()
    return jsonify([{'id': s.id, 'month': s.month, 'amount': s.amount} for s in sales_data])

@app.route('/api/user_stats', methods=['GET', 'POST'])
def api_user_stats():
    if request.method == 'POST':
        data = request.get_json()
        new_user_stats = UserStats(
            new_users=data['new_users'],
            returning_users=data['returning_users'],
            inactive_users=data['inactive_users']
        )
        db.session.add(new_user_stats)
        db.session.commit()
        return jsonify({'message': 'User stats added successfully!', 'id': new_user_stats.id}), 201
    user_stats = UserStats.query.order_by(UserStats.timestamp.desc()).first()
    if user_stats:
        return jsonify({
            'new_users': user_stats.new_users,
            'returning_users': user_stats.returning_users,
            'inactive_users': user_stats.inactive_users
        })
    return jsonify({'message': 'No user stats available'}), 404

@app.route('/api/revenue_source', methods=['GET', 'POST'])
def api_revenue_source():
    if request.method == 'POST':
        data = request.get_json()
        new_revenue_source = RevenueSource(
            organic=data['organic'],
            referral=data['referral'],
            direct=data['direct'],
            social=data['social']
        )
        db.session.add(new_revenue_source)
        db.session.commit()
        return jsonify({'message': 'Revenue source added successfully!', 'id': new_revenue_source.id}), 201
    revenue_source = RevenueSource.query.order_by(RevenueSource.timestamp.desc()).first()
    if revenue_source:
        return jsonify({
            'organic': revenue_source.organic,
            'referral': revenue_source.referral,
            'direct': revenue_source.direct,
            'social': revenue_source.social
        })
    return jsonify({'message': 'No revenue source data available'}), 404

@app.route('/api/user_profile')
@login_required
def api_user_profile():
    user = current_user
    return jsonify({
        'username': user.username,
        'full_name': user.full_name,
        'email': user.email,
        'phone': user.phone,
        'address': user.address
    })

@app.route('/api/change_password', methods=['POST'])
@login_required
def api_change_password():
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not current_password or not new_password:
        return jsonify({'message': 'Missing current or new password'}), 400

    if not current_user.check_password(current_password):
        return jsonify({'message': 'Incorrect current password'}), 401

    current_user.set_password(new_password)
    db.session.commit()
    return jsonify({'message': 'Password changed successfully'}), 200

@app.route('/api/dashboard_stats')
@login_required
def api_dashboard_stats():
    stats = DashboardStats.query.first()
    if stats:
        return jsonify({
            'total_users': stats.total_users,
            'total_revenue': stats.total_revenue,
            'new_orders': stats.new_orders,
            'messages': stats.messages
        })
    return jsonify({'message': 'No dashboard stats available'}), 404

@app.route('/api/update_dashboard_stats', methods=['POST'])
@login_required
def api_update_dashboard_stats():
    data = request.get_json()
    stats = DashboardStats.query.first()
    if not stats:
        stats = DashboardStats(
            total_users=data.get('total_users', 0),
            total_revenue=data.get('total_revenue', 0.0),
            new_orders=data.get('new_orders', 0),
            messages=data.get('messages', 0)
        )
        db.session.add(stats)
    else:
        stats.total_users = data.get('total_users', stats.total_users)
        stats.total_revenue = data.get('total_revenue', stats.total_revenue)
        stats.new_orders = data.get('new_orders', stats.new_orders)
        stats.messages = data.get('messages', stats.messages)
    db.session.commit()
    return jsonify({'message': 'Dashboard stats updated successfully!'}), 200

if __name__ == '__main__':
    app.run(debug=True)
