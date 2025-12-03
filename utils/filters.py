import psycopg2
from dotenv import load_dotenv
import os
from db import get_db_connection


# Load environment variables
load_dotenv()

#for local server


def filter_data(user_id, start_date, end_date, category=None):
    """Filters transaction data based on user criteria."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT type, amount, category, date 
            FROM transactions 
            WHERE user_id = %s AND date BETWEEN %s AND %s
        '''
        params = [user_id, start_date, end_date]
        
        if category:
            query += ' AND category = %s'
            params.append(category)
        
        query += ' ORDER BY date'
        
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        
        # Convert to list of dictionaries for easier handling
        result = []
        for row in rows:
            result.append({
                'type': row[0],
                'amount': float(row[1]),
                'category': row[2],
                'date': row[3].strftime('%Y-%m-%d')
            })
        
        return result
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            cursor.close()
            conn.close()