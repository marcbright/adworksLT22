import os
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine


# SQL Server connection details
#server = '' 
#database = ''
#username = '' 
#password = ''

# Load environment variables
server = os.getenv("AZURE_SERVER")
database = os.getenv("AZURE_DATABASE")
username = os.getenv("AZURE_USERNAME")
password = os.getenv("AZURE_PASSWORD")
#driver = os.getenv("AZURE_DRIVER", "ODBC Driver 17 for SQL Server")

# Create a SQLAlchemy Engine
engine = create_engine(f"DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes")

# Set page configuration
st.set_page_config(page_title="AdventureWorks Sales Dashboard", page_icon="📊", layout="wide")

# Branding Section
st.image("gi_kace_logo.png", width=120) 
st.title("📊 AdventureWorksLT2022 Sales Dashboard")
st.markdown("Gain insights into sales trends, customer behavior, and product performance.")

# Custom Divider
st.markdown("---")

# Styling with CSS (Optional)
st.markdown("""
    <style>
        .title {
            font-size: 30px;
            font-weight: bold;
            text-align: center;
        }
        .description {
            font-size: 18px;
            text-align: center;
            color: gray;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar Filters
st.sidebar.header("🔍 Filter Data")
date_range = st.sidebar.date_input("📅 Select Date Range", [pd.to_datetime("2000-01-01"), pd.to_datetime("2024-12-31")])

# Fetch Filter Options
product_categories = pd.read_sql("SELECT DISTINCT Name FROM SalesLT.ProductCategory", engine)
customers = pd.read_sql("SELECT DISTINCT CompanyName FROM SalesLT.Customer", engine)
states = pd.read_sql("SELECT DISTINCT StateProvince FROM SalesLT.Address", engine)

selected_category = st.sidebar.selectbox("📦 Product Category", product_categories["Name"])
selected_customer = st.sidebar.selectbox("👤 Customer", customers["CompanyName"])
selected_state = st.sidebar.multiselect("🏢 Select State", states["StateProvince"])
price_range = st.sidebar.slider("💰 Order Total ($)", 0, 5000000, (50, 500))

# Query Function with Filters
def get_filtered_orders(date_range, category, customer, state, price_range):
    query = f"""
    SELECT soh.SalesOrderID, soh.OrderDate, soh.TotalDue, c.CompanyName AS CustomerName,  
           p.Name AS ProductName, pc.Name AS CategoryName, a.City, a.StateProvince
    FROM SalesLT.SalesOrderHeader soh
    JOIN SalesLT.SalesOrderDetail sod ON soh.SalesOrderID = sod.SalesOrderID
    JOIN SalesLT.Product p ON sod.ProductID = p.ProductID
    JOIN SalesLT.ProductCategory pc ON p.ProductCategoryID = pc.ProductCategoryID
    JOIN SalesLT.Customer c ON soh.CustomerID = c.CustomerID
    JOIN SalesLT.CustomerAddress ca ON c.CustomerID = ca.CustomerID  
    JOIN SalesLT.Address a ON ca.AddressID = a.AddressID
    WHERE soh.OrderDate BETWEEN '{date_range[0]}' AND '{date_range[1]}'
    AND pc.Name = '{category}'
    AND c.CompanyName = '{customer}'
    AND soh.TotalDue BETWEEN {price_range[0]} AND {price_range[1]}
    """

    if state:
        states_str = "', '".join(state)  # Convert list to SQL string format
        query += f" AND a.StateProvince IN ('{states_str}')"

    return pd.read_sql(query, engine)

# Display Filtered Orders
st.subheader("📋 Filtered Orders")

if st.sidebar.button("🔄 Apply Filters"):
    orders_df = get_filtered_orders(date_range, selected_category, selected_customer, selected_state, price_range)
    
    if not orders_df.empty:
        st.dataframe(orders_df)  # Show results in table format
    else:
        st.warning("⚠️ No matching orders found. Try adjusting filters.")


# Function to Fetch KPIs
@st.cache_data
def get_kpis():
    query = """
    SELECT 
        SUM(soh.TotalDue) AS TotalRevenue, 
        COUNT(soh.SalesOrderID) AS NumberOfOrders,
        (SELECT TOP 1 p.Name 
         FROM SalesLT.SalesOrderDetail sod
         JOIN SalesLT.Product p ON sod.ProductID = p.ProductID
         GROUP BY p.Name 
         ORDER BY SUM(sod.OrderQty) DESC) AS TopSellingProduct
    FROM SalesLT.SalesOrderHeader soh;
    """
    return pd.read_sql(query, engine)

# Fetch KPI Data
kpi_df = get_kpis()

# Display KPI Metrics
st.header("📈 Key Metrics & KPIs")

col1, col2, col3 = st.columns(3)

# Total Revenue
col1.metric("💰 Total Revenue", f"${kpi_df['TotalRevenue'][0]:,.2f}")

# Number of Orders
col2.metric("📦 Number of Orders", f"{kpi_df['NumberOfOrders'][0]:,}")

# Top-Selling Product
col3.metric("🏆 Top Selling Product", kpi_df['TopSellingProduct'][0])

st.markdown("---")  # Add a separator


# Function to get top-selling products by category
@st.cache_data
def get_top_selling_products_category():
    query = """
    SELECT TOP 10 
        pc.Name AS Category, 
        SUM(sod.LineTotal) AS TotalSales
    FROM SalesLT.SalesOrderDetail sod
    JOIN SalesLT.Product p ON sod.ProductID = p.ProductID
    JOIN SalesLT.ProductCategory pc ON p.ProductCategoryID = pc.ProductCategoryID
    GROUP BY pc.Name
    ORDER BY TotalSales DESC;
    """
    return pd.read_sql(query, engine)

# Function to get number of orders per category
@st.cache_data
def get_orders_by_category():
    query = """
    SELECT 
        TOP 10 pc.Name AS CategoryName, 
        COUNT(soh.SalesOrderID) AS NumberOfOrders
    FROM SalesLT.SalesOrderHeader soh
    JOIN SalesLT.SalesOrderDetail sod ON soh.SalesOrderID = sod.SalesOrderID
    JOIN SalesLT.Product p ON sod.ProductID = p.ProductID
    JOIN SalesLT.ProductCategory pc ON p.ProductCategoryID = pc.ProductCategoryID
    GROUP BY pc.Name
    ORDER BY NumberOfOrders DESC;
    """
    return pd.read_sql(query, engine)

# Load Data
top_selling_df = get_top_selling_products_category()
orders_category_df = get_orders_by_category()

# Create two columns for side-by-side display
col1, col2 = st.columns(2)

# Plot Top Selling Products by Category
with col1:
    st.subheader("📦 Top Selling Products By Category")
    fig_top_selling = px.bar(
        top_selling_df, 
        x="Category", 
        y="TotalSales", 
        title="📦 Top Selling Products By Category",
        color="TotalSales",
        text="TotalSales",
        color_continuous_scale=px.colors.sequential.Viridis
    )
    st.plotly_chart(fig_top_selling, use_container_width=True)

# Plot Orders Per Category
with col2:
    st.subheader("📦 Number of Orders Per Category")
    fig_orders = px.bar(
        orders_category_df, 
        x="CategoryName", 
        y="NumberOfOrders", 
        title="📦 Number of Orders Per Category",
        color="NumberOfOrders",
        text="NumberOfOrders"
    )
    st.plotly_chart(fig_orders, use_container_width=True)



# Function to get number of orders per category
@st.cache_data
def get_frequently_purchased_products():
    query = """
    SELECT TOP 10 p.Name AS Product, COUNT(sod.ProductID) AS OrderCount
    FROM SalesLT.SalesOrderDetail sod
    JOIN SalesLT.Product p ON sod.ProductID = p.ProductID
    GROUP BY p.Name
    ORDER BY OrderCount DESC;
    """
    return pd.read_sql(query, engine)

@st.cache_data
def get_highest_customer_spending():
    query = """
    SELECT 
	TOP 10 c.FirstName, 
		c.CustomerID,
		c.CompanyName,
		SUM(s.TotalDue) AS TotalSpent  
FROM 
	SalesLT.Customer c  
	JOIN SalesLT.SalesOrderHeader s ON c.CustomerID = s.CustomerID  
GROUP BY 
	c.CustomerID, c.FirstName, c.CompanyName 
ORDER BY TotalSpent DESC; 
    """
    return pd.read_sql(query, engine)

get_frequently_purchased_products_df = get_frequently_purchased_products()
get_highest_customer_spending_df = get_highest_customer_spending()

col3, col4 = st.columns(2)

with col3:
    st.subheader("📦 Frequently Purchased Products")
    # Plot Top-Selling Products as a Horizontal Bar Chart
    fig_freq_purchased_products = px.bar(
    get_frequently_purchased_products_df, 
    x="OrderCount",  # Order count on x-axis
    y="Product",  # Products on y-axis (for horizontal bars)
    orientation="h",  # Horizontal bar chart
    title="🏆 Frequently Purchased Products",
    color="OrderCount",  # Color based on order count
    text="OrderCount",  # Show numbers on bars
    color_continuous_scale=px.colors.sequential.Oranges  # Customize color
    )
    st.plotly_chart(fig_freq_purchased_products)


with col4:
    st.subheader("💰 Highest Spending Customers")
    fig_highest_customer_spending = px.bar(
        get_highest_customer_spending_df, 
        x="CompanyName", 
        y="TotalSpent", 
        title="💰 Highest Spending Customers",  # Updated title
        color="TotalSpent",
        text="TotalSpent",
       color_continuous_scale=px.colors.sequential.Cividis_r
    )
    st.plotly_chart(fig_highest_customer_spending)

