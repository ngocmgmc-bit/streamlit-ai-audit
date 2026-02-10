# =========================
# APP CHẤM THẦU CHUYÊN GIA
# =========================

import streamlit as st

# =========================
# 1. CẤU HÌNH GIAO DIỆN CHUNG
# =========================
st.set_page_config(
    page_title="HỆ THỐNG CHẤM THẦU CHUYÊN GIA",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
    .main-title {
        font-size:28px;
        font-weight:700;
        color:#003366;
    }
    .sub-title {
        font-size:16px;
        color:#555;
    }
    .block-box {
        padding:20px;
        border-radius:10px;
        background:#f8f9fa;
        border:1px solid #ddd;
        margin-bottom:15px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>HỆ THỐNG CHẤM THẦU CHUYÊN GIA</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Chuẩn hóa theo Luật Đấu thầu & Thông tư 08/2022/TT-BKHĐT</div>", unsafe_allow_html=True)
st.divider()

# =========================
# 2. KHỞI TẠO GEMINI (BỌC AN TOÀN – KHÔNG CRASH)
# =========================
gemini_ready = False
model = None

try:
    from google import genai
    import os

    if "GEMINI_API_KEY" in st.secrets:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        model = client.models.get("gemini-1.5-flash")
        gemini_ready = True
    else:
        st.warning("⚠️ Chưa cấu hình GEMINI_API_KEY")

except Exception as e:
    st.warning("⚠️ Gemini AI chưa sẵn sàng – App vẫn chạy bình thường")

# =========================
# 3. SIDEBAR – ĐIỀU HƯỚNG
# =========================
with st.sidebar:
    st.header("📁 Chức năng")
    menu = st.radio(
        "",
        [
            "📤 Upload hồ sơ dự thầu",
            "📑 Phân tích & chấm thầu",
            "📄 Xuất báo cáo Word",
            "ℹ️ Thông tin hệ thống"
        ]
    )

# =========================
# 4. UPLOAD HỒ SƠ (1 HSDT – NHIỀU FILE)
# =========================
if menu == "📤 Upload hồ sơ dự thầu":
    st.subheader("📤 Upload hồ sơ dự thầu")
    st.markdown("<div class='block-box'>", unsafe_allow_html=True)

    files = st.file_uploader(
        "Chọn các file của **01 hồ sơ dự thầu** (PDF, DOCX, XLSX)",
        type=["pdf", "docx", "xlsx"],
        accept_multiple_files=True
    )

    if files:
        st.success(f"Đã nhận {len(files)} file hồ sơ")
        st.session_state["hsdt_files"] = files

    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# 5. CHẤM THẦU (GIỮ LOGIC CŨ – CHỈ GỌI)
# =========================
elif menu == "📑 Phân tích & chấm thầu":
    st.subheader("📑 Phân tích & chấm thầu")

    if "hsdt_files" not in st.session_state:
        st.warning("⚠️ Chưa upload hồ sơ")
    else:
        st.markdown("<div class='block-box'>", unsafe_allow_html=True)

        if st.button("▶ Thực hiện chấm thầu"):
            with st.spinner("Đang phân tích hồ sơ..."):
                # 🔴 GIỮ NGUYÊN LOGIC CHẤM THẦU CŨ Ở ĐÂY
                # ví dụ:
                # result = cham_thau(hsmt, hsdt_files)

                st.success("✔ Chấm thầu hoàn tất")
                st.session_state["ket_qua"] = "KẾT QUẢ CHẤM THẦU (GIẢ LẬP)"

        st.markdown("</div>", unsafe_allow_html=True)

# =========================
# 6. XUẤT WORD (THEO MẪU BỘ KHĐT)
# =========================
elif menu == "📄 Xuất báo cáo Word":
    st.subheader("📄 Xuất báo cáo Word")

    if "ket_qua" not in st.session_state:
        st.warning("⚠️ Chưa có kết quả chấm thầu")
    else:
        st.markdown("<div class='block-box'>", unsafe_allow_html=True)
        st.info("📌 Xuất báo cáo tổng hợp theo mẫu Bộ KHĐT (Thông tư 08)")
        st.button("⬇ Xuất file Word")
        st.markdown("</div>", unsafe_allow_html=True)

# =========================
# 7. THÔNG TIN HỆ THỐNG
# =========================
else:
    st.subheader("ℹ️ Thông tin hệ thống")
    st.markdown("""
    - Chấm **01 hồ sơ – nhiều file**
    - Kỹ thuật & tài chính: **xử lý độc lập**
    - Chuẩn Luật Đấu thầu Việt Nam
    - Có thể vận hành **không phụ thuộc AI**
    """)

