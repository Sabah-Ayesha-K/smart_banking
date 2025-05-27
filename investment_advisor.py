import pandas as pd
from collections import defaultdict

class InvestmentAdvisor:
    def __init__(self, transaction_data):
        self.transactions = transaction_data
        self.spending_profiles = {
            'conservative': {'fd': 0.5, 'mutual_funds': 0.3, 'gold': 0.2},
            'moderate': {'mutual_funds': 0.5, 'stocks': 0.3, 'fd': 0.2},
            'aggressive': {'stocks': 0.6, 'crypto': 0.2, 'mutual_funds': 0.2},
            'balanced': {'mutual_funds': 0.4, 'stocks': 0.3, 'fd': 0.2, 'gold': 0.1}
        }
    
    def analyze_spending(self, customer_id):
        """Analyze customer's spending habits"""
        customer_trans = self.transactions[
            (self.transactions['customer_id'] == customer_id) & 
            (self.transactions['type'] == 'debit')  # Only consider debits (spending)
        ]
        
        if customer_trans.empty:
            return None
        
        total_spent = customer_trans['amount'].sum()
        avg_transaction = customer_trans['amount'].mean()
        spending_categories = customer_trans['category'].value_counts(normalize=True)
        
        # Determine risk profile
        if avg_transaction < 100 and total_spent < 2000:
            risk_profile = 'conservative'
        elif avg_transaction < 500 and total_spent < 10000:
            risk_profile = 'moderate'
        elif total_spent > 15000:
            risk_profile = 'aggressive'
        else:
            risk_profile = 'balanced'
        
        return {
            'total_spent': total_spent,
            'avg_transaction': avg_transaction,
            'spending_categories': spending_categories.to_dict(),
            'risk_profile': risk_profile
        }
    
    def get_recommendations(self, customer_id):
        """Get investment recommendations based on spending profile"""
        analysis = self.analyze_spending(customer_id)
        if not analysis:
            return {"error": "Customer not found or no spending data"}
        
        profile = analysis['risk_profile']
        recommendations = self.spending_profiles.get(profile, {})
        
        # Add fund suggestions
        fund_suggestions = {
            'fd': ["5-year Tax Saver FD @6.5%", "Senior Citizen FD @7.2%"],
            'mutual_funds': ["Index Fund - Large Cap", "Balanced Advantage Fund"],
            'stocks': ["Blue Chip Stocks", "Tech Sector ETF"],
            'gold': ["Sovereign Gold Bonds", "Gold ETF"],
            'crypto': ["Bitcoin", "Ethereum"]  # With caution disclaimer
        }
        
        detailed_recommendations = []
        for inv_type, ratio in recommendations.items():
            detailed_recommendations.append({
                'type': inv_type,
                'allocation': ratio,
                'suggestions': fund_suggestions.get(inv_type, [])
            })
        
        return {
            'customer_id': customer_id,
            'risk_profile': profile,
            'spending_analysis': analysis,
            'recommendations': detailed_recommendations
        }