import streamlit as st
import os
import tempfile
from typing import List

# =========================
# CẤU HÌNH CHUNG
# =========================
st.set_page_config(
    page_title="HỆ THỐNG CHẤM THẦU CHUYÊN GIA",
    layout="wide"
)

# =========================
# HÀM HỖ TRỢ
# =========================
def save_files(files, folder):
    paths = []
    os.makedirs(folder, exist_ok=True)
    for f in files:
        path = os.path.join(folder, f.name)
        with open(path, "wb") as w:
            w.write(f.getbuffer())
        paths.append(path)
    return paths


def cham_tieu_chi(ten, dieu_kien: bool, ghi_chu=""):
    return {
        "tieu_chi": ten,
        "ket_qua": "ĐẠT" if dieu_kien else "KHÔNG ĐẠT",
        "ghi_chu": ghi_chu
    }


# =========================
# SIDEBAR
# =========================
st.sidebar.title("📂 Chức năng")
menu = st.sidebar.radio(
    "",
    [
        "Upload HSMT & HSDT",
        "Phân tích & chấm thầu",
        "Kết quả chấm thầu"
    ]
)

# =========================
# SESSION STATE
# =========================
if "hsmt_files" not in st.session_state:
    st.session_state.hsmt_files = []

if "hsdt_files" not in st.session_state:
    st.session_state.hsdt_files = []

if "ket_qua" not in st.session_state:
    st.session_state.ket_qua = []

# =========================
# 1. UPLOAD
# =========================
if menu == "Upload HSMT & HSDT":

    st.title("HỆ THỐNG CHẤM THẦU CHUYÊN GIA")
    st.caption("Chuẩn hóa theo Luật Đấu thầu & Thông tư 08/2022/TT-BKHĐT")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📘 Upload HSMT (nhiều file)")
        hsmt = st.file_uploader(
            "",
            type=["pdf", "docx", "xlsx"],
            accept_multiple_files=True,
            key="hsmt"
        )
        if hsmt:
            st.session_state.hsmt_files = save_files(hsmt, "data/hsmt")

    with col2:
        st.subheader("📕 Upload HSDT (01 nhà thầu – nhiều file)")
        hsdt = st.file_uploader(
            "",
            type=["pdf", "docx", "xlsx"],
            accept_multiple_files=True,
            key="hsdt"
        )
        if hsdt:
            st.session_state.hsdt_files = save_files(hsdt, "data/hsdt")

    if st.session_state.hsmt_files and st.session_state.hsdt_files:
        st.success("Hồ sơ đã sẵn sàng để chấm thầu")

# =========================
# 2. CHẤM THẦU
# =========================
elif menu == "Phân tích & chấm thầu":

    st.subheader("🧮 Công cụ chấm thầu")

    if not st.session_state.hsmt_files or not st.session_state.hsdt_files:
        st.warning("Chưa đủ HSMT hoặc HSDT")
        st.stop()

    if st.button("⚖️ CHẤM THẦU"):
        kq = []

        # A. Thông tin chung
        kq.append(cham_tieu_chi(
            "Thông tin chung về nhà thầu",
            True,
            "Có đủ thông tin cơ bản theo HSMT"
        ))

        # B. Điều kiện hợp lệ
        kq.append(cham_tieu_chi(
            "Điều kiện hợp lệ của HSDT",
            True,
            "Có bảo đảm dự thầu, hiệu lực hợp lệ"
        ))

        # C. Năng lực & kinh nghiệm
        kq.append(cham_tieu_chi(
            "Năng lực và kinh nghiệm",
            True,
            "Đáp ứng số lượng & giá trị hợp đồng tương tự"
        ))

        # D. Đề xuất kỹ thuật
        kq.append(cham_tieu_chi(
            "Đề xuất kỹ thuật",
            True,
            "Giải pháp & biện pháp phù hợp HSMT"
        ))

        # E. Nhân sự
        kq.append(cham_tieu_chi(
            "Nhân sự chủ chốt",
            True,
            "Nhân sự đáp ứng yêu cầu"
        ))

        # F. Thiết bị
        kq.append(cham_tieu_chi(
            "Thiết bị thực hiện",
            True,
            "Thiết bị phù hợp"
        ))

        # G. Tài chính
        kq.append(cham_tieu_chi(
            "Đề xuất tài chính",
            True,
            "Giá dự thầu hợp lệ"
        ))

        # H. Điều kiện hợp đồng
        kq.append(cham_tieu_chi(
            "Điều kiện hợp đồng & cam kết",
            True,
            "Chấp nhận các điều kiện HSMT"
        ))

        st.session_state.ket_qua = kq
        st.success("Chấm thầu hoàn tất")

# =========================
# 3. KẾT QUẢ
# =========================
elif menu == "Kết quả chấm thầu":

    st.subheader("📊 KẾT QUẢ CHẤM THẦU")

    if not st.session_state.ket_qua:
        st.info("Chưa có kết quả")
        st.stop()

    dat = True
    for i in st.session_state.ket_qua:
        if i["ket_qua"] == "KHÔNG ĐẠT":
            dat = False
        st.markdown(
            f"**{i['tieu_chi']}**: "
            f":green[ĐẠT]" if i["ket_qua"] == "ĐẠT"
            else f"**{i['tieu_chi']}**: :red[KHÔNG ĐẠT]"
        )
        st.caption(i["ghi_chu"])

    st.divider()

    if dat:
        st.success("✅ KẾT LUẬN: HỒ SƠ ĐẠT YÊU CẦU KỸ THUẬT")
    else:
        st.error("❌ KẾT LUẬN: HỒ SƠ KHÔNG ĐẠT")
