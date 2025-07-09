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
hd['opndate'] = pd.to_datetime(hd['opndate'],format='%Y-%m-%d').dt.date
hd['cash_in_date'] = pd.to_datetime(hd['cash_in_date'],format='%Y-%m-%d').dt.date
del hd['Unnamed: 0']


'''
Thống kê mô tả cơ bản
'''

'''
Mẫu dữ liệu
'''
st.table(hd.head(10))

'''
Mô tả thống kê
'''
hd_sta = hd.describe()

st.table(hd_sta)

hd.describe()
###############################
st.title("Phân bổ thời gian khách hàng nạp tiền vào tài khoản lần đầu")

fig = px.histogram(hd[hd['cashin_datediff']<=hd_sta['cashin_datediff']['75%']], x="cashin_datediff")

st.plotly_chart(fig, use_container_width=True)

###############################
st.title("Phân bổ giá trị tiền nạp vào tài khoản của khách hàng")

fig = px.histogram(hd[hd['cashin']<=hd_sta['cashin']['75%']], x="cashin")

st.plotly_chart(fig, use_container_width=True)

##############################
hd_cust = hd.groupby('cashin_datediff').agg(custodycd_count = ('custodycd','count'))
hd_cust.reset_index(inplace=True)
hd_cust_sta = hd_cust.describe()
hd_cust_sta.reset_index(inplace=True)
print(hd_cust_sta)

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

# --- Cấu hình trang ---
st.title("📊 Số lượng khách hàng nạp tiền vào tài khoản theo khoảng thời gian")

# --- Nút chọn dataset với mặc định ---
option = st.radio(
    "Chọn dataset để hiển thị:",
    ("Full", "75%"),
    index=0  # 👈 mặc định chọn "Full"
)

# --- Lọc dữ liệu và hiển thị chart ---
if option == "Full":
    filtered_df = hd_cust
    chart_title = "📈 Chart Full Dataset"
else:
    filtered_df = hd_cust[hd_cust["cashin_datediff"] >= hd_cust["custodycd_count"].quantile(0.75)]
    chart_title = "📉 Chart 75% Dataset"


fig = px.bar(filtered_df, x="cashin_datediff", y="custodycd_count", title= chart_title, )

st.plotly_chart(fig, use_container_width=True)


fig = px.scatter(x=[1,2,3], y=[4,5,6])
fig.write_html("plotly_chart.html")
st.plotly_chart(fig)

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