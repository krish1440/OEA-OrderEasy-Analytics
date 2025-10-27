![Logo](logo.png)

# OrderEasy Analytics - Smart Order Management System

**OrderEasy Analytics (OEA)** is a state-of-the-art, AI-powered order management platform for businesses of all sizes. Designed with a modern, intuitive interface using Streamlit, it provides robust order processing, delivery tracking, and powerful data-driven analytics. Integrated with **Supabase** for scalable cloud database management and **Cloudinary** for secure file storage, OEA lets you automate, analyze, and optimize your entire order lifecycle.

---

## ✨ Key Features

- **Order Management**
  - Create, edit, delete, and track orders with detailed attributes (receiver, product, quantity, payment, GST).
  - Auto-calculated financials: GST, pending amounts, advance payment, etc.
  - Edit and manage orders with full audit history.

- **E-way Bill Integration**
  - Upload & manage e-way bills for orders and deliveries (PDF/images via Cloudinary).
  - Download, replace, and view e-way bills directly from the dashboard.

- **Advanced Analytics Dashboard**
  - Monthly/Yearly trends for revenue, quantity, and customer activity.
  - Top receivers/product analysis, Customer Lifetime Value (CLV), retention, RFM segmentation.
  - Automated sales forecasting (Linear Regression, confidence intervals).
  - Visuals powered by Matplotlib & Seaborn for deep insights.

- **Delivery Management**
  - Add, track deliveries against orders, capture delivery quantity, payment details, and associated documentation.

- **User Management & Admin Tools**
  - Signup/login, change password, and delete account (all data deletion on account removal!).
  - Admin panel for user management, including organization support.
  - Role-based access with secure authentication.

- **Exports & Reporting**
  - Export orders, deliveries, and analytics to Excel (OpenPyXL).
  - Bulk ZIP downloads for deliveries.
  - PDF export (coming soon).

- **Responsive UI/UX**
  - Sidebar navigation, tabbed authentication, expanders for detailed order/delivery views.
  - Integrated contacts/help section.

---

## 🏗️ Tech Stack

| **Layer**       | **Technologies**                                                        |
|:--------------: |:-----------------------------------------------------------------------:|
| Backend         | Python 3.8+, Streamlit (UI/UX)                                          |
| Database        | Supabase (PostgreSQL)                                                   |
| File Storage    | Cloudinary (PDF, images)                                                |
| Data Analysis   | Pandas, NumPy, Scikit-learn, Seaborn, Matplotlib, SciPy                 |
| Environment     | python-dotenv, Streamlit secrets                                        |
| Packaging       | OpenPyXL, ZIP management                                                |
| Logging         | Python logging module                                                   |

---

## ⚡ Quick Start

1. **Clone this repo:**

```bash
git clone https://github.com/krish1440/OEA-OrderEasy-Analytics.git
cd OEA-OrderEasy-Analytics
```

2. **Install requirements:**

```bash
pip install -r requirements.txt
```

3. **Create Supabase tables:**

- `users`, `orders`, `deliveries`, `ewaybills`
- Required columns: see `app.py` or docs for details

4. **Configure Cloudinary:**

- Create an account and get your API credentials.

5. **Set Environment Variables:**

-.env file or Streamlit secrets:
```bash
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
ADMIN_USERNAME=
ADMIN_PASSWORD=
SUPABASE_URL=
SUPABASE_KEY=
```

6. **Run the Application:**

```bash
streamlit run app.py
```

---

## 🖥️ Deployment

- **Streamlit Cloud:**  
On cloud - [oea-ordereasy-analytic.streamlit.app](https://oea-ordereasy-analytic.streamlit.app/)
- **DevContainer support:**  
Ready for codespaces/VSCode remote development ([`.devcontainer`](.devcontainer/devcontainer.json))

---

## 🚩 Usage Workflow

1. **Sign Up / Log In**  
For your business/team, create or access your organization account.
2. **Add Orders & Delivery Docs**  
Input order details, upload e-way bills.
3. **Track & Manage**  
Edit, mark completed, view order timeline, manage deliveries.
4. **Analytics & Forecasting**  
Deep visual metrics, customer segmentation, advanced forecasting.
5. **Export & Admin**  
Download reports, manage users, control data.

---

## 🛡️ Security Highlights

- Password validation (min 6 chars, letter, digit, symbol)
- Role-based admin/user authentication
- Full organization-level data isolation and clean deletion

---

## 📚 Documentation & Help

- **Contact:** krishchaudhary144@gmail.com | +91 6353160662
- See [app.py](app.py) for advanced code reference.
- For integration, workflows or table schema setup: see Supabase/Cloudinary documentation.

---

## 👤 Author

**Krish Chaudhary**  
[LinkedIn](https://www.linkedin.com/in/krish-chaudhary-krc8252)

---

## 📝 License

MIT - see [LICENSE](LICENSE) for details.

---

## 👏 Acknowledgments

- Streamlit: Intuitive Python web framework
- Supabase: Instant backend/database
- Cloudinary: Reliable file storage
- Pandas, Matplotlib, Seaborn: Advanced analytics and visualization

---

## 🌟 Contributing

PRs and suggestions welcome!  
Create a fork, open an issue, or submit a pull request for new features, optimizations, or bug fixes.

---

*Transform your business order management — from chaos to clarity, with data-driven decisions, smart integrations, and seamless automation.*
