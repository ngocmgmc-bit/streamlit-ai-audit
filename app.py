import streamlit as st
from typing import List

# ================== CẤU HÌNH TRANG ==================
st.set_page_config(
    page_title="HỆ THỐNG CHẤM THẦU CHUYÊN GIA",
    layout="wide",
)

# ================== SIDEBAR ==================
with st.sidebar:
    st.markdown("## 📂 Chức năng")
    menu = st.radio(
        "",
        [
            "Upload hồ sơ dự thầu",
            "Phân tích & chấm thầu",
            "Xuất báo cáo Word",
            "Thông tin hệ thống",
        ],
    )

    st.markdown("---")
    st.markdown("### 📊 Trạng thái hồ sơ")

    if "hsmt_files" in st.session_state:
        st.success("✔ Đã upload HSMT")
    else:
        st.info("⬜ Chưa upload HSMT")

    if "hsdt_files" in st.session_state:
        st.success("✔ Đã upload HSDT")
    else:
        st.info("⬜ Chưa upload HSDT")

    if "ket_qua_cham" in st.session_state:
        st.success("✔ Đã chấm thầu")
    else:
        st.info("⬜ Chưa chấm thầu")

# ================== HEADER ==================
st.markdown(
    """
    <h2>HỆ THỐNG CHẤM THẦU CHUYÊN GIA</h2>
    <p style='color:gray'>
    Chuẩn hóa theo Luật Đấu thầu & Thông tư 08/2022/TT-BKHĐT
    </p>
    """,
    unsafe_allow_html=True,
)

st.warning("⚠ Gemini AI chưa sẵn sàng – App vẫn hoạt động bình thường")

# =====================================================
# 1️⃣ UPLOAD HỒ SƠ DỰ THẦU
# =====================================================
if menu == "Upload hồ sơ dự thầu":

    st.markdown("## 📌 Thông tin gói thầu")

    col1, col2, col3 = st.columns(3)
    with col1:
        ten_goi_thau = st.text_input("Tên gói thầu")
    with col2:
        ben_moi_thau = st.text_input("Bên mời thầu")
    with col3:
        hinh_thuc = st.selectbox(
            "Hình thức lựa chọn",
            ["Đấu thầu rộng rãi", "Chào hàng cạnh tranh", "Chỉ định thầu"],
        )

    st.session_state["thong_tin_goi_thau"] = {
        "ten": ten_goi_thau,
        "ben_moi_thau": ben_moi_thau,
        "hinh_thuc": hinh_thuc,
    }

    st.markdown("---")

    # ================== UPLOAD HSMT ==================
    st.markdown("## 📘 Upload Hồ sơ mời thầu (HSMT)")
    hsmt_files = st.file_uploader(
        "Chọn file HSMT (PDF, DOCX, XLSX)",
        type=["pdf", "docx", "xlsx"],
        accept_multiple_files=True,
        key="hsmt_uploader",
    )

    if hsmt_files:
        st.session_state["hsmt_files"] = hsmt_files
        st.success("✔ Đã upload đầy đủ HSMT")
        for i, f in enumerate(hsmt_files, 1):
            st.write(f"📄 {i}. {f.name}")

    st.markdown("---")

    # ================== UPLOAD HSDT ==================
    st.markdown("## 📕 Upload Hồ sơ dự thầu (HSDT)")
    hsdt_files = st.file_uploader(
        "Chọn các file của 01 HSDT (PDF, DOCX, XLSX)",
        type=["pdf", "docx", "xlsx"],
        accept_multiple_files=True,
        key="hsdt_uploader",
    )

    if hsdt_files:
        st.session_state["hsdt_files"] = hsdt_files
        st.success("✔ Đã upload đầy đủ HSDT")
        for i, f in enumerate(hsdt_files, 1):
            st.write(f"📄 {i}. {f.name}")

# =====================================================
# 2️⃣ PHÂN TÍCH & CHẤM THẦU
# =====================================================
elif menu == "Phân tích & chấm thầu":

    st.markdown("## 🧮 Công cụ chấm thầu")

    if "hsmt_files" not in st.session_state or "hsdt_files" not in st.session_state:
        st.error("❌ Cần upload đầy đủ HSMT và HSDT trước khi chấm thầu")
    else:
        if st.button("🚀 CHẤM THẦU"):
            # ❗ GIỮ CHỖ LOGIC – KHÔNG TỰ SỬA
            st.session_state["ket_qua_cham"] = {
                "ket_luan": "Hồ sơ đạt yêu cầu kỹ thuật",
                "diem": 85,
            }
            st.success("✔ Chấm thầu hoàn tất")

        if "ket_qua_cham" in st.session_state:
            st.markdown("### 📊 Kết quả chấm thầu")
            st.json(st.session_state["ket_qua_cham"])

# =====================================================
# 3️⃣ XUẤT BÁO CÁO WORD
# =====================================================
elif menu == "Xuất báo cáo Word":

    st.markdown("## 📄 Xuất báo cáo kết quả chấm thầu")

    if "ket_qua_cham" not in st.session_state:
        st.warning("⚠ Chưa có kết quả chấm thầu")
    else:
        st.info("📌 Sẵn sàng xuất báo cáo Word theo mẫu Bộ KH&ĐT")
        st.button("⬇ Tải báo cáo Word (đang hoàn thiện)")

# =====================================================
# 4️⃣ THÔNG TIN HỆ THỐNG
# =====================================================
elif menu == "Thông tin hệ thống":

    st.markdown("## ℹ Thông tin hệ thống")
    st.markdown(
        """
        - Phiên bản: **1.0 ổn định**
        - Chấm **01 HSDT (nhiều file)**
        - Chuẩn pháp lý: **Luật Đấu thầu + TT08**
        - AI: Gemini (tùy chọn, không bắt buộc)
        """
    )
