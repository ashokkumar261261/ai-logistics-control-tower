import sqlite3
from faker import Faker
import random
import os

FAKE = Faker()

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Exception as e:
        print(e)
    return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Exception as e:
        print(e)

def setup_database(db_path="sales_data.db"):
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = create_connection(db_path)

    if conn is not None:
        # Create Employees Table
        create_employees_table = """
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            department TEXT NOT NULL,
            hire_date DATE NOT NULL
        );
        """
        
        # Create Sales Table
        create_sales_table = """
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            amount REAL NOT NULL,
            sale_date DATE NOT NULL,
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        );
        """

        create_table(conn, create_employees_table)
        create_table(conn, create_sales_table)

        # Generate Mock Data
        cursor = conn.cursor()
        
        departments = ['Sales', 'Marketing', 'Engineering', 'HR']
        products = ['Software License', 'Consulting Service', 'Hardware Unit', 'Support Plan']
        
        employees = []
        for _ in range(20):
            name = FAKE.name()
            email = FAKE.email()
            dept = random.choice(departments)
            date = FAKE.date_between(start_date='-5y', end_date='today')
            employees.append((name, email, dept, date))
            
        cursor.executemany("INSERT INTO employees (name, email, department, hire_date) VALUES (?, ?, ?, ?)", employees)
        conn.commit()
        
        # Get employee IDs
        cursor.execute("SELECT id FROM employees")
        emp_ids = [row[0] for row in cursor.fetchall()]

        sales = []
        for _ in range(100):
            emp_id = random.choice(emp_ids)
            prod = random.choice(products)
            amount = round(random.uniform(100.0, 5000.0), 2)
            date = FAKE.date_between(start_date='-1y', end_date='today')
            sales.append((emp_id, prod, amount, date))

        cursor.executemany("INSERT INTO sales (employee_id, product_name, amount, sale_date) VALUES (?, ?, ?, ?)", sales)
        conn.commit()
        
        conn.close()
        print(f"Database setup complete at {db_path}")
    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    setup_database()
