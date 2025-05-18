# OEAOrderEasy Analytics

## Smart Order Management System
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
`


## Deployment
The application is deployed on Streamlit Cloud and can be accessed at:  
[Smart Order Management](https://oea-ordereasy-analytic.streamlit.app/)

## Usage
1. **Sign Up / Log In**: Create an account or log in with existing credentials.
2. **Add Orders**: Navigate to "Add Order" to input order details and calculate totals with GST.
3. **Manage Orders**: View, edit, delete, or mark orders as completed. Upload e-way bills for completed orders.
4. **Dashboard**: Explore analytics like revenue trends, customer segmentation, and sales forecasts.
5. **Export Reports**: Download order lists or revenue summaries in Excel format.
6. **Admin Panel** (Admins only): Manage users and delete accounts.
7. **Account Settings**: Change passwords or delete your account.



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
