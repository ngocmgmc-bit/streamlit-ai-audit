import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
import pandas as pd

st.set_page_config(page_title="AI Audit – Chấm thầu", layout="wide")
st.title("📑 HỆ THỐNG CHẤM THẦU – TỔ CHUYÊN GIA")

# ==================================================
# HÀM ĐỌC FILE
# ==================================================
def extract_text(file):
    if file.name.lower().endswith(".pdf"):
        reader = PdfReader(file)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    elif file.name.lower().endswith(".docx"):
        doc = Document(file)
        return "\n".join(p.text for p in doc.paragraphs)
    return ""

# ==================================================
# SESSION STATE
# ==================================================
if "hsmt_files" not in st.session_state:
    st.session_state.hsmt_files = {}

if "criteria" not in st.session_state:
    st.session_state.criteria = []

if "hsdt_files" not in st.session_state:
    st.session_state.hsdt_files = {}

# ==================================================
# TABS
# ==================================================
tab1, tab2, tab3 = st.tabs([
    "1️⃣ Upload HSMT",
    "2️⃣ Gán tiêu chí đánh giá (Chương III)",
    "3️⃣ CHẤM THẦU – TỔ CHUYÊN GIA"
])

# ==================================================
# TAB 1 – UPLOAD HSMT
# ==================================================
with tab1:
    st.header("📘 Upload Hồ sơ mời thầu (HSMT)")

    hsmt_uploads = st.file_uploader(
        "Tải các file HSMT (PDF / DOCX)",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )

    if hsmt_uploads:
        for f in hsmt_uploads:
            if f.name not in st.session_state.hsmt_files:
                st.session_state.hsmt_files[f.name] = extract_text(f)

    if st.session_state.hsmt_files:
        fname = st.selectbox("Chọn file HSMT để xem", st.session_state.hsmt_files.keys())
        st.text_area("Nội dung HSMT", st.session_state.hsmt_files[fname], height=350)

# ==================================================
# TAB 2 – GÁN TIÊU CHÍ (CHƯƠNG III)
# ==================================================
with tab2:
    st.header("📌 Gán tiêu chí đánh giá theo Chương III – HSMT")

    with st.form("add_criteria"):
        col1, col2 = st.columns(2)

        with col1:
            group = st.selectbox(
                "Nhóm tiêu chí",
                [
                    "I. Điều kiện hợp lệ",
                    "II. Năng lực & kinh nghiệm",
                    "III. Yêu cầu kỹ thuật",
                    "IV. Nhân sự",
                    "V. Thiết bị",
                    "VI. Điều kiện hợp đồng"
                ]
            )
            name = st.text_input("Tên tiêu chí")

        with col2:
            required = st.selectbox(
                "Loại tiêu chí",
                ["BẮT BUỘC (Đạt/Không đạt)", "KHÔNG BẮT BUỘC"]
            )

        description = st.text_area("Mô tả yêu cầu (trích đúng HSMT)")

        submit = st.form_submit_button("➕ Thêm tiêu chí")

        if submit and name.strip():
            st.session_state.criteria.append({
                "group": group,
                "name": name,
                "description": description,
                "required": required
            })

    if st.session_state.criteria:
        st.subheader("📋 Danh sách tiêu chí đã nhập")
        st.dataframe(pd.DataFrame(st.session_state.criteria), use_container_width=True)

# ==================================================
# TAB 3 – CHẤM THẦU ĐÚNG MẪU TỔ CHUYÊN GIA
# ==================================================
with tab3:
    st.header("🧾 CHẤM THẦU THEO CHƯƠNG III – TỔ CHUYÊN GIA")

    hsdt_uploads = st.file_uploader(
        "Upload HSDT của các nhà thầu (PDF / DOCX)",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )

    if hsdt_uploads:
        for f in hsdt_uploads:
            st.session_state.hsdt_files[f.name] = extract_text(f)

    if not st.session_state.criteria or not st.session_state.hsdt_files:
        st.warning("⚠️ Cần có tiêu chí Chương III và HSDT để chấm thầu")
    else:
        results = []

        for bidder, hsdt_text in st.session_state.hsdt_files.items():
            for c in st.session_state.criteria:
                found = c["name"].lower() in hsdt_text.lower()
                result = "ĐẠT" if found else "KHÔNG ĐẠT"

                results.append({
                    "Nhà thầu": bidder,
                    "Nhóm tiêu chí": c["group"],
                    "Tiêu chí": c["name"],
                    "Bắt buộc": c["required"],
                    "Kết quả": result
                })

        df = pd.DataFrame(results)

        st.subheader("📊 BẢNG CHẤM THẦU CHI TIẾT")
        st.dataframe(df, use_container_width=True)

        st.subheader("✅ KẾT LUẬN KỸ THUẬT")

        ket_luan = (
            df[df["Bắt buộc"] == "BẮT BUỘC (Đạt/Không đạt)"]
            .groupby("Nhà thầu")["Kết quả"]
            .apply(lambda x: "ĐẠT" if "KHÔNG ĐẠT" not in x.values else "KHÔNG ĐẠT")
            .reset_index()
        )

        st.dataframe(ket_luan, use_container_width=True)
