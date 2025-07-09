import streamlit as st
import pandas as pd
from OOP_redshit import *
import plotly.express as px
import hashlib

import os

# Bật chế độ wide mode
st.set_page_config(layout="wide")

# def calc_md5(row):
#     concat_str = ''.join(map(str, row.values))
#     return hashlib.md5(concat_str.encode()).hexdigest()

# def check_data(list,x_df,y_df):
#     xy_df = pd.DataFrame()
#     try:
#         x_df_hash = x_df[x_df['md5_hash'].isin(list)]
#         y_df_hash = y_df[y_df['md5_hash'].isin(list)]
#     except:
#         x_df_hash = pd.DataFrame()
#         y_df_hash = pd.DataFrame()
    
#     xy_df = pd.concat([xy_df,x_df_hash,y_df_hash])
#     return xy_df

# proc = coreconn(
#                     host= 'prod-redshift-cluster.cuxeoz0lhusr.ap-southeast-1.redshift.amazonaws.com',
#                     database= 'vpbanks_dwh',
#                     user='hieudd',
#                     password='Ani#2024'
#                )

# krx = coreconn(
#                     host= 'prod-redshift-cluster.cuxeoz0lhusr.ap-southeast-1.redshift.amazonaws.com',
#                     database= 'vpbanks_dwh_krx',
#                     user='hieudd',
#                     password='Ani#2024'
#               )

# uat = coreconn(
#                     host= 'uat-redshift-cluster.cuxeoz0lhusr.ap-southeast-1.redshift.amazonaws.com',
#                     database= 'vpbanks_dwh_krx',
#                     user='staging',
#                     password='Asc12345'
#             )

# q2 = ''' 
# with 
# 	cus_invest as
# 		(
# 			select custid, bond_custid, custodycd, bond_custodycd, opndate,fullname, openvia
# 			from dwh.smy_dwh_account_quantity_dv
# 			where openvia = 'NEO_Invest' and status = 'A'
# 		)
# 	,cash_in_info as 
# 		(
# 			select
# 			--	*
# 				ci.txdate cash_in_date
# 				, cf.custodycd
# 				, ci.acctno 
# 			--	, ci.tltxcd
# 			--	, ci.namt
# 				, nvl(sum(case when ci.tltxcd = '1141' then ci.namt end), 0) cashin
# --				, nvl(sum(case when ci.tltxcd = '1104' then ci.namt end), 0) cashout
# 				,dense_rank () over (partition by cf.custodycd, ci.acctno order by ci.txdate) daterank
# 			from staging.stg_flex_citrana ci
# 			left join staging.stg_flex_afmast af 			on ci.acctno = af.acctno
# 			left join staging.stg_flex_cfmast cf 			on af.custid = cf.custid
# 			left join cus_invest cs							on cf.custodycd = cs.custodycd 
# 			where 	
# 				(
# 					(ci.tltxcd = '1141' and ci.txcd = '0012') 
# 					or (ci.tltxcd = '1104' and ci.txcd = '0043')
# 				) --1141: nap, 1104: rut 
# 			group by ci.txdate,cf.custodycd, ci.acctno
# 		)
# 	,df as 
# 		(
# 			select ci.opndate, cif.*
#        			, datediff(day,ci.opndate,cif.cash_in_date) cashin_datediff
# 			from cash_in_info cif
# 			join cus_invest ci 			on cif.custodycd = ci.custodycd
# 			where 
# 				cif.daterank = 1 and cif.cashin >= 1e6		
# 		)
# 	,df_dated_quartile as
# 		(
# 			select
# 			    (
# 			        SELECT cashin_datediff
# 			        FROM df
# 			        GROUP BY cashin_datediff
# 			        ORDER BY COUNT(*) DESC
# 			        LIMIT 1
# 			    ) AS Mode
# 				,avg(cashin_datediff) as mean_cd
# 			    ,MIN(cashin_datediff) AS min_cd
# 			    ,PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY cashin_datediff) AS Q1
# 			    ,PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY cashin_datediff) AS Median
# 			    ,PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY cashin_datediff) AS Q3
# 			    ,MAX(cashin_datediff) AS max_cd
# 			FROM df
# 		)
# select * 
# from df
#      '''
          
# hd = krx.selectdf(q2)

# hd['opndate'] = hd['opndate'].dt.date
# hd['cash_in_date'] = hd['cash_in_date'].dt.date

# hd.to_csv(r'D:\VPBanks\python_code\acc_check_pj\job_pt.csv')

# uat.disconnect()
# proc.disconnect()
# krx.disconnect()

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