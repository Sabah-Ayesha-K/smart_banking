import pandas as pd
from datetime import datetime, timedelta

class FraudDetector:
    def __init__(self, transaction_data):
        self.transactions = transaction_data
        self.fraud_rules = {
            'high_amount': 5000,  # Threshold for high amount transactions
            'rapid_transactions': 5,  # Number of transactions in time window
            'time_window_minutes': 10  # Time window for rapid transactions
        }
    
    def detect_high_amount(self, customer_id=None):
        """Detect transactions above threshold amount"""
        threshold = self.fraud_rules['high_amount']
        if customer_id:
            return self.transactions[(self.transactions['customer_id'] == customer_id) & 
                                   (self.transactions['amount'] > threshold)]
        return self.transactions[self.transactions['amount'] > threshold]
    
    def detect_rapid_transactions(self, customer_id=None):
        """Detect multiple transactions in short time window"""
        data = self.transactions.copy()
        if customer_id:
            data = data[data['customer_id'] == customer_id]
        
        data = data.sort_values(['customer_id', 'timestamp'])
        data['time_diff'] = data.groupby('customer_id')['timestamp'].diff().dt.total_seconds() / 60
        
        # Find sequences of rapid transactions
        rapid_trans = data[data['time_diff'] <= self.fraud_rules['time_window_minutes']]
        counts = rapid_trans['customer_id'].value_counts()
        suspects = counts[counts >= self.fraud_rules['rapid_transactions'] - 1].index
        
        return data[data['customer_id'].isin(suspects)]
    
    def detect_international_transactions(self, customer_id=None):
        """Flag international transactions which might be suspicious"""
        data = self.transactions.copy()
        if customer_id:
            data = data[data['customer_id'] == customer_id]
        
        return data[data['location'] == 'International']
    
    def run_all_checks(self, customer_id=None):
        """Run all fraud detection checks"""
        results = {
            'high_amount': self.detect_high_amount(customer_id),
            'rapid_transactions': self.detect_rapid_transactions(customer_id),
            'international': self.detect_international_transactions(customer_id)
        }
        return results

# Example usage
transactions = pd.read_csv('transaction_data.csv')
transactions['timestamp'] = pd.to_datetime(transactions['timestamp'])

detector = FraudDetector(transactions)
fraud_results = detector.run_all_checks()

print("High amount transactions:\n", fraud_results['high_amount'])
print("\nRapid transactions:\n", fraud_results['rapid_transactions'].head())
print("\nInternational transactions:\n", fraud_results['international'].head())