# Smart Order Management System

## Overview
The **Smart Order Management System** is a comprehensive web application built using **Streamlit**, designed to streamline order processing, tracking, and analytics for businesses. It integrates with **Supabase** for database management and **Cloudinary** for file storage, offering features like order creation, e-way bill uploads, advanced analytics, and user management with admin capabilities.

## Features
- **Order Management**: Create, edit, delete, and track orders with details like receiver name, product, quantity, price, GST, and payment status.
- **E-way Bill Integration**: Upload and manage e-way bills (PDF/image) with Cloudinary, including download and replace functionalities.
- **Advanced Analytics**: Visualize key metrics such as:
  - Monthly revenue and quantity trends
  - Top receivers and products by revenue/quantity
  - Customer lifetime value (CLV) and retention analysis
  - RFM (Recency, Frequency, Monetary) customer segmentation
  - Sales forecasting with confidence intervals
- **User Management**: Secure authentication with signup, login, and password change features. Admins can manage users and delete accounts.
- **Export Reports**: Export order lists and revenue summaries to Excel for reporting purposes.
- **Responsive UI**: Intuitive interface with sidebar navigation and expandable order details.

## Tech Stack
- **Frontend & Backend**: Streamlit (Python)
- **Database**: Supabase (PostgreSQL)
- **File Storage**: Cloudinary
- **Data Analysis**: Pandas, NumPy, Scikit-learn
- **Visualization**: Matplotlib, Seaborn
- **Environment Management**: python-dotenv
- **Logging**: Python `logging` module

## Prerequisites
To run the application locally, ensure you have:
- Python 3.8+
- A Supabase account with the following tables created:
  - `users`: Stores user credentials and organization details
  - `orders`: Stores order information
  - `ewaybills`: Stores e-way bill metadata
- A Cloudinary account for file uploads
- A `.env` file or Streamlit secrets configured with:
  - `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`
  - `ADMIN_USERNAME`, `ADMIN_PASSWORD`
  - `SUPABASE_URL`, `SUPABASE_KEY`

## Installation
1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd smart-order-management
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**:
   Create a `.env` file in the project root with the following:
   ```env
   CLOUDINARY_CLOUD_NAME=your_cloud_name
   CLOUDINARY_API_KEY=your_api_key
   CLOUDINARY_API_SECRET=your_api_secret
   ADMIN_USERNAME=your_admin_username
   ADMIN_PASSWORD=your_admin_password
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   ```

4. **Create Supabase Tables**:
   Run the following SQL in the Supabase SQL Editor to set up the required tables:
   ```sql
   CREATE TABLE users (
       username TEXT PRIMARY KEY,
       password TEXT NOT NULL,
       organization TEXT NOT NULL,
       is_admin INTEGER DEFAULT 0
   );

   CREATE TABLE orders (
       order_id INTEGER,
       org TEXT,
       receiver_name TEXT,
       date TEXT,
       expected_delivery_date TEXT,
       product TEXT,
       description TEXT,
       quantity INTEGER,
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
   ```

5. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

## Deployment
The application is deployed on Streamlit Cloud and can be accessed at:  
[Smart Order Management](https://smart-order-management.streamlit.app/)

## Usage
1. **Sign Up / Log In**: Create an account or log in with existing credentials.
2. **Add Orders**: Navigate to "Add Order" to input order details and calculate totals with GST.
3. **Manage Orders**: View, edit, delete, or mark orders as completed. Upload e-way bills for completed orders.
4. **Dashboard**: Explore analytics like revenue trends, customer segmentation, and sales forecasts.
5. **Export Reports**: Download order lists or revenue summaries in Excel format.
6. **Admin Panel** (Admins only): Manage users and delete accounts.
7. **Account Settings**: Change passwords or delete your account.

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Make your changes and commit (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

## Author
Developed by **Krish Chaudhary**  
Connect with me on LinkedIn: [Krish Chaudhary](https://www.linkedin.com/in/krish-chaudhary-krc8252)

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments
- **Streamlit** for the intuitive web framework
- **Supabase** for scalable database management
- **Cloudinary** for reliable file storage
- **Pandas**, **Matplotlib**, and **Seaborn** for powerful data analysis and visualization
