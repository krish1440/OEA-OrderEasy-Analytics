import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
from supabase import create_client, Client
import cloudinary
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv
import os
from io import BytesIO
import uuid
import requests
import logging
from sklearn.linear_model import LinearRegression
import seaborn as sns
from scipy import stats
import re
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file for local
if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")
    admin_username = os.getenv("ADMIN_USERNAME")
    admin_password = os.getenv("ADMIN_PASSWORD")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
else:
    cloud_name = st.secrets["CLOUDINARY_CLOUD_NAME"]
    api_key = st.secrets["CLOUDINARY_API_KEY"]
    api_secret = st.secrets["CLOUDINARY_API_SECRET"]
    admin_username = st.secrets["ADMIN_USERNAME"]
    admin_password = st.secrets["ADMIN_PASSWORD"]
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_key = st.secrets["SUPABASE_KEY"]

# Configure Cloudinary
cloudinary.config(
    cloud_name=cloud_name,
    api_key=api_key,
    api_secret=api_secret
)

# Initialize Supabase client
supabase: Client = create_client(supabase_url, supabase_key)

# Set page configuration
st.set_page_config(page_title="Order Management System", layout="wide")

# Database setup
def init_db():
    # Existing table checks (users, orders, ewaybills) remain unchanged
    try:
        supabase.table("users").select("*").limit(1).execute()
        logger.info("Users table exists")
    except Exception as e:
        logger.error(f"Users table does not exist: {e}")
        st.error("The 'users' table is missing in Supabase. Please create it using the following SQL in the Supabase SQL Editor:")
        st.code("""
CREATE TABLE users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    organization TEXT NOT NULL,
    is_admin INTEGER DEFAULT 0
);
        """)
        raise Exception("Users table missing. Please create it and rerun the application.")

    try:
        supabase.table("orders").select("*").limit(1).execute()
        logger.info("Orders table exists")
    except Exception as e:
        logger.error(f"Orders table does not exist: {e}")
        st.error("The 'orders' table is missing in Supabase. Please create it using the following SQL in the Supabase SQL Editor:")
        st.code("""
CREATE TABLE orders (
    order_id INTEGER,
    org TEXT,
    receiver_name TEXT,
    date TEXT,
    expected_delivery_date TEXT,
    product TEXT,
    description TEXT,
    quantity INTEGER,
    delivered_quantity INTEGER DEFAULT 0,
    price REAL,
    basic_price REAL,
    gst REAL,
    advance_payment REAL,
    total_amount_with_gst REAL,
    pending_amount REAL,
    status TEXT,
    created_by TEXT,
    PRIMARY KEY (order_id, org)
);
        """)
        raise Exception("Orders table missing. Please create it and rerun the application.")

    try:
        supabase.table("deliveries").select("*").limit(1).execute()
        logger.info("Deliveries table exists")
    except Exception as e:
        logger.error(f"Deliveries table does not exist: {e}")
        st.error("The 'deliveries' table is missing in Supabase. Please create it using the following SQL in the Supabase SQL Editor:")
        st.code("""
CREATE TABLE deliveries (
    delivery_id SERIAL PRIMARY KEY,
    order_id INTEGER,
    org TEXT,
    delivery_quantity INTEGER,
    delivery_date TEXT,
    total_amount_received REAL,
    public_id TEXT,
    url TEXT,
    file_name TEXT,
    upload_date TEXT,
    resource_type TEXT,
    FOREIGN KEY (order_id, org) REFERENCES orders (order_id, org)
);
        """)
        raise Exception("Deliveries table missing. Please create it and rerun the application.")

    # Check and add total_amount_received column to deliveries if not exists
    try:
        response = supabase.table("deliveries").select("total_amount_received").limit(1).execute()
        logger.info("total_amount_received column exists in deliveries table")
    except Exception as e:
        logger.error(f"total_amount_received column does not exist in deliveries table: {e}")
        st.error("The 'total_amount_received' column is missing in the 'deliveries' table. Please add it using the following SQL in the Supabase SQL Editor:")
        st.code("""
ALTER TABLE deliveries ADD COLUMN total_amount_received REAL;
        """)
        raise Exception("total_amount_received column missing in deliveries table. Please add it and rerun the application.")

    # Check and remove base_price column from deliveries if exists
    
        

    try:
        supabase.table("ewaybills").select("*").limit(1).execute()
        logger.info("Ewaybills table exists")
    except Exception as e:
        logger.error(f"Ewaybills table does not exist: {e}")
        st.error("The 'ewaybills' table is missing in Supabase. Please create it using the following SQL in the Supabase SQL Editor:")
        st.code("""
CREATE TABLE ewaybills (
    order_id INTEGER,
    org TEXT,
    public_id TEXT,
    url TEXT,
    file_name TEXT,
    upload_date TEXT,
    resource_type TEXT,
    PRIMARY KEY (order_id, org),
    FOREIGN KEY (order_id, org) REFERENCES orders (order_id, org)
);
        """)
        raise Exception("Ewaybills table missing. Please create it and rerun the application.")

    # Check and add is_admin column to users if not exists
    try:
        response = supabase.table("users").select("is_admin").limit(1).execute()
        logger.info("is_admin column exists in users table")
    except Exception as e:
        logger.error(f"is_admin column does not exist in users table: {e}")
        st.error("The 'is_admin' column is missing in the 'users' table. Please add it using the following SQL in the Supabase SQL Editor:")
        st.code("""
ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0;
        """)
        raise Exception("is_admin column missing. Please add it and rerun the application.")

    # Check and add delivered_quantity column to orders if not exists
    try:
        response = supabase.table("orders").select("delivered_quantity").limit(1).execute()
        logger.info("delivered_quantity column exists in orders table")
    except Exception as e:
        logger.error(f"delivered_quantity column does not exist in orders table: {e}")
        st.error("The 'delivered_quantity' column is missing in the 'orders' table. Please add it using the following SQL in the Supabase SQL Editor:")
        st.code("""
ALTER TABLE orders ADD COLUMN delivered_quantity INTEGER DEFAULT 0;
        """)
        raise Exception("delivered_quantity column missing. Please add it and rerun the application.")

    # Check and add resource_type column to ewaybills if not exists
    try:
        response = supabase.table("ewaybills").select("resource_type").limit(1).execute()
        logger.info("resource_type column exists in ewaybills table")
    except Exception as e:
        logger.error(f"resource_type column does not exist in ewaybills table: {e}")
        st.error("The 'resource_type' column is missing in the 'ewaybills' table. Please add it and populate existing records using the following SQL in the Supabase SQL Editor:")
        st.code("""
ALTER TABLE ewaybills ADD COLUMN resource_type TEXT;
UPDATE ewaybills SET resource_type = CASE
    WHEN file_name LIKE '%.pdf' THEN 'raw'
    ELSE 'image'
END;
        """)
        raise Exception("resource_type column missing. Please add it and rerun the application.")

    # Check and add resource_type column to deliveries if not exists
    try:
        response = supabase.table("deliveries").select("resource_type").limit(1).execute()
        logger.info("resource_type column exists in deliveries table")
    except Exception as e:
        logger.error(f"resource_type column does not exist in deliveries table: {e}")
        st.error("The 'resource_type' column is missing in the 'deliveries' table. Please add it and populate existing records using the following SQL in the Supabase SQL Editor:")
        st.code("""
ALTER TABLE deliveries ADD COLUMN resource_type TEXT;
UPDATE deliveries SET resource_type = CASE
    WHEN file_name LIKE '%.pdf' THEN 'raw'
    ELSE 'image'
END;
        """)
        raise Exception("resource_type column missing in deliveries table. Please add it and rerun the application.")

init_db()

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "current_org" not in st.session_state:
    st.session_state.current_org = None
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False
if "form_message" not in st.session_state:
    st.session_state.form_message = ""
if "form_status" not in st.session_state:
    st.session_state.form_status = ""
if "editing_order" not in st.session_state:
    st.session_state.editing_order = None
if "clear_form" not in st.session_state:
    st.session_state.clear_form = False
if "show_delete_account" not in st.session_state:
    st.session_state.show_delete_account = False

def display_header():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@500;700&display=swap');
        
        .header-container {
            background: linear-gradient(135deg, #444a54 0%, #212832 100%);
            padding: 20px 15px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
            text-align: left;
            margin-bottom: 20px;
            position: relative;
            overflow: hidden;
        }
        
        .logo-container {
            display: flex;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .logo-text-primary {
            font-family: 'Montserrat', sans-serif;
            font-size: 32px;
            font-weight: 700;
            color: #ffffff;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3), 0 0 10px rgba(255, 255, 255, 0.2);
            margin: 0;
            letter-spacing: 1px;
        }
        
        .logo-text-secondary {
            font-family: 'Montserrat', sans-serif;
            font-size: 24px;
            font-weight: 700;
            color: #ffffff;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3), 0 0 10px rgba(255, 255, 255, 0.2);
            margin-left: 10px;
            letter-spacing: 1px;
        }
        
        .logo-text-full {
            font-family: 'Montserrat', sans-serif;
            font-size: 20px;
            font-weight: 500;
            color: #ffffff;
            text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.3);
            margin-top: 5px;
            letter-spacing: 1px;
            display: block;
            text-align: right;
            padding-right: 10px;
        }
        
        /* 3D effect for text */
        .metallic-text {
            color: #f5f5f5;
            background: linear-gradient(180deg, #ffffff 0%, #c0c0c0 50%, #ffffff 100%);
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
            filter: drop-shadow(2px 2px 2px rgba(0, 0, 0, 0.5));
        }
        
        /* Media queries for responsiveness */
        @media (min-width: 768px) {
            .header-container {
                padding: 24px 20px;
                margin-bottom: 25px;
            }
            
            .logo-text-primary {
                font-size: 38px;
            }
            
            .logo-text-secondary {
                font-size: 30px;
            }
            
            .logo-text-full {
                font-size: 24px;
                padding-right: 20px;
            }
        }
        
        @media (max-width: 576px) {
            .logo-container {
                flex-direction: column;
                align-items: flex-start;
            }
            
            .logo-text-primary {
                font-size: 28px;
            }
            
            .logo-text-secondary {
                font-size: 20px;
                margin-left: 0;
                margin-top: 5px;
            }
            
            .logo-text-full {
                font-size: 18px;
                text-align: right;
                padding-right: 10px;
                margin-top: 8px;
                width: 100%;
            }
        }
        
        @media (max-width: 400px) {
            .header-container {
                padding: 15px 12px;
            }
            
            .logo-text-primary {
                font-size: 24px;
            }
            
            .logo-text-secondary {
                font-size: 18px;
            }
            
            .logo-text-full {
                font-size: 16px;
                text-align: right;
                width: 100%;
            }
        }
        </style>
        
        <div class="header-container">
            <div class="logo-container">
                <span class="logo-text-primary metallic-text">OEA</span>
                <span class="logo-text-secondary metallic-text">OrderEasy Analytics</span>
            </div>
            <span class="logo-text-full metallic-text">OrderEasy</span>
        </div>
        """,
        unsafe_allow_html=True
    )

# Helper functions for database operations
def load_users():
    response = supabase.table("users").select("*").execute()
    users = {row["username"]: {
        "password": row["password"],
        "organization": row["organization"],
        "is_admin": row["is_admin"]
    } for row in response.data}
    return users

def save_user(username, password, organization, is_admin=0):
    try:
        supabase.table("users").insert({
            "username": username,
            "password": password,
            "organization": organization,
            "is_admin": is_admin
        }).execute()
        return True
    except Exception as e:
        logger.error(f"Error saving user {username}: {e}")
        return False

def load_orders():
    response = supabase.table("orders").select("*").execute()
    df = pd.DataFrame(response.data)
    return df if not df.empty else pd.DataFrame(columns=[
        "order_id", "org", "receiver_name", "date", "expected_delivery_date",
        "product", "description", "quantity", "price", "basic_price", "gst",
        "advance_payment", "total_amount_with_gst", "pending_amount", "status", "created_by"
    ])

def save_orders(df):
    # Convert DataFrame to list of dictionaries
    data = df.to_dict(orient="records")
    # Delete existing records and insert new ones
    supabase.table("orders").delete().neq("order_id", -1).execute()  # Clear table
    if data:
        supabase.table("orders").insert(data).execute()

def load_ewaybills():
    response = supabase.table("ewaybills").select("*").execute()
    ewaybills = {f"{row['order_id']}_{row['org']}": {
        "public_id": row["public_id"],
        "url": row["url"],
        "file_name": row["file_name"],
        "upload_date": row["upload_date"],
        "resource_type": row["resource_type"] if row["resource_type"] else ("raw" if row["file_name"].lower().endswith(".pdf") else "image")
    } for row in response.data}
    return ewaybills

def save_ewaybill(order_id, org, public_id, url, file_name, upload_date, resource_type):
    supabase.table("ewaybills").upsert({
        "order_id": order_id,
        "org": org,
        "public_id": public_id,
        "url": url,
        "file_name": file_name,
        "upload_date": upload_date,
        "resource_type": resource_type
    }).execute()

# Authentication functions
def login(username, password):
    users = load_users()
    if username in users and users[username]["password"] == password:
        st.session_state.authenticated = True
        st.session_state.current_user = username
        st.session_state.current_org = users[username]["organization"]
        st.session_state.is_admin = (username == admin_username and password == admin_password)
        return True
    return False

def signup(username, password, organization):
    if username in load_users():
        return False
    
    password_pattern = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@₹!%*?&])[A-Za-z\d@₹!%*?&]{6,}₹"
    if not re.match(password_pattern, password):
        st.error("Password must be at least 6 characters long and contain at least one letter, one digit, and one special symbol (@₹!%*?&).")
        return False
    
    return save_user(username, password, organization)

def load_deliveries(order_id=None, org=None):
    query = supabase.table("deliveries").select("*")
    if order_id is not None and org is not None:
        query = query.eq("order_id", order_id).eq("org", org)
    response = query.execute()
    df = pd.DataFrame(response.data)
    return df if not df.empty else pd.DataFrame(columns=[
        "org", "delivery_id", "order_id", "delivery_quantity", "delivery_date",
        "total_amount_received", "public_id", "url", "file_name", "upload_date", "resource_type"
    ])


def delete_delivery(order_id, delivery_id):
    try:
        # Get delivery details
        delivery_response = supabase.table("deliveries").select("*").eq("order_id", order_id).eq("delivery_id", delivery_id).eq("org", st.session_state.current_org).execute()
        if not delivery_response.data:
            logger.error(f"Delivery {delivery_id} for order {order_id} not found")
            return False, "Delivery not found"

        delivery = delivery_response.data[0]
        delivery_quantity = delivery["delivery_quantity"]
        amount_received = delivery["total_amount_received"]
        public_id = delivery["public_id"]
        resource_type = delivery["resource_type"]

        # Validate delivery_quantity
        if delivery_quantity <= 0:
            logger.error(f"Invalid delivery quantity {delivery_quantity} for delivery {delivery_id}")
            return False, "Invalid delivery quantity"

        # Get order details before deleting delivery
        order_response = supabase.table("orders").select(
            "delivered_quantity, quantity, status, pending_amount, total_amount_with_gst, advance_payment"
        ).eq("order_id", order_id).eq("org", st.session_state.current_org).execute()
        if not order_response.data:
            logger.error(f"Order {order_id} not found for org {st.session_state.current_org}")
            return False, "Order not found"

        order = order_response.data[0]

        # Validate delivered_quantity
        if order["delivered_quantity"] < delivery_quantity:
            logger.error(
                f"Cannot delete delivery {delivery_id}: delivered_quantity {order['delivered_quantity']} "
                f"is less than delivery_quantity {delivery_quantity}"
            )
            return False, "Cannot delete delivery: Insufficient delivered quantity"

        # Delete Cloudinary file if exists
        if public_id:
            try:
                result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
                if result.get("result") == "ok":
                    logger.info(f"Deleted Cloudinary file: {public_id} (resource_type: {resource_type})")
                else:
                    logger.warning(f"Cloudinary file deletion issue: {public_id}, result: {result}")
            except Exception as e:
                logger.error(f"Error deleting Cloudinary file {public_id}: {e}")

        # Delete delivery from database
        supabase.table("deliveries").delete().eq("order_id", order_id).eq("delivery_id", delivery_id).eq("org", st.session_state.current_org).execute()

        # Calculate new delivered_quantity
        new_delivered_quantity = order["delivered_quantity"] - delivery_quantity

        # Recalculate pending_amount
        # Sum total_amount_received from remaining deliveries (excluding the deleted one)
        remaining_deliveries = supabase.table("deliveries").select("total_amount_received").eq("order_id", order_id).eq("org", st.session_state.current_org).execute()
        remaining_total_received = sum(d["total_amount_received"] for d in remaining_deliveries.data) if remaining_deliveries.data else 0
        new_pending_amount = order["total_amount_with_gst"] - order["advance_payment"] - remaining_total_received
        new_pending_amount = max(0, new_pending_amount)  # Prevent negative pending amount

        # Update status if necessary
        new_status = order["status"]
        if new_delivered_quantity < order["quantity"] and order["status"] == "Completed":
            new_status = "Pending"

        # Update order
        updates = {
            "delivered_quantity": new_delivered_quantity,
            "pending_amount": new_pending_amount,
            "status": new_status
        }
        supabase.table("orders").update(updates).eq("order_id", order_id).eq("org", st.session_state.current_org).execute()

        logger.info(
            f"Deleted delivery #{delivery_id} for order {order_id}. "
            f"Updated order: delivered_quantity={new_delivered_quantity}, "
            f"pending_amount={new_pending_amount:.2f}, status={new_status}"
        )
        return True, "Delivery deleted successfully"
    except Exception as e:
        logger.error(f"Error deleting delivery {delivery_id} for order {order_id}: {e}")
        return False, f"Error deleting delivery: {str(e)}"
def delete_account(username, by_admin=False):
    users = load_users()
    if username not in users:
        logger.error(f"User {username} not found for deletion")
        return False

    if by_admin and username == st.session_state.current_user:
        st.error("Admin cannot delete their own account via Admin Panel. Use Account Settings to delete your account.")
        return False

    org = users[username]["organization"]

    # Get order IDs for the organization
    response = supabase.table("orders").select("order_id").eq("org", org).execute()
    order_ids = [row["order_id"] for row in response.data]
    logger.info(f"Found {len(order_ids)} orders for organization {org}")

    # Delete Cloudinary files from deliveries
    deleted_files = 0
    for order_id in order_ids:
        deliveries = load_deliveries(order_id, org)
        for _, delivery in deliveries.iterrows():
            if delivery["public_id"]:
                try:
                    result = cloudinary.uploader.destroy(delivery["public_id"], resource_type=delivery["resource_type"])
                    if result.get("result") == "ok":
                        logger.info(f"Deleted Cloudinary file: {delivery['public_id']} (resource_type: {delivery['resource_type']})")
                        deleted_files += 1
                    else:
                        logger.warning(f"Cloudinary file deletion issue: {delivery['public_id']}, result: {result}")
                except Exception as e:
                    logger.error(f"Error deleting Cloudinary file {delivery['public_id']}: {e}")

    # Delete from database
    try:
        supabase.table("deliveries").delete().eq("org", org).execute()
        logger.info(f"Deleted deliveries for org {org}")
        supabase.table("ewaybills").delete().eq("org", org).execute()
        logger.info(f"Deleted e-way bills for org {org}")
        supabase.table("orders").delete().eq("org", org).execute()
        logger.info(f"Deleted orders for org {org}")
        supabase.table("users").delete().eq("username", username).execute()
        logger.info(f"Deleted user {username}")
    except Exception as e:
        logger.error(f"Database deletion error: {e}")
        return False

    # Verify Cloudinary cleanup
    try:
        for resource_type in ["raw", "image"]:
            resources = cloudinary.api.resources(prefix=f"delivery_{org}_", resource_type=resource_type)
            remaining_files = resources.get("resources", [])
            if remaining_files:
                logger.warning(f"Found {len(remaining_files)} remaining Cloudinary {resource_type} files for org {org}: {[r['public_id'] for r in remaining_files]}")
            else:
                logger.info(f"No remaining Cloudinary {resource_type} files for org {org}")
    except Exception as e:
        logger.error(f"Error verifying Cloudinary cleanup for org {org}: {e}")

    if not by_admin:
        st.session_state.authenticated = False
        st.session_state.current_user = None
        st.session_state.current_org = None
        st.session_state.is_admin = False

    logger.info(f"Account deletion completed for {username}. Deleted {deleted_files} Cloudinary files")
    return True

def logout():
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.session_state.current_org = None
    st.session_state.is_admin = False
    st.session_state.form_submitted = False
    st.session_state.form_message = ""
    st.session_state.form_status = ""
    st.session_state.editing_order = None
    st.session_state.show_delete_account = False
def add_order(receiver_name, date, expected_delivery_date, product, description, quantity, price, gst, advance_payment):
    orders = load_orders()
    
    basic_price = quantity * price
    gst_amount = basic_price * (gst / 100)
    total_amount_with_gst = basic_price + gst_amount
    pending_amount = total_amount_with_gst - advance_payment
    
    org_orders = get_org_orders()
    order_id = 1 if org_orders.empty else org_orders["order_id"].max() + 1
    
    new_order = {
        "order_id": int(order_id),  # Convert to Python int
        "org": st.session_state.current_org,
        "receiver_name": receiver_name,
        "date": str(date),
        "expected_delivery_date": str(expected_delivery_date),
        "product": product,
        "description": description,
        "quantity": int(quantity),  # Convert to Python int
        "price": float(price),  # Convert to Python float
        "basic_price": float(basic_price),  # Convert to Python float
        "gst": float(gst),  # Convert to Python float
        "advance_payment": float(advance_payment),  # Convert to Python float
        "total_amount_with_gst": float(total_amount_with_gst),  # Convert to Python float
        "pending_amount": float(pending_amount),  # Convert to Python float
        "status": "Pending",
        "created_by": st.session_state.current_user
    }
    
    supabase.table("orders").insert(new_order).execute()
    
    st.session_state.form_submitted = True
    st.session_state.form_message = "Order added successfully!"
    st.session_state.form_status = "success"
    st.session_state.clear_form = True
    logger.info(f"Added order {order_id} for org {st.session_state.current_org}")
    return True
# Order management functions
def add_delivery(order_id, delivery_quantity, delivery_date, total_amount_received, file_data=None, file_name=None):
    try:
        # Fetch order details including advance_payment and pending_amount
        order_response = supabase.table("orders").select(
            "quantity, delivered_quantity, status, pending_amount, total_amount_with_gst, advance_payment"
        ).eq("order_id", order_id).eq("org", st.session_state.current_org).execute()
        if not order_response.data:
            logger.error(f"Order {order_id} not found")
            return False, "Order not found"

        order = order_response.data[0]
        total_quantity = order["quantity"]
        current_delivered = order["delivered_quantity"]
        advance_payment = order["advance_payment"]
        order_total_amount = order["total_amount_with_gst"]

        new_delivered = current_delivered + delivery_quantity

        if new_delivered > total_quantity:
            logger.error(f"Delivery quantity exceeds order quantity: {new_delivered} > {total_quantity}")
            return False, f"Delivery quantity ({delivery_quantity}) would exceed order quantity ({total_quantity - current_delivered})."

        # Validate total_amount_received
        if total_amount_received < 0:
            logger.error(f"Total amount received cannot be negative: {total_amount_received}")
            return False, f"Total amount received cannot be negative."

        # Calculate current total received from previous deliveries
        deliveries = load_deliveries(order_id, st.session_state.current_org)
        previous_total_received = deliveries["total_amount_received"].sum() if not deliveries.empty else 0

        # Calculate effective pending amount before this delivery
        effective_pending = order_total_amount - advance_payment - previous_total_received
        if effective_pending < 0:
            effective_pending = 0  # Prevent negative pending amount due to overpayment

        # Update pending amount
        new_pending = effective_pending - total_amount_received

        # Calculate next delivery_id for this order and org
        max_delivery_id_response = supabase.table("deliveries").select("delivery_id").eq("order_id", order_id).eq("org", st.session_state.current_org).order("delivery_id", desc=True).limit(1).execute()
        next_delivery_id = 1 if not max_delivery_id_response.data else max_delivery_id_response.data[0]["delivery_id"] + 1

        public_id = None
        url = None
        resource_type = None
        upload_date = None

        if file_data and file_name:
            file_ext = file_name.split(".")[-1].lower()
            resource_type = "raw" if file_ext == "pdf" else "image"
            public_id = f"delivery_{st.session_state.current_org}_{order_id}_{uuid.uuid4()}"
            
            upload_result = cloudinary.uploader.upload(
                file_data,
                public_id=public_id,
                resource_type=resource_type,
                access_mode="public",
                type="upload"
            )
            
            resource_info = cloudinary.api.resource(public_id, resource_type=resource_type)
            if resource_info.get("access_mode") != "public":
                cloudinary.uploader.explicit(
                    public_id,
                    type="upload",
                    resource_type=resource_type,
                    access_mode="public"
                )
            
            url = upload_result["secure_url"]
            upload_date = datetime.datetime.now().isoformat()

        # Insert delivery with payment details
        delivery_data = {
            "org": st.session_state.current_org,
            "delivery_id": next_delivery_id,
            "order_id": order_id,
            "delivery_quantity": int(delivery_quantity),
            "delivery_date": str(delivery_date),
            "total_amount_received": float(total_amount_received),
            "public_id": public_id,
            "url": url,
            "file_name": file_name,
            "upload_date": upload_date,
            "resource_type": resource_type
        }
        supabase.table("deliveries").insert(delivery_data).execute()

        # Update order's delivered_quantity and pending_amount
        updates = {
            "delivered_quantity": new_delivered,
            "pending_amount": new_pending
        }
        if new_delivered >= total_quantity and order["status"] != "Completed":
            updates["status"] = "Completed"
            updates["pending_amount"] = 0.0
            # Verify total amount received (including advance) matches order total
            total_received = previous_total_received + total_amount_received + advance_payment
            
        supabase.table("orders").update(updates).eq("order_id", order_id).eq("org", st.session_state.current_org).execute()

        logger.info(f"Added delivery #{next_delivery_id} of {delivery_quantity} units for order {order_id}, amount received: ₹{total_amount_received:.2f}, new pending: ₹{new_pending:.2f}")
        return True, "Delivery added successfully"
    except Exception as e:
        logger.error(f"Error adding delivery for order {order_id}: {e}")
        return False, f"Error adding delivery: {str(e)}"
def export_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def update_order_status(order_id, new_status):
    supabase.table("orders").update({"status": new_status}).eq("order_id", order_id).eq("org", st.session_state.current_org).execute()
    logger.info(f"Updated status of order {order_id} to {new_status}")

def upload_ewaybill(order_id, file_data, file_name):
    try:
        file_ext = file_name.split(".")[-1].lower()
        resource_type = "raw" if file_ext == "pdf" else "image"
        public_id = f"ewaybill_{st.session_state.current_org}_{order_id}_{uuid.uuid4()}"
        
        upload_result = cloudinary.uploader.upload(
            file_data,
            public_id=public_id,
            resource_type=resource_type,
            access_mode="public",
            type="upload"
        )
        
        resource_info = cloudinary.api.resource(public_id, resource_type=resource_type)
        if resource_info.get("access_mode") != "public":
            cloudinary.uploader.explicit(
                public_id,
                type="upload",
                resource_type=resource_type,
                access_mode="public"
            )
            resource_info = cloudinary.api.resource(public_id, resource_type=resource_type)
        
        secure_url = upload_result["secure_url"]
        try:
            response = requests.get(secure_url, timeout=5)
            response.raise_for_status()
            logger.info(f"Uploaded e-way bill for order {order_id}, public_id: {public_id}, url: {secure_url}, resource_type: {resource_type}")
        except requests.RequestException as e:
            logger.error(f"Uploaded file {public_id} not accessible: {e}")
            return False
        
        save_ewaybill(
            order_id=order_id,
            org=st.session_state.current_org,
            public_id=public_id,
            url=secure_url,
            file_name=file_name,
            upload_date=datetime.datetime.now().isoformat(),
            resource_type=resource_type
        )
        
        return True
    except Exception as e:
        logger.error(f"Error uploading e-way bill for order {order_id}: {e}")
        return False


def delete_order(order_id):
    try:
        # Get deliveries for the order
        deliveries = load_deliveries(order_id, st.session_state.current_org)

        # Delete Cloudinary files for deliveries
        for _, delivery in deliveries.iterrows():
            if delivery["public_id"]:
                try:
                    result = cloudinary.uploader.destroy(delivery["public_id"], resource_type=delivery["resource_type"])
                    if result.get("result") == "ok":
                        logger.info(
                            f"Deleted Cloudinary delivery file: {delivery['public_id']} (resource_type: {delivery['resource_type']})")
                    else:
                        logger.warning(
                            f"Cloudinary delivery file deletion issue: {delivery['public_id']}, result: {result}")
                except Exception as e:
                    logger.error(f"Error deleting Cloudinary delivery file {delivery['public_id']}: {e}")

        # Delete deliveries from database
        supabase.table("deliveries").delete().eq("order_id", order_id).eq("org", st.session_state.current_org).execute()
        logger.info(f"Deleted all deliveries for order {order_id}")

        # Delete order-specific e-way bill if exists
        ewaybill_response = supabase.table("ewaybills").select("*").eq("order_id", order_id).eq("org",
                                                                                                st.session_state.current_org).execute()
        if ewaybill_response.data:
            ewaybill = ewaybill_response.data[0]
            if ewaybill["public_id"]:
                try:
                    result = cloudinary.uploader.destroy(ewaybill["public_id"], resource_type=ewaybill["resource_type"])
                    if result.get("result") == "ok":
                        logger.info(
                            f"Deleted Cloudinary e-way bill: {ewaybill['public_id']} (resource_type: {ewaybill['resource_type']})")
                    else:
                        logger.warning(
                            f"Cloudinary e-way bill deletion issue: {ewaybill['public_id']}, result: {result}")
                except Exception as e:
                    logger.error(f"Error deleting Cloudinary e-way bill {ewaybill['public_id']}: {e}")

        # Delete e-way bill from database
        supabase.table("ewaybills").delete().eq("order_id", order_id).eq("org", st.session_state.current_org).execute()
        logger.info(f"Deleted e-way bill for order {order_id}")

        # Delete the order
        supabase.table("orders").delete().eq("order_id", order_id).eq("org", st.session_state.current_org).execute()
        logger.info(f"Deleted order {order_id}")

        st.session_state.form_submitted = True
        st.session_state.form_message = f"Order #{order_id} and all associated data deleted successfully!"
        st.session_state.form_status = "success"
        return True
    except Exception as e:
        logger.error(f"Error deleting order {order_id}: {e}")
        st.session_state.form_submitted = True
        st.session_state.form_message = f"Error deleting order: {str(e)}"
        st.session_state.form_status = "error"
        return False

def edit_order(order_id, receiver_name, date, expected_delivery_date, product, description, quantity, price, gst, advance_payment):
    # Check if new quantity is valid
    order_response = supabase.table("orders").select("delivered_quantity").eq("order_id", order_id).eq("org", st.session_state.current_org).execute()
    if order_response.data:
        delivered_quantity = order_response.data[0]["delivered_quantity"]
        if quantity < delivered_quantity:
            logger.error(f"Cannot reduce quantity below delivered amount: {quantity} < {delivered_quantity}")
            return False
    
    basic_price = quantity * price
    gst_amount = basic_price * (gst / 100)
    total_amount_with_gst = basic_price + gst_amount
    pending_amount = total_amount_with_gst - advance_payment
    
    response = supabase.table("orders").select("*").eq("order_id", order_id).eq("org", st.session_state.current_org).execute()
    if response.data:
        supabase.table("orders").update({
            "receiver_name": receiver_name,
            "date": str(date),
            "expected_delivery_date": str(expected_delivery_date),
            "product": product,
            "description": description,
            "quantity": quantity,
            "price": price,
            "basic_price": basic_price,
            "gst": gst,
            "advance_payment": advance_payment,
            "total_amount_with_gst": total_amount_with_gst,
            "pending_amount": pending_amount
        }).eq("order_id", order_id).eq("org", st.session_state.current_org).execute()
        logger.info(f"Order {order_id} updated successfully")
        return True
    logger.warning(f"Order {order_id} not found for editing")
    return False
def clear_form_feedback():
    st.session_state.form_submitted = False
    st.session_state.form_message = ""
    st.session_state.form_status = ""

def get_org_orders():
    response = supabase.table("orders").select("*").eq("org", st.session_state.current_org).execute()
    df = pd.DataFrame(response.data)
    return df if not df.empty else pd.DataFrame(columns=[
        "order_id", "org", "receiver_name", "date", "expected_delivery_date",
        "product", "description", "quantity", "price", "basic_price", "gst",
        "advance_payment", "total_amount_with_gst", "pending_amount", "status", "created_by"
    ])

# Analytics functions

def get_total_revenue(df):
    if df.empty:
        return 0
    # Calculate total revenue as advance_payment + sum of total_amount_received from deliveries
    revenue = 0
    for _, row in df.iterrows():
        deliveries = load_deliveries(row["order_id"], row["org"])
        delivery_amount = deliveries["total_amount_received"].sum() if not deliveries.empty else 0
        revenue += row["advance_payment"] + delivery_amount
    return revenue

def get_monthly_summary(df):
    if df.empty:
        return {"total": 0, "completed": 0, "pending": 0, "revenue": 0, "avg_order_value": 0, "mom_growth": 0}
    
    current_month = datetime.datetime.now().month
    current_year = datetime.datetime.now().year
    
    df["date"] = pd.to_datetime(df["date"])
    monthly_df = df[(df["date"].dt.month == current_month) & (df["date"].dt.year == current_year)]
    
    # Calculate revenue for the current month
    monthly_revenue = 0
    monthly_order_count = len(monthly_df)
    for _, row in monthly_df.iterrows():
        deliveries = load_deliveries(row["order_id"], row["org"])
        delivery_amount = deliveries["total_amount_received"].sum() if not deliveries.empty else 0
        monthly_revenue += row["advance_payment"] + delivery_amount
    
    result = {
        "total": monthly_order_count,
        "completed": len(monthly_df[monthly_df["status"] == "Completed"]),
        "pending": len(monthly_df[monthly_df["status"] == "Pending"]),
        "revenue": monthly_revenue,
        "avg_order_value": monthly_revenue / monthly_order_count if monthly_order_count > 0 else 0
    }
    
    # Calculate revenue for the previous month
    last_month = current_month - 1 if current_month > 1 else 12
    last_month_year = current_year if current_month > 1 else current_year - 1
    last_month_df = df[(df["date"].dt.month == last_month) & (df["date"].dt.year == last_month_year)]
    
    last_month_revenue = 0
    for _, row in last_month_df.iterrows():
        deliveries = load_deliveries(row["order_id"], row["org"])
        delivery_amount = deliveries["total_amount_received"].sum() if not deliveries.empty else 0
        last_month_revenue += row["advance_payment"] + delivery_amount
    
    if last_month_revenue > 0 and monthly_revenue > 0:
        result["mom_growth"] = ((monthly_revenue - last_month_revenue) / last_month_revenue * 100)
    else:
        result["mom_growth"] = 0
    
    return result

# UI Components
def show_login_page():
    display_header()
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Login")
            
            if submit_button:
                if login(username, password):
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    
    with tab2:
        with st.form("signup_form"):
            new_username = st.text_input("New Username")
            new_password = st.text_input("New Password", type="password")
            organization = st.text_input("Organization Name")
            signup_button = st.form_submit_button("Sign Up")
            
            if signup_button:
                if new_username and new_password and organization:
                    if signup(new_username, new_password, organization):
                        st.success("Sign up successful! You can now login.")
                    else:
                        st.error("Username already exists")
                else:
                    st.error("Please fill in all fields")

def show_sidebar():
    display_header()
    
    st.sidebar.title(f"Organization: {st.session_state.current_org}")
    st.sidebar.write(f"Logged in as: {st.session_state.current_user}")
    if st.session_state.is_admin:
        st.sidebar.write("Role: Admin")
    
    menu_options = ["Dashboard", "Add Order", "Manage Orders", "Export Reports", "Account Settings"]
    if st.session_state.is_admin:
        menu_options.append("Admin Panel")
    
    menu = st.sidebar.radio("Navigation", menu_options)
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Logout"):
            logout()
            st.rerun()
    
    with col2:
        if st.button("Delete Account"):
            st.session_state.show_delete_account = True
            st.rerun()
            
    if st.session_state.show_delete_account:
        st.sidebar.warning("Are you sure you want to delete your account? This action cannot be undone!")
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("Yes, Delete"):
                if delete_account(st.session_state.current_user):
                    st.success("Account deleted successfully!")
                    st.rerun()
        with col2:
            if st.button("Cancel"):
                st.session_state.show_delete_account = False
                st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Contact Us")
    st.sidebar.write("📧 krishchaudhary144@gmail.com")
    st.sidebar.write("📞 +91 6353160662")
        
    return menu

def show_admin_panel():
    
    st.title("Admin Panel")
    
    if not st.session_state.is_admin:
        st.error("Access denied. Admin privileges required.")
        return
    
    st.subheader("User Management")
    
    users = load_users()
    if not users:
        st.info("No users found.")
        return
    
    user_data = [{"Username": k, "Organization": v["organization"]} for k, v in users.items()]
    user_df = pd.DataFrame(user_data)
    
    st.write("**All Users**")
    st.dataframe(user_df)
    
    st.subheader("Delete User")
    selected_user = st.selectbox("Select User to Delete", options=[u["Username"] for u in user_data if u["Username"] != st.session_state.current_user])
    
    if st.button("Delete Selected User"):
        if selected_user:
            if delete_account(selected_user, by_admin=True):
                st.success(f"User {selected_user} deleted successfully!")
                st.rerun()
            else:
                st.error(f"Failed to delete user {selected_user}.")
        else:
            st.error("Please select a user to delete.")

def show_add_order():
    
    
    st.title("Add Order")
    
    with st.form("add_order_form"):
        receiver_name = st.text_input("Receiver Name")
        date = st.date_input("Order Date", value=datetime.date.today())
        expected_delivery_date = st.date_input("Expected Delivery Date", value=datetime.date.today())
        product = st.text_input("Product")
        description = st.text_area("Description (Optional)")
        
        col1, col2 = st.columns(2)
        with col1:
            quantity = st.number_input("Quantity", min_value=1, value=1)
        with col2:
            price = st.number_input("Price per Unit (₹)", min_value=0.01, value=0.01, step=0.01)
        
        basic_price = quantity * price
        st.write(f"**Basic Price: ₹{basic_price:.2f}**")
        
        col1, col2 = st.columns(2)
        with col1:
            gst = st.number_input("GST (%)", min_value=0.0, value=0.0, step=0.1)
        with col2:
            advance_payment = st.number_input("Advance Payment (₹)", min_value=0.0, value=0.0, step=0.01)
        
        total_amount_with_gst = basic_price + (basic_price * (gst / 100))
        pending_amount = total_amount_with_gst - advance_payment
        
        st.write(f"**Total Amount with GST: ₹{total_amount_with_gst:.2f}**")
        st.write(f"**Pending Amount: ₹{pending_amount:.2f}**")
        
        submitted = st.form_submit_button("Add Order")
        
        if submitted:
            if receiver_name and product:
                if add_order(receiver_name, date, expected_delivery_date, product, description, 
                            quantity, price, gst, advance_payment):
                    st.success("Order added successfully!")
                    st.rerun()
            else:
                st.error("Receiver Name and Product are required fields!")
    
    if st.session_state.form_submitted and st.session_state.clear_form:
        st.session_state.clear_form = False
        st.rerun()

def show_dashboard():
    
    st.title("Dashboard")
    
    org_orders = get_org_orders()
    
    if org_orders.empty:
        st.info("No orders yet. Add some orders to see your dashboard.")
        return
    
    org_orders["date"] = pd.to_datetime(org_orders["date"])
    org_orders["expected_delivery_date"] = pd.to_datetime(org_orders["expected_delivery_date"])
    
    monthly_summary = get_monthly_summary(org_orders)
    
    FIGURE_WIDTH = 10
    FIGURE_HEIGHT = 6

    st.subheader("All-Time Metrics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Orders (All Time)", len(org_orders))
    with col2:
        st.metric("Completed Orders", len(org_orders[org_orders["status"] == "Completed"]))
    with col3:
        st.metric("Pending Orders", len(org_orders[org_orders["status"] == "Pending"]))
    with col4:
        total_delivered = org_orders["delivered_quantity"].sum()
        st.metric("Total Units Delivered", total_delivered)
    
    st.subheader("Current Month Metrics")
    current_month = datetime.datetime.now().month
    current_year = datetime.datetime.now().year
    monthly_df = org_orders[(org_orders["date"].dt.month == current_month) & (org_orders["date"].dt.year == current_year)]
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Orders (This Month)", len(monthly_df))
    with col2:
        st.metric("Completed Orders", len(monthly_df[monthly_df["status"] == "Completed"]))
    with col3:
        st.metric("Pending Orders", len(monthly_df[monthly_df["status"] == "Pending"]))
    with col4:
        monthly_delivered = monthly_df["delivered_quantity"].sum()
        st.metric("Units Delivered", monthly_delivered)
    
    st.subheader("📦 Quantity Analysis")
    org_orders["month"] = pd.to_datetime(org_orders["date"]).dt.strftime("%b %Y")
    monthly_quantity = org_orders.groupby("month")["quantity"].sum().reset_index(name="monthly_quantity")
    monthly_quantity['month_dt'] = pd.to_datetime(monthly_quantity['month'], format="%b %Y")
    monthly_quantity = monthly_quantity.sort_values('month_dt').drop(columns='month_dt')
    
    if len(monthly_quantity) > 1:
        fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
        sns.lineplot(data=monthly_quantity, x="month", y="monthly_quantity", marker="o", ax=ax)
        ax.set_xlabel("Month")
        ax.set_ylabel("Monthly Quantity")
        ax.set_title("Monthly Quantity Trend")
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
    st.subheader("📅 Year-wise Revenue")
    # Calculate revenue for each order
    org_orders["revenue"] = 0.0
    for idx, row in org_orders.iterrows():
        deliveries = load_deliveries(row["order_id"], row["org"])
        delivery_amount = deliveries["total_amount_received"].sum() if not deliveries.empty else 0
        org_orders.at[idx, "revenue"] = row["advance_payment"] + delivery_amount
    
    # Extract year from date and group by year
    org_orders["year"] = org_orders["date"].dt.year
    yearly_revenue = org_orders.groupby("year")["revenue"].sum().reset_index()
    yearly_revenue = yearly_revenue.sort_values("year", ascending=False)  # Sort in decreasing order
    yearly_revenue["year"] = yearly_revenue["year"].astype(str)
    
    # Create dropdown for selecting year
    if not yearly_revenue.empty:
        selected_year = st.selectbox("Select Year for Revenue Details", 
                                     options=yearly_revenue["year"].tolist(), 
                                     key="year_wise_revenue")
        
        # Display revenue for the selected year
        selected_revenue = yearly_revenue[yearly_revenue["year"] == selected_year]["revenue"].iloc[0]
        st.metric(f"Revenue for {selected_year}", f"₹{selected_revenue:.2f}")
        
        # Display table of yearly revenue
        st.write("**Year-wise Revenue Summary**")
        yearly_revenue_display = yearly_revenue[["year", "revenue"]].rename(
            columns={"year": "Year", "revenue": "Total Revenue (₹)"}
        )
        yearly_revenue_display["Total Revenue (₹)"] = yearly_revenue_display["Total Revenue (₹)"].map(
            lambda x: f"{x:.2f}"
        )
        st.dataframe(yearly_revenue_display)
    else:
        st.info("No revenue data available for any year.")
    st.subheader("📈 Revenue and Financial Analysis")
    org_orders["month"] = pd.to_datetime(org_orders["date"]).dt.strftime("%b %Y")
    # Calculate revenue as advance_payment + total_amount_received from deliveries
    org_orders["revenue"] = 0.0
    for idx, row in org_orders.iterrows():
        deliveries = load_deliveries(row["order_id"], row["org"])
        delivery_amount = deliveries["total_amount_received"].sum() if not deliveries.empty else 0
        org_orders.at[idx, "revenue"] = row["advance_payment"] + delivery_amount
    
    monthly_revenue = org_orders.groupby("month")["revenue"].sum().reset_index()
    monthly_revenue['month_dt'] = pd.to_datetime(monthly_revenue['month'], format="%b %Y")
    monthly_revenue = monthly_revenue.sort_values('month_dt').drop(columns='month_dt')
    
    if len(monthly_revenue) >= 2:
        current_revenue = monthly_revenue["revenue"].iloc[-1]
        previous_revenue = monthly_revenue["revenue"].iloc[-2]
        delta = ((current_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Revenue", f"₹{org_orders['revenue'].sum():.2f}", 
                      f"{delta:.1f}% from previous month")
        with col2:
            avg_order_value = org_orders["revenue"].mean()
            st.metric("Average Order Value", f"₹{avg_order_value:.2f}")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Revenue", f"₹{org_orders['revenue'].sum():.2f}")
        with col2:
            avg_order_value = org_orders["revenue"].mean()
            st.metric("Average Order Value", f"₹{avg_order_value:.2f}")
    
    if len(monthly_revenue) > 1:
        fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
        sns.lineplot(data=monthly_revenue, x="month", y="revenue", marker="o", ax=ax)
        ax.set_xlabel("Month")
        ax.set_ylabel("Revenue (₹)")
        ax.set_title("Monthly Revenue Trend")
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
    
    st.subheader("👥 Receiver Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        receiver_quantity = org_orders.groupby("receiver_name")["quantity"].sum().reset_index()
        receiver_quantity = receiver_quantity.sort_values("quantity", ascending=False).head(5)
        fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
        sns.barplot(data=receiver_quantity, x="quantity", y="receiver_name", ax=ax, palette="Blues_d")
        ax.set_xlabel("Total Quantity")
        ax.set_ylabel("Receiver")
        ax.set_title("Top Receivers by Quantity")
        for i, v in enumerate(receiver_quantity["quantity"]):
            ax.text(v, i, f"{v}", va="center")
        plt.tight_layout()
        st.pyplot(fig)
    
    with col2:
        receiver_revenue = org_orders.groupby("receiver_name")["revenue"].sum().reset_index()
        receiver_revenue = receiver_revenue.sort_values("revenue", ascending=False).head(10)
        fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
        sns.barplot(data=receiver_revenue, x="revenue", y="receiver_name", ax=ax, palette="Greens_d")
        ax.set_xlabel("Total Revenue (₹)")
        ax.set_ylabel("Receiver")
        ax.set_title("Top Receivers by Revenue")
        for i, v in enumerate(receiver_revenue["revenue"]):
            ax.text(v, i, f"₹{v:.2f}", va="center")
        plt.tight_layout()
        st.pyplot(fig)
    
    st.subheader("📦 Product Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        product_quantity = org_orders.groupby("product")["quantity"].sum().reset_index()
        product_quantity = product_quantity.sort_values("quantity", ascending=False).head(10)
        fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
        sns.barplot(data=product_quantity, x="quantity", y="product", ax=ax, palette="Oranges_d")
        ax.set_xlabel("Total Quantity")
        ax.set_ylabel("Product")
        ax.set_title("Top Products by Quantity")
        for i, v in enumerate(product_quantity["quantity"]):
            ax.text(v, i, f"{v}", va="center")
        plt.tight_layout()
        st.pyplot(fig)
    
    with col2:
        product_revenue = org_orders.groupby("product")["revenue"].sum().reset_index()
        product_revenue = product_revenue.sort_values("revenue", ascending=False).head(5)
        fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
        sns.barplot(data=product_revenue, x="revenue", y="product", ax=ax, palette="Purples_d")
        ax.set_xlabel("Total Revenue (₹)")
        ax.set_ylabel("Product")
        ax.set_title("Top Products by Revenue")
        for i, v in enumerate(product_revenue["revenue"]):
            ax.text(v, i, f"₹{v:.2f}", va="center")
        plt.tight_layout()
        st.pyplot(fig)
    
    st.subheader("👥 Advanced Customer Analysis")
    col1, col2 = st.columns(2)
    with col1:
      st.subheader("Customer Lifetime Value")
      customer_metrics = org_orders.groupby("receiver_name").agg({
        "total_amount_with_gst": ["sum", "count"],
        "date": "min"
      }).reset_index()
      customer_metrics.columns = ["receiver_name", "total_spent", "order_count", "first_order"]
      customer_metrics["customer_age"] = (datetime.datetime.now() - customer_metrics["first_order"]).dt.days / 30
      customer_metrics["clv"] = customer_metrics["total_spent"] / customer_metrics["customer_age"].replace(0, 1)
      top_clv = customer_metrics.sort_values("clv", ascending=False).head(5)
      if not top_clv.empty:
        fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
        # Ensure the order matches the sorted DataFrame
        sns.barplot(data=top_clv, x="clv", y="receiver_name", ax=ax, palette="Blues_d", order=top_clv["receiver_name"])
        ax.invert_xaxis()  # Invert the x-axis to plot bars from right to left
        ax.set_xlabel("Customer Lifetime Value (₹/month)")
        ax.set_ylabel("Receiver")
        ax.set_title("Top Customers by Lifetime Value")
        for i, v in enumerate(top_clv["clv"]):
            # Corrected ax.text() call: x, y, string, and formatting
            ax.text(x=v * 0.95, y=i, s=f"₹{v:.2f}", va="center", ha="right")  # Position text slightly inside the bar
        plt.tight_layout()
        st.pyplot(fig)
    with col2:
        st.subheader("Customer Retention")
        customer_orders = org_orders.groupby(["receiver_name", org_orders["date"].dt.to_period("M")]).size().reset_index(name="orders")
        repeat_customers = customer_orders.groupby("receiver_name").size()
        repeat_rate = (sum(repeat_customers > 1) / len(repeat_customers)) * 100 if len(repeat_customers) > 0 else 0
        st.metric("Repeat Customer Rate", f"{repeat_rate:.1f}%")
        monthly_retention = customer_orders.groupby("date")["receiver_name"].nunique().reset_index()
        monthly_retention["date"] = monthly_retention["date"].astype(str)
        if len(monthly_retention) > 1:
            fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
            sns.lineplot(data=monthly_retention, x="date", y="receiver_name", marker="o", ax=ax)
            ax.set_xlabel("Month")
            ax.set_ylabel("Unique Customers")
            ax.set_title("Customer Retention Trend")
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
    
    st.subheader("📦 Advanced Product Analysis")
    st.subheader("Product Demand Trends")
    product_trends = org_orders.groupby(["product", org_orders["date"].dt.to_period("M")])["quantity"].sum().reset_index()
    product_trends["date"] = product_trends["date"].astype(str)
    top_products = org_orders["product"].value_counts().head(3).index
    product_trends = product_trends[product_trends["product"].isin(top_products)]
    if not product_trends.empty:
        fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
        sns.lineplot(data=product_trends, x="date", y="quantity", hue="product", marker="o", ax=ax)
        ax.set_xlabel("Month")
        ax.set_ylabel("Quantity Sold")
        ax.set_title("Top Products Demand Trend")
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
    
    st.subheader("📈 Advanced Time Series Analysis")
    if not org_orders.empty:
        org_orders["month_period"] = org_orders["date"].dt.to_period("M")
        monthly_metrics = org_orders.groupby("month_period").agg({
            "revenue": "sum",
            "quantity": "sum",
            "pending_amount": "sum"
        }).reset_index()
        monthly_metrics = monthly_metrics.sort_values("month_period")
        monthly_metrics["month_period"] = monthly_metrics["month_period"].astype(str)
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(FIGURE_WIDTH, 12), sharex=True)
        sns.lineplot(data=monthly_metrics, x="month_period", y="revenue", marker="o", ax=ax1, color="blue")
        ax1.set_title("Monthly Revenue Trend")
        ax1.set_ylabel("Revenue (₹)")
        ax1.grid(True)
        sns.lineplot(data=monthly_metrics, x="month_period", y="quantity", marker="o", ax=ax2, color="green")
        ax2.set_title("Monthly Quantity Sold")
        ax2.set_ylabel("Units")
        ax2.grid(True)
        sns.lineplot(data=monthly_metrics, x="month_period", y="pending_amount", marker="o", ax=ax3, color="red")
        ax3.set_title("Monthly Pending Amount")
        ax3.set_xlabel("Month")
        ax3.set_ylabel("Pending (₹)")
        ax3.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
    
    st.subheader("🔮 Advanced Sales Forecasting")
    if len(org_orders) >= 10:
        org_orders["date_only"] = org_orders["date"].dt.date
        daily_sales = org_orders.groupby("date_only")["revenue"].sum().reset_index()
        daily_sales["day_number"] = range(1, len(daily_sales) + 1)
        
        try:
            X = daily_sales["day_number"].values.reshape(-1, 1)
            y = daily_sales["revenue"].values
            model = LinearRegression()
            model.fit(X, y)
            
            predictions = model.predict(X)
            
            residuals = y - predictions
            mse = np.mean(residuals**2)
            confidence_level = 0.95
            t_value = stats.t.ppf((1 + confidence_level) / 2, len(X) - 2)
            X_mean = np.mean(X)
            X_var = np.sum((X - X_mean)**2)
            ci_se = np.sqrt(mse * (1 + 1/len(X) + (X - X_mean)**2/X_var)).flatten()
            ci = t_value * ci_se
            
            future_days = np.array(range(len(daily_sales) + 1, len(daily_sales) + 15)).reshape(-1, 1)
            future_predictions = model.predict(future_days)
            future_ci_se = np.sqrt(mse * (1 + 1/len(X) + (future_days - X_mean)**2/X_var)).flatten()
            future_ci = t_value * future_ci_se
            
            all_days = np.concatenate([X, future_days]).flatten()
            all_predictions = np.concatenate([predictions, future_predictions])
            all_ci_lower = np.concatenate([predictions - ci, future_predictions - future_ci])
            all_ci_upper = np.concatenate([predictions + ci, future_predictions + future_ci])
            
            fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
            ax.plot(X.flatten(), y, "o-", label="Actual Sales")
            ax.plot(future_days.flatten(), future_predictions, "o--", color="red", label="Forecast")
            ax.fill_between(all_days, all_ci_lower, all_ci_upper, color="red", alpha=0.1, label="95% CI")
            ax.set_xlabel("Day")
            ax.set_ylabel("Sales (₹)")
            ax.set_title("14-Day Sales Forecast with Confidence Intervals")
            ax.legend()
            plt.tight_layout()
            st.pyplot(fig)
            
            weekly_forecast = sum(future_predictions[:7])
            two_week_forecast = sum(future_predictions)
            st.metric("Predicted 7-Day Revenue", f"₹{weekly_forecast:.2f}")
            st.metric("Predicted 14-Day Revenue", f"₹{two_week_forecast:.2f}")
            r_squared = model.score(X, y)
            st.metric("Forecast Reliability (R²)", f"{r_squared:.2f}")
        except Exception as e:
            st.error(f"Could not create forecast: {str(e)}")
    else:
        st.info("Need at least 10 orders to create a sales forecast.")
    
    st.subheader("📊 Advanced Order Status Analysis")
    status_metrics = org_orders.groupby("status").agg({
        "pending_amount": "sum",
        "revenue": "sum",
        "quantity": "sum"
    }).reset_index()
    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
        sns.barplot(data=status_metrics, x="status", y="pending_amount", ax=ax, palette="Reds_d")
        ax.set_xlabel("Order Status")
        ax.set_ylabel("Pending Amount (₹)")
        ax.set_title("Pending Amount by Status")
        for i, v in enumerate(status_metrics["pending_amount"]):
            ax.text(i, v, f"₹{v:.2f}", ha="center", va="bottom")
        plt.tight_layout()
        st.pyplot(fig)
    with col2:
        fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
        sns.barplot(data=status_metrics, x="status", y="revenue", ax=ax, palette="Blues_d")
        ax.set_xlabel("Order Status")
        ax.set_ylabel("Revenue (₹)")
        ax.set_title("Revenue by Status")
        for i, v in enumerate(status_metrics["revenue"]):
            ax.text(i, v, f"₹{v:.2f}", ha="center", va="bottom")
        plt.tight_layout()
        st.pyplot(fig)
    
    st.subheader("🌟 Customer Segmentation (RFM Analysis)")
    if len(org_orders) >= 5:
        current_date = datetime.datetime.now()
        rfm = org_orders.groupby("receiver_name").agg({
            "date": lambda x: (current_date - x.max()).days,
            "order_id": "count",
            "revenue": "sum"
        }).reset_index()
        rfm.columns = ["receiver_name", "recency", "frequency", "monetary"]
        
        def assign_fallback_scores(series, n_bins=4):
            if series.nunique() < n_bins:
                return pd.Series(np.linspace(1, n_bins, len(series)), index=series.index).rank(method='dense').astype(int)
            else:
                try:
                    return pd.qcut(series, n_bins, labels=[4, 3, 2, 1], duplicates="drop")
                except:
                    bins = pd.cut(series, bins=n_bins, labels=[4, 3, 2, 1], include_lowest=True)
                    return bins
                
        try:
            rfm["R_score"] = pd.qcut(rfm["recency"], 4, labels=[4, 3, 2, 1], duplicates="drop")
        except ValueError as e:
            rfm["R_score"] = assign_fallback_scores(rfm["recency"])
        
        try:
            rfm["F_score"] = pd.qcut(rfm["frequency"], 4, labels=[1, 2, 3, 4], duplicates="drop")
        except ValueError as e:
            rfm["F_score"] = assign_fallback_scores(rfm["frequency"])
        
        try:
            rfm["M_score"] = pd.qcut(rfm["monetary"], 4, labels=[1, 2, 3, 4], duplicates="drop")
        except ValueError as e:
            rfm["M_score"] = assign_fallback_scores(rfm["monetary"])
        
        rfm["RFM_score"] = rfm["R_score"].astype(int) + rfm["F_score"].astype(int) + rfm["M_score"].astype(int)
        
        def assign_segment(score):
            if score >= 10:
                return "VIP Customers"
            elif score >= 7:
                return "Loyal Customers"
            elif score >= 4:
                return "Occasional Customers"
            else:
                return "At-Risk Customers"
        
        rfm["segment"] = rfm["RFM_score"].apply(assign_segment)
        segment_counts = rfm["segment"].value_counts().reset_index()
        segment_counts.columns = ["segment", "count"]
        
        fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
        sns.barplot(data=segment_counts, x="count", y="segment", ax=ax, palette="viridis")
        ax.set_xlabel("Number of Customers")
        ax.set_ylabel("Customer Segment")
        ax.set_title("Customer Segmentation by RFM Analysis")
        for i, v in enumerate(segment_counts["count"]):
            ax.text(v, i, f"{v}", va="center")
        plt.tight_layout()
        st.pyplot(fig)
        
        st.write("**Customer Segments and Names**")
        for segment in rfm["segment"].unique():
            customers = rfm[rfm["segment"] == segment]["receiver_name"].tolist()
            st.write(f"**{segment}**: {', '.join(customers)}")
        
        st.write("**What this means**:")
        st.write("- **VIP Customers**: Recent, frequent, and high-spending customers. Focus on retaining them.")
        st.write("- **Loyal Customers**: Regular buyers. Offer loyalty rewards to keep them engaged.")
        st.write("- **Occasional Customers**: Infrequent buyers. Encourage more purchases with promotions.")
        st.write("- **At-Risk Customers**: Haven't ordered recently. Reach out to re-engage them.")
    else:
        st.info("Need at least 5 orders to perform RFM analysis.")
    
    st.subheader("📦 Order Size Analysis")
    if not org_orders.empty:
        order_sizes = org_orders[["quantity", "receiver_name", "product"]]
        fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
        sns.histplot(data=order_sizes, x="quantity", bins=20, ax=ax, color="skyblue")
        ax.set_xlabel("Order Size (Quantity)")
        ax.set_ylabel("Number of Orders")
        ax.set_title("Distribution of Order Sizes")
        mean_size = order_sizes["quantity"].mean()
        median_size = order_sizes["quantity"].median()
        ax.axvline(mean_size, color="red", linestyle="--", label=f"Mean: {mean_size:.1f}")
        ax.axvline(median_size, color="green", linestyle="--", label=f"Median: {median_size:.1f}")
        ax.legend()
        plt.tight_layout()
        st.pyplot(fig)
        top_customers = order_sizes.groupby("receiver_name")["quantity"].sum().reset_index()
        top_customers = top_customers.sort_values("quantity", ascending=False).head(5)
        st.write("**Top 5 Customers by Total Order Size**:")
        for _, row in top_customers.iterrows():
            st.write(f"- {row['receiver_name']}: {row['quantity']} units")
        st.write("**What this means**:")
        st.write("- **Large orders**: Customers or products with high quantities may indicate bulk purchasing behavior.")
        st.write("- **Small orders**: Frequent small orders may suggest opportunities to bundle products.")
        st.write("- **Action**: Offer discounts for bulk orders or target high-volume customers with special promotions.")
    else:
        st.info("No orders available to analyze order sizes.")

def show_edit_order_form(order):
    
    st.title("Edit Order")
    
    with st.form("edit_order_form"):
        receiver_name = st.text_input("Receiver Name", value=order["receiver_name"])
        date = st.date_input("Order Date", pd.to_datetime(order["date"]).date())
        expected_delivery_date = st.date_input("Expected Delivery Date", pd.to_datetime(order["expected_delivery_date"]).date())
        product = st.text_input("Product", value=order["product"])
        description = st.text_area("Description (Optional)", value=order["description"])
        
        col1, col2 = st.columns(2)
        with col1:
            quantity = st.number_input("Quantity", min_value=1, value=int(order["quantity"]))
        with col2:
            price = st.number_input("Price per Unit (₹)", min_value=0.01, value=float(order["price"]), step=0.01)
        
        basic_price = quantity * price
        st.write(f"**Basic Price: ₹{basic_price:.2f}**")
        
        col1, col2 = st.columns(2)
        with col1:
            gst = st.number_input("GST (%)", min_value=0.0, value=float(order["gst"]), step=0.1)
        with col2:
            advance_payment = st.number_input("Advance Payment (₹)", min_value=0.0, value=float(order["advance_payment"]), step=0.01)
        
        total_amount_with_gst = basic_price + (basic_price * (gst / 100))
        pending_amount = total_amount_with_gst - advance_payment
        
        st.write(f"**Total Amount with GST: ₹{total_amount_with_gst:.2f}**")
        st.write(f"**Pending Amount: ₹{pending_amount:.2f}**")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Save Changes")
        with col2:
            cancel = st.form_submit_button("Cancel")
        
        if submitted:
            if receiver_name and product:
                if edit_order(order["order_id"], receiver_name, date, expected_delivery_date,
                             product, description, quantity, price, gst, advance_payment):
                    st.session_state.editing_order = None
                    st.session_state.form_submitted = True
                    st.session_state.form_message = "Order updated successfully!"
                    st.session_state.form_status = "success"
                    st.rerun()
        
        if cancel:
            st.session_state.editing_order = None
            st.rerun()

def show_manage_orders():
    
    st.title("Manage Orders")
    
    if st.session_state.form_submitted:
        if st.session_state.form_status == "success":
            st.success(st.session_state.form_message)
        elif st.session_state.form_status == "error":
            st.error(st.session_state.form_message)
        if st.button("Clear"):
            clear_form_feedback()
    
    org_orders = get_org_orders()
    
    if org_orders.empty:
        st.info("No orders to display.")
        return
    
    if st.session_state.editing_order is not None:
        order_to_edit = org_orders[org_orders["order_id"] == st.session_state.editing_order].iloc[0]
        show_edit_order_form(order_to_edit)
        return
    
    st.subheader("Filter Orders")
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox("Status", ["All", "Pending", "Completed"])
    with col2:
        date_range = st.date_input("Date Range", 
                                  value=[], 
                                  help="Select a date range to filter orders.")
    
    filtered_orders = org_orders.copy()

    if status_filter != "All":
        filtered_orders = filtered_orders[filtered_orders["status"] == status_filter]
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_orders["date"] = pd.to_datetime(filtered_orders["date"])
        filtered_orders = filtered_orders[
            (filtered_orders["date"] >= pd.Timestamp(start_date)) & 
            (filtered_orders["date"] <= pd.Timestamp(end_date))
        ]
    
    filtered_orders = filtered_orders.sort_values(by="order_id")
    
    st.subheader("Orders")
    if filtered_orders.empty:
        st.info("No orders match the filter criteria.")
        return
    
    for _, order in filtered_orders.iterrows():
        # Calculate pending quantity
        pending_quantity = order["quantity"] - order["delivered_quantity"]
        #expander label
        expander_label = (
            f"Order #{order['order_id']} - {order['product']} - {order['status']} -"
            f"(Pending Quantity: {pending_quantity}, Pending Amount: ₹{order['pending_amount']:.2f})"
        )
        with st.expander(expander_label):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Receiver:** {order['receiver_name']}")
                st.write(f"**Date:** {order['date']}")
                st.write(f"**Expected Delivery:** {order['expected_delivery_date']}")
                st.write(f"**Product:** {order['product']}")
                if order["description"]:
                    st.write(f"**Description:** {order['description']}")
                st.write(f"**Quantity Ordered:** {order['quantity']}")
                st.write(f"**Quantity Delivered:** {order['delivered_quantity']}")
                st.write(f"**Pending Quantity:** {pending_quantity}")
                st.write(f"**Price per Unit:** ₹{order['price']:.2f}")
                st.write(f"**Basic Price:** ₹{order['basic_price']:.2f}")
                st.write(f"**GST (%):** {order['gst']:.1f}%")
                st.write(f"**Advance Payment:** ₹{order['advance_payment']:.2f}")
                st.write(f"**Total Amount with GST:** ₹{order['total_amount_with_gst']:.2f}")
                st.write(f"**Pending Amount:** ₹{order['pending_amount']:.2f}")
            
            with col2:
                order_id = order["order_id"]
                if st.button(f"Edit Order", key=f"edit_{order_id}"):
                    st.session_state.editing_order = order_id
                    st.rerun()
                
                if st.button(f"Delete Order", key=f"delete_{order_id}"):
                    if delete_order(order_id):
                        st.rerun()
                
                if order["status"] == "Pending":
                    if st.button(f"Mark as Completed", key=f"complete_{order_id}"):
                        update_order_status(order_id, "Completed")
                        st.session_state.form_submitted = True
                        st.session_state.form_message = "Order marked as completed!"
                        st.session_state.form_status = "success"
                        st.rerun()
            
            # Delivery Management
            st.subheader("Deliveries")
            deliveries = load_deliveries(order_id, st.session_state.current_org)
            if deliveries.empty:
                st.info("No deliveries recorded for this order.")
            else:
                for _, delivery in deliveries.iterrows():
                    with st.container():
                        st.write(f"**Delivery ID:** {delivery['delivery_id']}")
                        st.write(f"**Quantity:** {delivery['delivery_quantity']}")
                        st.write(f"**Date:** {delivery['delivery_date']}")
                        st.write(f"**Total Amount Received:** ₹{delivery['total_amount_received']:.2f}")
                        if delivery["url"]:
                            try:
                                response = requests.get(delivery["url"], timeout=5)
                                response.raise_for_status()
                                file_data = response.content
                                file_ext = delivery["file_name"].split(".")[-1].lower()
                                mime_types = {
                                    "pdf": "application/pdf",
                                    "jpg": "image/jpeg",
                                    "jpeg": "image/jpeg",
                                    "png": "image/png"
                                }
                                mime = mime_types.get(file_ext, "application/octet-stream")
                                st.download_button(
                                    label="Download E-way Bill",
                                    data=file_data,
                                    file_name=f"ewaybill_delivery_{delivery['delivery_id']}.{file_ext}",
                                    mime=mime,
                                    key=f"download_delivery_ewaybill_{order_id}_{delivery['delivery_id']}"
                                )
                            except requests.RequestException as e:
                                st.warning(f"E-way bill not accessible ({e}).")
                        
                        if st.button("Delete Delivery", key=f"delete_delivery_{order_id}_{delivery['delivery_id']}"):
                            success, message = delete_delivery(order_id, delivery["delivery_id"])
                            if success:
                                st.session_state.form_submitted = True
                                st.session_state.form_message = message
                                st.session_state.form_status = "success"
                            else:
                                st.session_state.form_submitted = True
                                st.session_state.form_message = message
                                st.session_state.form_status = "error"
                            st.rerun()
                        st.markdown("---")
            
            if order["delivered_quantity"] < order["quantity"]:
                with st.form(f"add_delivery_form_{order_id}"):
                    delivery_quantity = st.number_input(
                        "Delivery Quantity",
                        min_value=1,
                        max_value=order["quantity"] - order["delivered_quantity"],
                        value=1
                    )
                    delivery_date = st.date_input("Delivery Date", value=datetime.date.today())
                    total_amount_received = st.number_input(
                        "Total Amount Received (₹)",
                        min_value=0.0,
                        value=0.0,
                        step=0.01,
                        help="Enter the amount received for this delivery."
                    )
                    uploaded_file = st.file_uploader(
                        "Upload E-way Bill",
                        type=["pdf", "jpg", "png"],
                        key=f"delivery_ewaybill_{order_id}"
                    )
                    
                    submitted = st.form_submit_button("Add Delivery")
                    
                    if submitted:
                        file_data = uploaded_file.read() if uploaded_file else None
                        file_name = uploaded_file.name if uploaded_file else None
                        success, message = add_delivery(
                            order_id, delivery_quantity, delivery_date, total_amount_received, file_data, file_name
                        )
                        if success:
                            st.session_state.form_submitted = True
                            st.session_state.form_message = message
                            st.session_state.form_status = "success"
                        else:
                            st.session_state.form_submitted = True
                            st.session_state.form_message = message
                            st.session_state.form_status = "error"
                        st.rerun()
def show_export_reports():
    
    st.title("Export Reports")
    
    org_orders = get_org_orders()
    
    if org_orders.empty:
        st.info("No orders to export.")
        return
    
    st.subheader("Export Order List")
    
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox("Status", ["All", "Pending", "Completed"])
    with col2:
        date_range = st.date_input("Date Range", 
                                  value=[], 
                                  help="Select a date range to filter orders.")
    
    filtered_orders = org_orders.copy()
    if status_filter != "All":
        filtered_orders = filtered_orders[filtered_orders["status"] == status_filter]
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_orders["date"] = pd.to_datetime(filtered_orders["date"])
        filtered_orders = filtered_orders[
            (filtered_orders["date"] >= pd.Timestamp(start_date)) & 
            (filtered_orders["date"] <= pd.Timestamp(end_date))
        ]
    
    # Add revenue column to filtered_orders
    filtered_orders["revenue"] = 0.0
    for idx, row in filtered_orders.iterrows():
        deliveries = load_deliveries(row["order_id"], row["org"])
        delivery_amount = deliveries["total_amount_received"].sum() if not deliveries.empty else 0
        filtered_orders.at[idx, "revenue"] = row["advance_payment"] + delivery_amount
    
    st.dataframe(filtered_orders)
    
    col1, col2= st.columns(2)
    with col1:
        if st.button("Export to Excel"):
            excel_data = export_to_excel(filtered_orders)
            st.download_button(
                label="Download Excel File",
                data=excel_data,
                file_name="order_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    with col2:
        st.button("Export to PDF (Coming Soon)", disabled=True)
    
    st.subheader("Revenue Summary")
    
    if not org_orders.empty:
        org_orders["date"] = pd.to_datetime(org_orders["date"])
        org_orders["month"] = org_orders["date"].dt.strftime("%Y-%m")
        # Calculate revenue for each order
        org_orders["revenue"] = 0.0
        for idx, row in org_orders.iterrows():
            deliveries = load_deliveries(row["order_id"], row["org"])
            delivery_amount = deliveries["total_amount_received"].sum() if not deliveries.empty else 0
            org_orders.at[idx, "revenue"] = row["advance_payment"] + delivery_amount
        
        monthly_revenue = org_orders.groupby("month").agg({
            "revenue": "sum"
        }).reset_index()
        monthly_revenue.columns = ["Month", "Total Revenue"]
        
        # Add yearly revenue calculation
        org_orders["year"] = org_orders["date"].dt.year
        yearly_revenue = org_orders.groupby("year").agg({
            "revenue": "sum"
        }).reset_index()
        yearly_revenue.columns = ["Year", "Total Revenue"]
        yearly_revenue["Year"] = yearly_revenue["Year"].astype(str)
        
        # Display monthly and yearly revenue
        st.write("**Monthly Revenue**")
        if not monthly_revenue.empty:
            st.dataframe(monthly_revenue)
            if st.button("Export Revenue Summary"):
                output = BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    monthly_revenue.to_excel(writer, index=False)
                st.download_button(
                    label="Download Revenue Summary",
                    data=output.getvalue(),
                    file_name="revenue_summary.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.info("No orders to calculate revenue.")
        
        st.write("**Yearly Revenue**")
        if not yearly_revenue.empty:
            st.dataframe(yearly_revenue)
            if st.button("Export Yearly Revenue"):
                output = BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    yearly_revenue.to_excel(writer, index=False)
                st.download_button(
                    label="Download Yearly Revenue",
                    data=output.getvalue(),
                    file_name="yearly_revenue.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.info("No orders to calculate yearly revenue.")
    
        st.subheader("Export Deliveries for a Specific Order")
        order_options = [(row["order_id"], row["org"], row["product"]) for _, row in filtered_orders.iterrows()]
        order_display = [f"Order {order_id} - {product}" for order_id, org, product in order_options]
        selected_order = st.selectbox("Select Order", order_display)
    
        if selected_order:
          order_id, org, _ = order_options[order_display.index(selected_order)]
          deliveries = load_deliveries(order_id, org)
        
        if deliveries.empty:
            st.info(f"No deliveries found for Order {order_id} - {org}.")
        else:
            st.write("**Deliveries**")
            for _, delivery in deliveries.iterrows():
                st.write(f"**Delivery ID**: {delivery['delivery_id']}")
                st.write(f"**Quantity**: {delivery['delivery_quantity']}")
                st.write(f"**Date**: {delivery['delivery_date']}")
                st.write(f"**Total Amount Received**: ₹{delivery['total_amount_received']:.2f}")
                st.markdown("---")
            
            if st.button("Export Deliveries to Excel"):
                # Prepare delivery details for export
                export_deliveries = deliveries[[
                    "delivery_id", "delivery_quantity", "delivery_date", "total_amount_received"
                ]].rename(columns={
                    "delivery_id": "Delivery ID",
                    "delivery_quantity": "Quantity",
                    "delivery_date": "Date",
                    "total_amount_received": "Total Amount Received"
                })
                
                # Get order details for header
                order_details = filtered_orders[
                    (filtered_orders["order_id"] == order_id) & (filtered_orders["org"] == org)
                ][[
                    "order_id", "receiver_name", "quantity", "advance_payment", "gst", 
                    "total_amount_with_gst", "pending_amount", "product", "description", 
                    "date", "expected_delivery_date", "status", "created_by"
                ]].rename(columns={
                    "order_id": "Order ID",
                    "receiver_name": "Receiver Name",
                    "quantity": "Total Quantity",
                    "advance_payment": "Advance Payment",
                    "gst": "GST%",
                    "total_amount_with_gst": "Total Amount with GST",
                    "pending_amount": "Pending Amount",
                    "product": "Product",
                    "description": "Description",
                    "date": "Order Date",
                    "expected_delivery_date": "Expected Delivery Date",
                    "status": "Status",
                    "created_by": "Created By"
                })
                
                # Create Excel file with order details as header and deliveries below
                output = BytesIO()
                workbook = openpyxl.Workbook()
                sheet = workbook.active
                sheet.title = "Deliveries"
                
                # Write order details as header
                sheet.append(["Order Details"])
                for r in dataframe_to_rows(order_details, index=False, header=True):
                    sheet.append(r)
                sheet.append([]) 
                
                # Write deliveries
                sheet.append(["Delivery Details"])
                for r in dataframe_to_rows(export_deliveries, index=False, header=True):
                    sheet.append(r)
                
                workbook.save(output)
                output.seek(0)
                
                st.download_button(
                    label="Download Deliveries Excel",
                    data=output.getvalue(),
                    file_name=f"deliveries_order_{order_id}_{org}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

def show_account_settings():
    
    st.title("Account Settings")
    
    st.subheader("User Information")
    st.write(f"**Username:** {st.session_state.current_user}")
    st.write(f"**Organization:** {st.session_state.current_org}")
    
    st.subheader("Change Password")
    with st.form("change_password_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        submit = st.form_submit_button("Change Password")
        
        if submit:
            if current_password and new_password and confirm_password:
                users = load_users()
                if users[st.session_state.current_user]["password"] == current_password:
                    if new_password == confirm_password:
                        password_pattern = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@₹!%*?&])[A-Za-z\d@₹!%*?&]{6,}₹"
                        if not re.match(password_pattern, new_password):
                            st.error("New password must be at least 6 characters long and contain at least one letter, one digit, and one special symbol (@₹!%*?&).")
                        else:
                            supabase.table("users").update({"password": new_password}).eq("username", st.session_state.current_user).execute()
                            st.success("Password changed successfully!")
                    else:
                        st.error("New passwords do not match!")
                else:
                    st.error("Current password is incorrect!")
            else:
                st.error("All fields are required!")
    
    st.subheader("Delete Account")
    st.warning(
        "Warning: Deleting your account will permanently remove all your data, "
        "including orders and reports. This action cannot be undone."
    )
    
    if st.button("Delete My Account"):
        st.session_state.show_delete_account = True
        st.rerun()

def main():
    if not st.session_state.authenticated:
        show_login_page()
    else:
        menu = show_sidebar()
        if menu == "Dashboard":
            show_dashboard()
        elif menu == "Add Order":
            show_add_order()
        elif menu == "Manage Orders":
            show_manage_orders()
        elif menu == "Export Reports":
            show_export_reports()
        elif menu == "Account Settings":
            show_account_settings()
        elif menu == "Admin Panel" and st.session_state.is_admin:
            show_admin_panel()

if __name__ == "__main__":
    main()
