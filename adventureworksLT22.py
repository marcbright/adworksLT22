#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().system('pip install plotly pyodbc pandas matplotlib seaborn')


# In[17]:


pip install sqlalchemy


# In[96]:


import pyodbc
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# SQL Server connection details
server = 'DESKTOP-PHE7T8U' 
database = 'AdventureWorksLT2022'
username = '' 
password = ''

# Create a SQLAlchemy Engine
engine = create_engine(f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server")


# In[67]:


query = """
SELECT TABLE_SCHEMA, TABLE_NAME 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_TYPE = 'BASE TABLE';
"""
df_tables = pd.read_sql(query, engine)
df_tables


# In[68]:


products = "SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Product';"
products = pd.read_sql(products, engine)
products


# In[69]:


address = "SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Address';"
address = pd.read_sql(address, engine)
address


# In[70]:


customer = "SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Customer';"
customer = pd.read_sql(customer, engine)
customer


# In[33]:


customeradd = "SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'CustomerAddress';"
customeradd = pd.read_sql(customeradd, engine)
customeradd


# In[71]:


prod_cat = "SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'ProductCategory';"
prod_cat = pd.read_sql(prod_cat, engine)
prod_cat


# In[73]:


sod = "SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'SalesOrderDetail';"
sod = pd.read_sql(sod, engine)
sod


# In[75]:


soh = "SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'SalesOrderHeader';"
soh = pd.read_sql(soh, engine)
soh


# In[39]:


df_tables.isnull().sum()


# In[42]:


df_tables.duplicated().isnull()


# In[43]:


df_tables.info()


# In[54]:


df_tables.info()


# In[47]:


df_tables.describe()


# In[51]:


unique_tables = df_tables.drop_duplicates(subset=['TABLE_SCHEMA', 'TABLE_NAME'])

print(unique_tables)


# In[80]:


query = """
SELECT * FROM SalesLT.Customer;
"""
df_customer = pd.read_sql(query, engine)

df_customer.head()


# In[82]:


query = """
SELECT * FROM SalesLT.Product;
"""
df_product = pd.read_sql(query, engine)

df_product.head()


# In[83]:


query = """
SELECT * FROM SalesLT.SalesOrderDetail;
"""
df_sod = pd.read_sql(query, engine)

df_sod.head()


# In[84]:


query = """
SELECT * FROM SalesLT.SalesOrderHeader;
"""
df_soh = pd.read_sql(query, engine)

df_soh.head()


# In[66]:


df_customer.columns


# In[94]:


query = """
SELECT * FROM SalesLT.Product;
"""
sql_df = pd.read_sql(query, engine)
sql_df.head(5)


# In[85]:


customer_spending = "SalesLT.HighestCustomerSpending;"
df_highest_spending = pd.read_sql(customer_spending, engine)
df_highest_spending


# In[120]:


fig = px.bar(df_highest_spending,
             x="FirstName",
             y="TotalSpent",
             title="Top 10 Highest Customer Spending",
             color="TotalSpent",
             text="TotalSpent",
             color_continuous_scale=px.colors.sequential.Viridis)

fig.update_layout(
    height=600,
    title_x=0.5,  # Center the title horizontally
    title_y=0.95, # Adjust vertical position if necessary
    title_font=dict(size=20)  # Adjust title font size if needed
)

fig.show()


# In[125]:


sales_summary_cat = "SalesLT.SalesSummaryByCategory;"
df_sales = pd.read_sql(sales_summary_cat, engine)
df_sales.head(10)


# In[128]:


fig = px.bar(df_sales,
             x="ProductCategory",
             y="TotalSales",
             title="Sales By Product Category",
             color="TotalSales",
             text="TotalSales",
             color_continuous_scale='Bluered_r', hover_name="TotalSales")

fig.update_layout(
    height=600,
    title_x=0.5,  # Center the title horizontally
    title_y=0.95, # Adjust vertical position if necessary
    title_font=dict(size=20)  # Adjust title font size if needed
)

fig.show()


# In[86]:


query = """
SELECT YEAR(OrderDate) Year, SUM(TotalDue) AS TotalRevenue
FROM
	SalesLT.SalesOrderHeader
GROUP BY 
	YEAR(OrderDate)
ORDER BY  
	Year;
"""

df_TotalRev = pd.read_sql(query, engine)
df_TotalRev


# In[87]:


query = """
SELECT YEAR(OrderDate) AS Year, AVG(TotalDue) AS AvgOrderValue
FROM SalesLT.SalesOrderHeader
GROUP BY YEAR(OrderDate)
ORDER BY Year;
"""

df_AvgOrderValue = pd.read_sql(query, engine)
df_AvgOrderValue


# In[88]:


best_sell_product = "SalesLT.BestSellingProduct;"
df_best_selling_pro = pd.read_sql(best_sell_product, engine)
df_best_selling_pro


# In[101]:


fig = px.bar(df_best_selling_pro, 
             x="ProductName", 
             y="TotalSales", 
             title="Top Selling Product Categories",
             color="TotalSales",
             text="TotalSales")

fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
fig.update_layout(height=600)
fig.show()


# In[91]:


best_freq_per_pro = "SalesLT.FrequentlyPurchasedProducts;"
df_best_freq_per_pro = pd.read_sql(best_freq_per_pro, engine)
df_best_freq_per_pro


# In[130]:


fig = px.bar(df_best_freq_per_pro,
             x="Product",
             y="OrderCount",
             title="Frequently Purchased Products",
             color="OrderCount",
             text="OrderCount",
             color_continuous_scale=px.colors.sequential.Cividis_r)

fig.update_layout(
    height=600,
    title_x=0.5,  # Center the title horizontally
    title_y=0.95, # Adjust vertical position if necessary
    title_font=dict(size=20)  # Adjust title font size if needed
)

fig.show()


# In[131]:


shppingdest = "SalesLT.ShoppingDestination;"
df_shppingdest = pd.read_sql(shppingdest, engine)
df_shppingdest


# In[151]:


fig = px.bar(df_shppingdest,
             x="City",
             y="NumberOfCustomers",
             title="Frequently Purchased Products",
             color="NumberOfCustomers",
             text="NumberOfCustomers",
             color_continuous_scale=px.colors.sequential.Cividis_r)

fig.update_layout(
    height=600,
    title_x=0.5,  # Center the title horizontally
    title_y=0.95, # Adjust vertical position if necessary
    title_font=dict(size=20)  # Adjust title font size if needed
)

fig.show()


# In[ ]:




