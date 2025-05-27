from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from fraud_detection import FraudDetector
from investment_advisor import InvestmentAdvisor
from datetime import datetime

app = Flask(__name__)

# Load transaction data
transactions = pd.read_csv('transaction_data.csv')
transactions['timestamp'] = pd.to_datetime(transactions['timestamp'])

# Initialize systems
detector = FraudDetector(transactions)
advisor = InvestmentAdvisor(transactions)

@app.route('/')
def index():
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

if __name__ == '__main__':
    app.run(debug=True)