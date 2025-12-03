import psycopg2
from datetime import datetime
from dotenv import load_dotenv
import os
from decimal import Decimal
from db import get_db_connection

# Load environment variables
load_dotenv()

#for local server




def analyze_spending(user_id, month):
    """Analyzes spending patterns and provides advice."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total income and expenses for the month
        cursor.execute('''
            SELECT 
                COALESCE(SUM(CASE WHEN type = 'Income' THEN amount ELSE 0 END)::float, 0) as income,
                COALESCE(SUM(CASE WHEN type = 'Expense' THEN amount ELSE 0 END)::float, 0) as expense
            FROM transactions
            WHERE user_id = %s AND to_char(date, 'YYYY-MM') = %s
        ''', (user_id, month))
        
        total_income, total_expense = cursor.fetchone()
        # Convert to float if they're Decimal
        if isinstance(total_income, Decimal):
            total_income = float(total_income)
        if isinstance(total_expense, Decimal):
            total_expense = float(total_expense)
            
        savings = total_income - total_expense
        
        advice = []
        
        # Savings advice
        if savings < 0:
            advice.append("⚠️ You're spending more than you earn this month! Consider reducing expenses.")
        elif savings > 0 and savings < (0.2 * total_income):
            advice.append("💡 You're saving some money, but try to save at least 20% of your income.")
        elif savings >= (0.2 * total_income):
            advice.append("✅ Great job! You're saving a healthy portion of your income.")
        
        # Get expense breakdown by category
        cursor.execute('''
            SELECT category, SUM(amount)::float as total
            FROM transactions
            WHERE user_id = %s AND type = 'Expense' AND to_char(date, 'YYYY-MM') = %s
            GROUP BY category
            ORDER BY total DESC
        ''', (user_id, month))
        
        expenses_by_category = cursor.fetchall()
        
        if expenses_by_category:
            # Check if any single category is more than 50% of expenses
            for category, amount in expenses_by_category:
                if isinstance(amount, Decimal):
                    amount = float(amount)
                
                if amount > 0.5 * total_expense:
                    advice.append(f"⚠️ You're spending {amount/total_expense*100:.1f}% of your expenses on '{category}'. Consider diversifying your spending.")
                
                # Generic advice for top categories
                if amount > 0.3 * total_expense:
                    advice.append(f"💸 You're spending a lot on '{category}'. Maybe look for ways to reduce this expense.")
        
        # Check if there are any expenses at all
        if total_expense == 0 and total_income > 0:
            advice.append("🌟 You haven't recorded any expenses this month. Great savings!")
        
        # Check if income is zero
        if total_income == 0:
            advice.append("🔄 You haven't recorded any income this month. Don't forget to track your earnings!")
        
        return advice
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return ["An error occurred while analyzing your spending."]
    finally:
        if conn:
            cursor.close()
            conn.close()