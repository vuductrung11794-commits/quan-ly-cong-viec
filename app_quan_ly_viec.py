import streamlit as st
import pandas as pd
from datetime import datetime

# Cấu hình giao diện trang web
st.set_page_config(page_title="Trợ Lý Điều Phối Công Việc", layout="wide")

st.title("🎯 Bảng Điều Phối & Phân Tích Công Việc")
st.caption("Tự động đồng bộ từ Google Sheets • Phân loại theo Ma trận Eisenhower & PARA")

# 1. Cấu hình kết nối Google Sheets từ Sheet ID của bạn
SHEET_ID = "1RxC_2UqrS4MlI1o51tyA9TDLISTFCKBeQuM_XSWYZEQ"
SHEET_NAME = "Tasks"
URL_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

# 2. Hàm đọc và xử lý dữ liệu
@st.cache_data(ttl=60)  # Tự động làm mới dữ liệu sau mỗi 60 giây
def tai_du_lieu():
    df = pd.read_csv(URL_CSV)
    # Lọc bỏ hàng trống và các việc đã hoàn thành
    df = df.dropna(subset=['Cong_Viec'])
    df = df[df['Trang_Thai'] != 'Hoàn thành']
    
    # Chuẩn hóa thời gian và tính số ngày còn lại đến hạn chót
    df['Han_Chot'] = pd.to_datetime(df['Han_Chot'])
    ngay_hien_tai = pd.to_datetime(datetime.today().strftime('%Y-%m-%d'))
    df['So_Ngay_Con'] = (df['Han_Chot'] - ngay_hien_tai).dt.days
    
    # Chuẩn hóa cột Quan_Trong về dạng Boolean (True/False)
    df['Quan_Trong'] = df['Quan_Trong'].astype(str).str.upper().map({'TRUE': True, 'FALSE': False}).fillna(False)
    return df

try:
    df = tai_du_lieu()
except Exception as e:
    st.error("Không thể kết nối đến Google Sheets. Hãy đảm bảo bạn đã bật quyền 'Bất kỳ ai có đường liên kết đều có thể xem' trên Google Sheet.")
    st.stop()

# 3. Phân loại theo Ma trận Eisenhower (Mốc khẩn cấp: còn <= 3 ngày)
o1_khan_cap_quan_trong = df[(df['Quan_Trong'] == True) & (df['So_Ngay_Con'] <= 3)]
o2_quan_trong_khong_khan = df[(df['Quan_Trong'] == True) & (df['So_Ngay_Con'] > 3)]
o3_khan_khong_quan_trong = df[(df['Quan_Trong'] == False) & (df['So_Ngay_Con'] <= 3)]
o4_khong_khan_khong_quan = df[(df['Quan_Trong'] == False) & (df['So_Ngay_Con'] > 3)]

# 4. Thẻ số liệu tổng quan
c1, c2, c3, c4 = st.columns(4)
c1.metric("🚨 Ô 1: Làm ngay", f"{len(o1_khan_cap_quan_trong)} việc")
c2.metric("📅 Ô 2: Lên lịch", f"{len(o2_quan_trong_khong_khan)} việc")
c3.metric("🤝 Ô 3: Xử lý nhanh", f"{len(o3_khan_khong_quan_trong)} việc")
c4.metric("📁 Ô 4: Khi rảnh", f"{len(o4_khong_khan_khong_quan)} việc")

st.markdown("---")

# 5. Bố cục trực quan 4 ô Ma trận
col_trai, col_phai = st.columns(2)

with col_trai:
    st.subheader("🚨 Ô 1: Quan trọng & Khẩn cấp (Làm ngay)")
    if o1_khan_cap_quan_trong.empty:
        st.success("Không có công việc nào bị quá hạn hoặc cận kề deadline!")
    else:
        for _, row in o1_khan_cap_quan_trong.iterrows():
            st.error(f"**{row['Cong_Viec']}**  \n📁 Nhóm: `{row['Nhom_PARA']}` | ⏳ Còn: **{row['So_Ngay_Con']} ngày** (Hạn: {row['Han_Chot'].strftime('%d/%m/%Y')})")

    st.subheader("🤝 Ô 3: Khẩn cấp nhưng Không quan trọng")
    if o3_khan_khong_quan_trong.empty:
        st.info("Trống.")
    else:
        for _, row in o3_khan_khong_quan_trong.iterrows():
            st.warning(f"**{row['Cong_Viec']}**  \n📁 Nhóm: `{row['Nhom_PARA']}` | ⏳ Còn: {row['So_Ngay_Con']} ngày")

with col_phai:
    st.subheader("📅 Ô 2: Quan trọng nhưng Không khẩn cấp (Trọng tâm dài hạn)")
    if o2_quan_trong_khong_khan.empty:
        st.info("Trống.")
    else:
        for _, row in o2_quan_trong_khong_khan.iterrows():
            st.info(f"**{row['Cong_Viec']}**  \n📁 Nhóm: `{row['Nhom_PARA']}` | ⏳ Còn: {row['So_Ngay_Con']} ngày")

    st.subheader("📁 Ô 4: Không quan trọng & Không khẩn cấp")
    if o4_khong_khan_khong_quan.empty:
        st.caption("Trống.")
    else:
        for _, row in o4_khong_khan_khong_quan.iterrows():
            st.write(f"- {row['Cong_Viec']} (`{row['Nhom_PARA']}`)")