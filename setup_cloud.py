import mysql.connector

# Connect to your Aiven Cloud MySQL database
conn = mysql.connector.connect(
    host="mysql-3357b29d-apatheticsoul19-4ee9.a.aivencloud.com",
    port=24161,
    user="avnadmin",
    password="AVNS_hvR086svhLXqJOoV6Sd",
    database="defaultdb"
)

cursor = conn.cursor()

# 1. Suppliers Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact_person VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# 2. Products Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    reorder_level INT NOT NULL DEFAULT 10,
    supplier_id INT,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# 3. Stock Transactions Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS stock_transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    transaction_type ENUM('IN', 'OUT') NOT NULL,
    quantity INT NOT NULL,
    reference_note VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);
""")

# Insert Sample Data (using INSERT IGNORE to prevent duplicate errors)
cursor.execute("INSERT IGNORE INTO suppliers (supplier_id, name, contact_person, phone, email) VALUES (1, 'TechCorp Supplies', 'Rohan Sharma', '9876543210', 'rohan@techcorp.com');")
cursor.execute("INSERT IGNORE INTO products (sku, name, category, unit_price, stock_quantity, reorder_level, supplier_id) VALUES ('SKU-001', 'Wireless Mouse', 'Electronics', 499.99, 45, 10, 1);")

conn.commit()
cursor.close()
conn.close()

print("Cloud database tables and sample data verified successfully!")