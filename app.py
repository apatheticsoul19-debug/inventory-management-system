import streamlit as st
import mysql.connector
import pandas as pd

def get_connection():
    return mysql.connector.connect(
        host="mysql-3357b29d-apatheticsoul19-4ee9.a.aivencloud.com",
        port=24161,        # e.g., 15234 (must be a number, not text)
        user="avnadmin",
        password="AVNS_hVR086svhLXqJ0oV6Sd",
        database="defaultdb"
    )


st.title("📦 Inventory and Stock Management System")

menu = st.sidebar.selectbox("Navigation",
                            ["Dashboard & Low Stock", "Manage Products", "Suppliers", "Log Stock Transaction"])

# 1. Dashboard & Low Stock
if menu == "Dashboard & Low Stock":
    st.header("📊 Inventory Overview")
    conn = get_connection()
    products_df = pd.read_sql(
        "SELECT p.product_id, p.sku, p.name, p.category, p.unit_price, p.stock_quantity, p.reorder_level, s.name as supplier_name FROM products p LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id",
        conn)
    conn.close()

    st.subheader("All Products")
    st.dataframe(products_df, use_container_width=True)

    st.subheader("⚠️ Low Stock Alerts (Reorder Required)")
    low_stock = products_df[products_df['stock_quantity'] <= products_df['reorder_level']]
    if not low_stock.empty:
        st.warning(f"Found {len(low_stock)} products below reorder level!")
        st.dataframe(low_stock, use_container_width=True)
    else:
        st.success("All stock levels are healthy!")

# 2. Manage Products
elif menu == "Manage Products":
    st.header("🛍️ Product Management")

    conn = get_connection()
    suppliers_df = pd.read_sql("SELECT supplier_id, name FROM suppliers", conn)
    conn.close()

    supplier_dict = dict(zip(suppliers_df['name'], suppliers_df['supplier_id']))

    with st.form("add_product_form"):
        st.subheader("Add New Product")
        sku = st.text_input("SKU")
        name = st.text_input("Product Name")
        category = st.text_input("Category")
        unit_price = st.number_input("Unit Price", min_value=0.0, format="%.2f")
        stock_quantity = st.number_input("Initial Stock Quantity", min_value=0, step=1)
        reorder_level = st.number_input("Reorder Level Alert", min_value=0, value=10, step=1)
        selected_supplier = st.selectbox("Supplier", list(supplier_dict.keys()))

        submitted = st.form_submit_button("Add Product")
        if submitted and sku and name:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO products (sku, name, category, unit_price, stock_quantity, reorder_level, supplier_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (sku, name, category, unit_price, stock_quantity, reorder_level, supplier_dict[selected_supplier])
            )
            conn.commit()
            conn.close()
            st.success(f"Product '{name}' added successfully!")

# 3. Suppliers
elif menu == "Suppliers":
    st.header("🏭 Supplier Management")

    with st.form("add_supplier_form"):
        st.subheader("Add New Supplier")
        sup_name = st.text_input("Supplier Company Name")
        contact_person = st.text_input("Contact Person")
        phone = st.text_input("Phone Number")
        email = st.text_input("Email")

        sup_submitted = st.form_submit_button("Save Supplier")
        if sup_submitted and sup_name:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO suppliers (name, contact_person, phone, email) VALUES (%s, %s, %s, %s)",
                (sup_name, contact_person, phone, email)
            )
            conn.commit()
            conn.close()
            st.success(f"Supplier '{sup_name}' added successfully!")

    st.subheader("Existing Suppliers List")
    conn = get_connection()
    sup_df = pd.read_sql("SELECT * FROM suppliers", conn)
    conn.close()
    st.dataframe(sup_df, use_container_width=True)

# 4. Log Stock Transaction
elif menu == "Log Stock Transaction":
    st.header("📝 Log In / Out Stock Movement")

    conn = get_connection()
    prod_df = pd.read_sql("SELECT product_id, name, stock_quantity FROM products", conn)
    conn.close()

    prod_dict = dict(
        zip(prod_df['name'] + " (Current Stock: " + prod_df['stock_quantity'].astype(str) + ")", prod_df['product_id']))

    with st.form("transaction_form"):
        selected_prod_label = st.selectbox("Select Product", list(prod_dict.keys()))
        tx_type = st.selectbox("Transaction Type", ["IN (Restock)", "OUT (Sale/Usage)"])
        quantity = st.number_input("Quantity", min_value=1, step=1)
        ref_note = st.text_input("Reference Note (e.g., Invoice # or Customer Order)")

        tx_submitted = st.form_submit_button("Record Transaction")
        if tx_submitted:
            p_id = prod_dict[selected_prod_label]
            t_code = "IN" if "IN" in tx_type else "OUT"

            conn = get_connection()
            cursor = conn.cursor()

            # Insert Transaction
            cursor.execute(
                "INSERT INTO stock_transactions (product_id, transaction_type, quantity, reference_note) VALUES (%s, %s, %s, %s)",
                (p_id, t_code, quantity, ref_note)
            )

            # Update product stock quantity automatically
            if t_code == "IN":
                cursor.execute("UPDATE products SET stock_quantity = stock_quantity + %s WHERE product_id = %s",
                               (quantity, p_id))
            else:
                cursor.execute("UPDATE products SET stock_quantity = stock_quantity - %s WHERE product_id = %s",
                               (quantity, p_id))

            conn.commit()
            conn.close()
            st.success("Transaction recorded and stock updated successfully!")
