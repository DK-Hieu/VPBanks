import streamlit as st
import pandas as pd
# from OOP_redshit import *
import plotly.express as px
import hashlib

import os

# Bật chế độ wide mode
st.set_page_config(layout="wide")

# Lấy dữ liệu 
DIR = os.path.dirname(__file__)
csv_path = os.path.join(DIR, "job_pt.csv")

hd = pd.read_csv(csv_path)
hd['opndate'] = pd.to_datetime(hd['opndate'],format='%Y-%m-%d')
hd['cash_in_date'] = pd.to_datetime(hd['cash_in_date'],format='%Y-%m-%d')
del hd['Unnamed: 0']

st.title('Phân tích cơ bản Khoảng thời gian user nạp tiền lần đầu với Neo Invest')

st.header('Mẫu dữ liệu')
st.table(hd.head(5))

###############################
st.header("📊 Số lượng khách hàng nạp tiền vào tài khoản theo khoảng thời gian")

hd_cust = hd.groupby('cashin_datediff').agg(custodycd_count = ('custodycd','nunique'))
hd_cust.reset_index(inplace=True)
hd_cust_sta = hd_cust.describe()
hd_cust_sta.reset_index(inplace=True)

hd_cust_table = hd_cust.copy()
hd_cust_table.sort_values(by='custodycd_count',ascending=False,inplace=True)
hd_cust_table.rename(columns={'cashin_datediff':'Thời gian đợi (Ngày)','custodycd_count':'Số lượng khách hàng'},inplace=True)

# --- Nút chọn dataset với mặc định ---
option = st.radio(
    "Chọn dataset để hiển thị:",
    ("Full", "10 ngày đầu tiên "),
    index=0  # 👈 mặc định chọn "Full"
)

# --- Lọc dữ liệu và hiển thị chart ---
if option == "Full":
    filtered_df = hd_cust
    chart_title = "📈 Chart Full Dataset"
else:
    filtered_df = hd_cust[hd_cust["cashin_datediff"] <= 10]
    chart_title = "📉 Chart 75% Dataset"

fig = px.bar(filtered_df, x="cashin_datediff", y="custodycd_count", title= chart_title)

st.plotly_chart(fig, use_container_width=True)

st.table(hd_cust_table.head(10))

# ###############################
st.header("Phân bổ giá trị tiền nạp lần đầu của khách hàng")

hd_sta = hd.describe()

fig = px.histogram(hd[hd['cashin']<=hd_sta['cashin']['75%']], x="cashin")

st.plotly_chart(fig, use_container_width=True)

# ###############################
st.header(" Độ tương quan giữa thời gian chờ khách nạp lần đầu vs giá trị tiền nạp lần đầu")

hd_cash_date = hd[hd['cashin'] <= 10*10**9][['custodycd','cashin','cashin_datediff']]

# --- Nút chọn dataset với mặc định ---
option = st.radio(
    "Chọn dataset để hiển thị:",
    ("Full", "Filter (max 10B)"),
    index=1  # 👈 mặc định chọn "Full"
)

# --- Lọc dữ liệu và hiển thị chart ---
if option == "Full":
    filtered_df = hd
    chart_title = "📈 Chart Full Dataset"
else:
    filtered_df = hd_cash_date
    chart_title = "📉 Chart Filter with max value 10x10^9 Dataset"
    
fig = px.scatter(filtered_df, x="cashin_datediff", y="cashin",title= chart_title)

st.plotly_chart(fig, use_container_width=True)

# ##############################

hd_time_year = hd[['opndate','custodycd','cashin','cashin_datediff']]
hd_time_year['yeardf'] = hd_time_year['opndate'].dt.year
hd_time_year.sort_values(by='yeardf', ascending=True,inplace=True)
hd_time_year['yeardf'] = hd_time_year['yeardf'].astype('str')
hd_time_year = hd_time_year[hd_time_year['cashin'] <= 10*10**9]



st.header("Phân bố thời gian chờ qua từng năm")
fig = px.box(hd_time_year, x="cashin_datediff", color="yeardf")

st.plotly_chart(fig, use_container_width=True)

st.header("Phân bố giá trị nạp tiền lần đầu của khách hàng qua từng năm")
fig = px.box(hd_time_year, x="cashin", color="yeardf")

st.plotly_chart(fig, use_container_width=True)

# fig = px.box(df, x="time", y="total_bill")
# st.plotly_chart(fig, use_container_width=True)

# --- Nút chọn dữ liệu ---
# col1, col2 = st.columns(2)
# with col1:
#     if st.button("📈 Full"):
#         filtered_df = hd_cust  # Dùng toàn bộ dữ liệu
#         chart_title = "📈 Chart Full Dataset"
# with col2:
#     if st.button("📉 75%"):
#         filtered_df = hd_cust[hd_cust["custodycd_count"] >= hd_cust["custodycd_count"].quantile(0.75)]  # Dữ liệu <= 75th percentile
#         chart_title = "📉 Chart 75% Dataset"

# # --- Nút Export ---
# st.markdown("---")
# if st.button("📥 Export HTML"):
#     try:
#         # Lấy toàn bộ HTML hiện tại (Streamlit >= 1.33)
#         html_code = st.query_params.get_all()

#         # Ghi ra file
#         with open("exported_app.html", "w", encoding="utf-8") as f:
#             f.write(html_code)

#         st.success("✅ Trang đã được export ra file `exported_app.html`!")
#         # Hiển thị nút tải file
#         with open("exported_app.html", "r", encoding="utf-8") as f:
#             st.download_button("📥 Tải file exported_app.html", data=f, file_name="exported_app.html")
#     except Exception as e:
#         st.error(f"❌ Lỗi export: {e}")