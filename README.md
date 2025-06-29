# Flask Admin Dashboard

This is a simple Flask-based admin dashboard application.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/dee-mee/flask-admin-dashboard.git
    cd flask-admin-dashboard
    ```

2.  **Create a virtual environment and activate it:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install Flask Flask-SQLAlchemy Flask-Login
    ```

4.  **Initialize the database:**
    ```bash
    python init_db.py
    ```

## Running the Application

To run the Flask application, use the following command:

```bash
flask run
```

The application should then be accessible at `http://127.0.0.1:5000/`.
