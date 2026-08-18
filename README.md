# 📊 Sales Intelligence Hub

> A branch-based sales management system with real-time analytics, MySQL triggers, and role-based access control.

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red)](https://streamlit.io/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-MIT-green)](#license)

---

## 🎯 Overview

**Sales Intelligence Hub** is a centralized **multi-branch sales management platform** that tracks sales transactions, payment collections, and pending amounts across distributed operations. Built with **Streamlit** (Python web UI) and **MySQL** backend, it provides:

- 📈 **Real-time dashboards** for executive reporting
- 🔐 **Role-based access control** (Super Admin vs Branch Admin)
- 💳 **Multi-payment tracking** per sale (partial/installment payments)
- 🔄 **Automated status management** via MySQL triggers
- 📊 **Advanced analytics** with dynamic query explorer

---

## 🏗️ Project Structure

```
sales_intelligence_hub_final/
├── login.py                          # Authentication & login page
├── Connector.py                      # Database connection manager
├── security.py                       # Password hashing/verification
├── theme.py                          # UI theme & styling
├── database_functions.py             # Database query helpers
├── requirements.txt                  # Python dependencies
├── README.md                         # Quick start guide
├── ARCHITECTURE.md                   # Technical architecture
├── PROJECT_DOCUMENTATION.md          # Complete project analysis
│
├── pages/                            # Streamlit multi-page routes
│   ├── Analytics.py                  # Executive analytics dashboard
│   ├── dashboards.py                 # Sales KPI dashboards
│   ├── create_sales.py               # New sale & payment entry
│   ├── Sales.py                      # Sales records viewer
│   ├── Payments.py                   # Payment tracking
│   ├── Query_Explorer.py             # Dynamic SQL query builder
│   └── __init__.py
│
├── sql/                              # SQL scripts
│   ├── schema.sql                    # Database schema
│   └── analytical_queries.sql        # Pre-built queries
│
├── setup_scripts/                    # Data initialization
│   ├── branches.py                   # Branch table setup
│   ├── customer_sales.py             # Sales table setup
│   ├── users.py                      # User table setup
│   └── payment_split.py              # Payment splits setup
│
└── data/                             # Demo data (CSV files)
    ├── branches.csv
    ├── customer_sales.csv
    ├── users.csv
    └── payment_splits.csv
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- MySQL Server 8.0+
- pip (Python package manager)

### Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/sales_intelligence_hub.git
cd sales_intelligence_hub_final
```

#### 2. Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate      # On Windows: .venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Setup Database

Create the database:
```sql
CREATE DATABASE IF NOT EXISTS Sales_Management;
```

#### 5. Configure Environment Variables

Create `.env` file from template:
```bash
cp .env.example .env
```

Edit `.env` with your MySQL credentials:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=Sales_Management
```

#### 6. Prepare Demo Data

Create `data/` folder and add CSV files with columns:

**branches.csv:**
```csv
branch_name,branch_admin_name
Chennai,Arun Kumar
Bangalore,Ravi Shankar
```

**customer_sales.csv:**
```csv
branch_id,date,name,mobile_number,product_name,gross_sales,received_amount
1,2026-01-15,John Doe,9876543210,Product A,50000,30000
```

**users.csv:**
```csv
username,password,branch_id,role,email
super_admin,password123,NULL,Super Admin,admin@company.com
branch_admin_1,password456,1,Admin,admin1@company.com
```

**payment_splits.csv:**
```csv
sale_id,payment_date,amount_paid,payment_method
1,2026-01-15,30000,Cash
1,2026-02-01,20000,Online Transfer
```

#### 7. Initialize Database

Run setup scripts **in order** (each creates tables and loads data):

```bash
python branches.py
python customer_sales.py
python users.py
python payment_split.py
```

Each script will print ✅ confirmations on successful completion.

#### 8. Launch the App

```bash
python -m streamlit run login.py
```

The app will open at `http://localhost:8501`

---

## 🔐 User Roles & Access

### Super Admin
- **Access:** All branches, all sales records
- **Permissions:** Create/edit sales, view analytics, run custom queries
- **Dashboard:** Company-wide KPIs and branch comparison

### Branch Admin
- **Access:** Only their assigned branch
- **Permissions:** Create/edit branch sales, view branch analytics
- **Dashboard:** Branch-specific KPIs and collections

### Login Credentials (Demo)
```
Username: super_admin
Password: password123

Username: branch_admin_1
Password: password456
```

---

## 📊 Key Features

### 1. Sales Dashboard
- **Real-time KPIs:** Total sales, collected amount, pending amount
- **Open vs Closed:** Track sales completion status
- **Branch-wise comparison:** Performance metrics by branch
- **Collection rate:** (Total Received / Total Sales) %

### 2. Sales Management
- **Create new sales:** Record gross sale with customer details
- **Add payments:** Track partial/installment payments
- **Payment methods:** Cash, Cheque, Online Transfer, etc.
- **Automatic status:** Status switches to "Close" when fully collected

### 3. Payment Tracking
- **Multiple payments per sale:** No limit on installment count
- **Payment method breakdown:** Analyze collection by channel
- **Payment history:** Full audit trail of all transactions

### 4. Analytics & Reporting
- **Monthly trends:** Sales and collection patterns over time
- **Branch rankings:** Top performing branches
- **Query Explorer:** Pre-built SQL queries for deep analysis
- **Custom queries:** Run dynamic queries on sales data

### 5. Security
- **Password hashing:** Bcrypt for secure credential storage
- **Role-based access:** SQL WHERE clauses enforce visibility
- **Session management:** Streamlit session state for login persistence
- **Foreign keys:** Referential integrity constraints

---

## 🗄️ Database Schema

### Tables

#### branch
```sql
branch_id (PK)
branch_name
branch_admin_name
```

#### users
```sql
user_id (PK)
username (UNIQUE)
password (hashed)
branch_id (FK)
role (Super Admin | Admin)
email
```

#### customer_sales
```sql
sale_id (PK)
branch_id (FK)
date
name
mobile_number
product_name
gross_sales
received_amount
pending_amount (GENERATED: gross_sales - received_amount)
status (ENUM: Open | Close) [AUTO via TRIGGER]
```

#### payment_split
```sql
payment_id (PK)
sale_id (FK)
payment_date
amount_paid
payment_method
```

### Key Features
- **Generated Columns:** `pending_amount` auto-calculated, always consistent
- **MySQL Triggers:** Auto-update `status` based on `pending_amount`
- **Foreign Keys:** Enforce data relationships across tables
- **Unique Constraints:** Prevent duplicate usernames

---

## 🔄 ELT Process

### Extract
CSV files in `data/` folder contain source data

### Load
Python scripts (`branches.py`, `customer_sales.py`, etc.) load CSV into MySQL

### Transform
- **Calculated fields:** `pending_amount = gross_sales - received_amount`
- **Automated status:** Triggers set status to "Close" when `pending_amount <= 0`
- **Role-based filtering:** SQL WHERE clauses filter by branch_id
- **Data aggregation:** Dashboard queries compute real-time metrics

---

## 📈 Analytics & Insights

### Built-in Queries

**Branch-wise Sales Summary**
```sql
SELECT b.branch_name, COUNT(cs.sale_id) AS total_sales,
       SUM(cs.gross_sales) AS total_gross,
       AVG(cs.gross_sales) AS avg_sale_value
FROM customer_sales cs
JOIN branch b ON cs.branch_id = b.branch_id
GROUP BY b.branch_name;
```

**Monthly Sales Trend**
```sql
SELECT YEAR(date) AS year, MONTH(date) AS month,
       SUM(gross_sales) AS total_gross,
       SUM(received_amount) AS total_received
FROM customer_sales
GROUP BY YEAR(date), MONTH(date)
ORDER BY year, month;
```

**Top 3 Highest Gross Sales**
```sql
SELECT * FROM customer_sales
WHERE branch_id = %s
ORDER BY gross_sales DESC
LIMIT 3;
```

**Open Sales (Pending Collection)**
```sql
SELECT * FROM customer_sales
WHERE branch_id = %s AND status = 'Open'
ORDER BY pending_amount DESC;
```

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Streamlit (Python web framework) |
| **Backend** | Python 3.10+ |
| **Database** | MySQL 8.0+ |
| **Authentication** | Bcrypt (password hashing) |
| **ORM** | mysql-connector-python |
| **Visualization** | Plotly (interactive charts) |
| **Data Processing** | Pandas |
| **Environment Mgmt** | python-dotenv |

---

## 📦 Dependencies

```
streamlit
pandas
mysql-connector-python
python-dotenv
plotly
```

Install all with:
```bash
pip install -r requirements.txt
```

---

## 🔐 Security Best Practices

✅ **Implemented**
- Password hashing with Bcrypt
- Parameterized SQL queries (prevent SQL injection)
- Role-based access control
- Session-based authentication
- Environment variables for secrets (DB password not in code)
- Foreign key constraints

⚠️ **Recommended for Production**
- Use HTTPS for Streamlit deployment
- Add two-factor authentication (2FA)
- Implement API rate limiting
- Add audit logging for all transactions
- Use database SSL connections
- Implement row-level security (RLS)

---

## 🚀 Deployment

### Local Development
```bash
python -m streamlit run login.py
```

### Streamlit Cloud
```bash
streamlit login
streamlit deploy
```

### Docker (Optional)
```dockerfile
FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "login.py"]
```

---

## 📊 Business Intelligence Features

### Executive Dashboards
- Company-wide KPIs (total sales, collections, pending)
- Branch performance comparison
- Time-series trends (sales and collections)
- Open vs closed sales ratio

### Operational Analytics
- Sales by customer / product / date range
- Payment method distribution
- Pending amount aging (0-30, 30-60, 60+ days)
- Collection efficiency by branch

### Query Explorer
- Pre-built queries for common analyses
- Custom SQL query execution (Admin only)
- Export results to CSV
- Query result caching

---

## 💡 Use Cases

1. **Sales Tracking:** Monitor individual sales from creation to full payment
2. **Collections Management:** Track pending amounts and collection status
3. **Branch Performance:** Compare branches by total sales and collection rate
4. **Cash Flow Analysis:** Understand payment inflows by method and timing
5. **Executive Reporting:** Generate dashboards for board meetings
6. **Compliance & Audit:** Maintain audit trail of all transactions

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Add docstrings to functions
- Test with sample data before submitting
- Update README for new features

---

## 🐛 Known Issues & Limitations

- **CSV-based data loading:** Current setup uses CSV files; consider implementing direct API data ingestion
- **No real-time notifications:** Consider adding email/SMS alerts for high-value sales
- **Limited scalability:** Current indexing strategy sufficient for ~100k records; add more indexes for larger datasets
- **Single-deployment:** No multi-region or read-replicas support

---

## 🗺️ Roadmap

- [ ] Add predictive analytics (forecasting next quarter revenue)
- [ ] Implement payment reminder automation (email/SMS)
- [ ] Add mobile app (React Native)
- [ ] Implement aging receivables report with alerts
- [ ] Add audit logging and compliance reports
- [ ] Create branch performance scorecard
- [ ] Add API layer for third-party integrations
- [ ] Implement real-time notifications

---

## 📝 Configuration

### Environment Variables (.env)

```env
# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_secure_password
DB_NAME=Sales_Management

# Optional: Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_HEADLESS=true
```

---

## 🆘 Troubleshooting

### Database Connection Failed
```
Error: Access denied for user 'root'@'localhost'
```
**Solution:** Check `.env` credentials and ensure MySQL is running
```bash
mysql -u root -p  # Test connection
```

### CSV File Not Found
```
Error: File does not exist: data/users.csv
```
**Solution:** Create `data/` folder and ensure all CSV files are present

### Streamlit Port Already in Use
```
Error: Address already in use
```
**Solution:** Change port or kill existing process
```bash
python -m streamlit run login.py --server.port 8502
```

### ImportError for mysql.connector
```
ModuleNotFoundError: No module named 'mysql'
```
**Solution:** Install mysql-connector-python
```bash
pip install mysql-connector-python
```

---

## 📖 Additional Documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Technical architecture details
- [PROJECT_DOCUMENTATION.md](./PROJECT_DOCUMENTATION.md) - Complete project analysis (EDA, ELT, business recommendations)
- [README.md](./README.md) - Original quick start guide
- [sql/schema.sql](./sql/schema.sql) - Database schema
- [sql/analytical_queries.sql](./sql/analytical_queries.sql) - Pre-built queries

---

## 📧 Support & Contact

For issues, questions, or suggestions:
- Open an issue on GitHub
- Email: support@salesintelligencehub.com
- Documentation: Check [PROJECT_DOCUMENTATION.md](./PROJECT_DOCUMENTATION.md)

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](./LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- MySQL database design inspired by ERP best practices
- Dashboard UI using Plotly for interactive visualizations

---

## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| **Database Tables** | 4 (branch, users, customer_sales, payment_split) |
| **Branches** | 8 (scalable) |
| **User Roles** | 2 (Super Admin, Branch Admin) |
| **Pages** | 7 (login, dashboards, analytics, sales, payments, query explorer, create sales) |
| **Python Files** | 15+ |
| **SQL Triggers** | 4 (2 for sales status, 2 for user constraint) |
| **Generated Columns** | 1 (pending_amount) |
| **Foreign Keys** | 3 |

---

**Last Updated:** 2026-08-18  
**Version:** 1.0.0  
**Maintainer:** Sales Intelligence Hub Team

⭐ If you found this helpful, please star the repository!
