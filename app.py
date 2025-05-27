from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from fraud_detection import FraudDetector
from investment_advisor import InvestmentAdvisor
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'
# new_trans_df creation moved inside add_transaction
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            session['username'] = username
            return redirect(url_for('add_transaction'))
        except sqlite3.IntegrityError:
            flash("Username already exists")
            return redirect(url_for('signup'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_input = request.form['password']
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password_input):
            session['username'] = username
            return redirect(url_for('add_transaction'))
        else:
            flash("Invalid credentials")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Load transaction data
transactions = pd.read_csv('transaction_data.csv')
transactions['timestamp'] = pd.to_datetime(transactions['timestamp'])

# Initialize systems
detector = FraudDetector(transactions)
advisor = InvestmentAdvisor(transactions)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        action = request.form['action']  # 'login' or 'signup'

        conn = get_db_connection()

        if action == 'signup':
            try:
                hashed_password = generate_password_hash(password)
                conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
                conn.commit()
                session['username'] = username
                conn.close()
                return redirect(url_for('add_transaction'))
            except sqlite3.IntegrityError:
                flash("Username already exists")
                return redirect(url_for('index'))

        elif action == 'login':
            user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            conn.close()
            if user and check_password_hash(user['password'], password):
                session['username'] = username
                return redirect(url_for('add_transaction'))
            else:
                flash("Invalid username or password")
                return redirect(url_for('index'))

    return render_template('index.html')


@app.route('/fraud', methods=['GET', 'POST'])
def fraud_detection():
    if request.method == 'POST':
        customer_id = request.form.get('customer_id', '').strip()
        check_type = request.form.get('check_type')
        
        if check_type == 'high_amount':
            results = detector.detect_high_amount(customer_id if customer_id else None)
            title = "High Amount Transactions"
        elif check_type == 'rapid':
            results = detector.detect_rapid_transactions(customer_id if customer_id else None)
            title = "Rapid Transactions"
        elif check_type == 'international':
            results = detector.detect_international_transactions(customer_id if customer_id else None)
            title = "International Transactions"
        elif check_type == 'all':
            results = detector.run_all_checks(customer_id if customer_id else None)
            title = "All Fraud Checks"
        else:
            results = pd.DataFrame()
            title = "No Results"
        
        # Convert results to HTML
        if isinstance(results, dict):  # For 'all' checks
            results_html = {}
            for check, df in results.items():
                results_html[check] = df.to_html(classes='table table-striped', index=False) if not df.empty else "<p>No suspicious transactions found</p>"
        else:
            results_html = results.to_html(classes='table table-striped', index=False) if not results.empty else "<p>No suspicious transactions found</p>"
        
        return render_template('fraud.html', 
                            results=results_html, 
                            title=title,
                            customer_id=customer_id,
                            check_type=check_type)
    
    return render_template('fraud.html')

@app.route('/investments', methods=['GET', 'POST'])
def investment_recommendations():
    if request.method == 'POST':
        customer_id = request.form.get('customer_id', '').strip()
        if customer_id:
            recommendations = advisor.get_recommendations(customer_id)
            
            if "error" in recommendations:
                return render_template('investments.html', error=recommendations["error"], customer_id=customer_id)
            
            return render_template('investments.html', recommendations=recommendations, customer_id=customer_id)
    
    # Default view with sample customer IDs
    sample_customers = transactions['customer_id'].unique()[:5]
    return render_template('investments.html', sample_customers=sample_customers)

@app.route('/add_transaction', methods=['GET', 'POST'])
def add_transaction():
    if 'username' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        new_trans = {
            'customer_id': session['username'],
            'timestamp': pd.to_datetime(request.form['timestamp']),
            'amount': float(request.form['amount']),
            'type': request.form['type'],
            'category': request.form['category'],
            'merchant': request.form['merchant'],
            'location': request.form['location']
        }

        # Convert dict to DataFrame and append using concat
        global transactions
        new_trans_df = pd.DataFrame([new_trans])
        transactions = pd.concat([transactions, new_trans_df], ignore_index=True)
        transactions.to_csv('transaction_data.csv', index=False)

    return render_template('add_transaction.html')
if __name__ == '__main__':
    app.run(debug=True)