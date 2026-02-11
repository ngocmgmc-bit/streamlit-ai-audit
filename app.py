import streamlit as st
import os
import PyPDF2
from docx import Document
import pandas as pd
import tempfile

st.set_page_config(page_title="HỆ THỐNG CHẤM THẦU CHUYÊN GIA", layout="wide")

# =========================
# HÀM ĐỌC FILE
# =========================

def read_pdf(file_path):
    text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text


def read_docx(file_path):
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])


def read_files(uploaded_files):
    full_text = ""
    for file in uploaded_files:
        suffix = file.name.split(".")[-1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix="."+suffix) as tmp:
            tmp.write(file.read())
            tmp_path = tmp.name

        if suffix == "pdf":
            full_text += read_pdf(tmp_path)
        elif suffix == "docx":
            full_text += read_docx(tmp_path)

        os.remove(tmp_path)

    return full_text


# =========================
# GIAO DIỆN
# =========================

st.title("⚖️ HỆ THỐNG CHẤM THẦU CHUYÊN GIA")
st.caption("Chuẩn hóa theo Luật Đấu thầu & Thông tư 08/2022/TT-BKHĐT")

tab1, tab2 = st.tabs(["📂 Upload hồ sơ", "🧮 Phân tích & Chấm thầu"])

# =========================
# TAB UPLOAD
# =========================

with tab1:

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📁 Upload HSMT (nhiều file)")
        hsmt_files = st.file_uploader(
            "Chọn file HSMT",
            type=["pdf", "docx"],
            accept_multiple_files=True,
            key="hsmt"
        )

    with col2:
        st.subheader("📁 Upload HSDT (1 nhà thầu – nhiều file)")
        hsdt_files = st.file_uploader(
            "Chọn file HSDT",
            type=["pdf", "docx"],
            accept_multiple_files=True,
            key="hsdt"
        )

# =========================
# TAB CHẤM THẦU
# =========================

with tab2:

    st.subheader("🧮 Công cụ chấm thầu")

    if not hsmt_files or not hsdt_files:
        st.warning("Vui lòng upload đầy đủ HSMT và HSDT ở tab Upload.")
        st.stop()

    if st.button("⚖️ THỰC HIỆN CHẤM THẦU"):

        with st.spinner("Đang phân tích hồ sơ..."):

            hsmt_text = read_files(hsmt_files)
            hsdt_text = read_files(hsdt_files)

            # =========================
            # DANH SÁCH TIÊU CHÍ
            # =========================

            tieu_chi = [
                "Thông tin chung",
                "Điều kiện hợp lệ",
                "Năng lực và kinh nghiệm",
                "Đề xuất kỹ thuật",
                "Nhân sự chủ chốt",
                "Thiết bị",
                "Tiến độ thực hiện",
                "Đề xuất tài chính",
                "Điều kiện hợp đồng"
            ]

            ket_qua = []

            for i, tc in enumerate(tieu_chi, 1):

                yeu_cau = tc.lower() in hsmt_text.lower()
                co_noi_dung = tc.lower() in hsdt_text.lower()

                if yeu_cau and co_noi_dung:
                    ket_luan = "ĐẠT"
                    doi_chieu = "Có nội dung trong HSDT phù hợp tiêu chí HSMT"
                else:
                    ket_luan = "KHÔNG ĐẠT"
                    doi_chieu = "Không tìm thấy nội dung phù hợp hoặc thiếu nội dung"

                ket_qua.append({
                    "STT": i,
                    "Tiêu chí": tc,
                    "Yêu cầu có trong HSMT": "Có" if yeu_cau else "Không rõ",
                    "Nội dung có trong HSDT": "Có" if co_noi_dung else "Không",
                    "Đối chiếu": doi_chieu,
                    "Kết luận": ket_luan
                })

            df = pd.DataFrame(ket_qua)

            st.success("✅ Hoàn tất phân tích & đối chiếu")

            st.subheader("📊 BẢNG ĐỐI CHIẾU CHI TIẾT")
            st.dataframe(df, use_container_width=True)

            if (df["Kết luận"] == "KHÔNG ĐẠT").any():
                st.error("❌ KẾT LUẬN CHUNG: KHÔNG ĐẠT")
            else:
                st.success("✅ KẾT LUẬN CHUNG: ĐẠT")
