import pandas as pd
from datetime import datetime, timedelta
import random

def generate_sample_data(num_records=100):
    customers = ['CUST001', 'CUST002', 'CUST003', 'CUST004', 'CUST005']
    transaction_types = ['debit', 'credit']
    categories = ['groceries', 'shopping', 'utilities', 'entertainment', 'transfer']
    
    data = []
    for _ in range(num_records):
        customer = random.choice(customers)
        amount = round(random.uniform(10, 2000), 2)
        # Occasionally generate large amounts for fraud testing
        if random.random() < 0.1:
            amount = round(random.uniform(5000, 20000), 2)
        
        timestamp = datetime.now() - timedelta(days=random.randint(0, 30), 
                                           hours=random.randint(0, 23),
                                           minutes=random.randint(0, 59))
        
        data.append({
            'customer_id': customer,
            'timestamp': timestamp,
            'amount': amount,
            'type': random.choice(transaction_types),
            'category': random.choice(categories),
            'merchant': f"Merchant_{random.randint(1, 20)}",
            'location': random.choice(['Local', 'International'])
        })
    
    return pd.DataFrame(data)

# Generate and save sample data
if __name__ == "__main__":
    transactions = generate_sample_data(500)
    transactions.to_csv('transaction_data.csv', index=False)
    print("Successfully generated transaction_data.csv with 500 records")