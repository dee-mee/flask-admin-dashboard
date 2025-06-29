from app import app, db, User, Task, Order, Activity, Transaction, SalesData, UserStats, RevenueSource, Message, DashboardStats
from werkzeug.security import generate_password_hash
import datetime

with app.app_context():
    db.drop_all() # Drop all tables to ensure a clean slate
    db.create_all()

    # Create a default admin user if not exists
    if not User.query.filter_by(username='admin').first():
        admin_user = User(username='admin', full_name='Admin User', email='admin@example.com', phone='(254) 456-7890', address='123 Admin Street, City, Country')
        admin_user.set_password('password')
        db.session.add(admin_user)
        db.session.commit()
        print("Default admin user created: username='admin', password='password'")

    # Add some sample data if tables are empty
    if not Task.query.first():
        db.session.add_all([
            Task(name='Design new dashboard', due_date=datetime.date(2025, 7, 15)),
            Task(name='Develop new features', due_date=datetime.date(2025, 7, 20)),
            Task(name='Test and deploy', due_date=datetime.date(2025, 7, 25))
        ])
        db.session.commit()

    if not Order.query.first():
        db.session.add_all([
            Order(customer='John Doe', product='Product A', amount=100.00, status='Completed'),
            Order(customer='Jane Smith', product='Product B', amount=50.00, status='Pending'),
            Order(customer='Peter Jones', product='Product C', amount=75.00, status='Cancelled'),
        ])
        db.session.commit()

    if not Activity.query.first():
        db.session.add_all([
            Activity(description='New user registered: John Doe'),
            Activity(description='New order placed: #1235'),
            Activity(description='User updated profile: Jane Smith'),
        ])
        db.session.commit()

    if not Transaction.query.first():
        db.session.add_all([
            Transaction(description='Initial Deposit', amount=10000.00, type='deposit'),
            Transaction(description='Sent to John Doe', amount=50.00, type='withdrawal'),
            Transaction(description='Received from Jane Smith', amount=100.00, type='deposit'),
        ])
        db.session.commit()

    

    if not UserStats.query.first():
        db.session.add(UserStats(new_users=35, returning_users=60, inactive_users=15))
        db.session.commit()

    if not RevenueSource.query.first():
        db.session.add(RevenueSource(organic=15000.00, referral=8000.00, direct=18000.00, social=5000.00))
        db.session.commit()

    if not Message.query.first():
        db.session.add_all([
            Message(content='Welcome to the new dashboard!'),
            Message(content='New features coming soon.'),
            Message(content='Check out the updated analytics.'),
        ])
        db.session.commit()

    if not DashboardStats.query.first():
        db.session.add(DashboardStats(total_users=24500, total_revenue=48500.00, new_orders=1245, messages=0))
        db.session.commit()

    print("Database initialized and populated with sample data.")
