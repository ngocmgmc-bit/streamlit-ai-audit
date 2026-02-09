import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
import pandas as pd
import io

st.set_page_config(page_title="AI Audit HSMT – Chấm thầu", layout="wide")

# =========================
# HÀM ĐỌC FILE
# =========================
def read_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"
    return text

def read_docx(file):
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs])

def extract_text(file):
    if file.name.lower().endswith(".pdf"):
        return read_pdf(file)
    elif file.name.lower().endswith(".docx"):
        return read_docx(file)
    else:
        return ""

# =========================
# SESSION STATE
# =========================
if "hsmt_files" not in st.session_state:
    st.session_state.hsmt_files = {}

if "hsdt_files" not in st.session_state:
    st.session_state.hsdt_files = {}

if "criteria" not in st.session_state:
    st.session_state.criteria = []

# =========================
# GIAO DIỆN
# =========================
st.title("📑 AI AUDIT HSMT – CHẤM THẦU TỰ ĐỘNG")

tab1, tab2, tab3 = st.tabs([
    "1️⃣ Upload & Tách HSMT",
    "2️⃣ Gán nhãn tiêu chí HSMT",
    "3️⃣ Upload HSDT & Chấm thầu"
])

# =========================
# TAB 1 – UPLOAD HSMT
# =========================
with tab1:
    st.header("Upload Hồ sơ mời thầu (HSMT)")
    hsmt_upload = st.file_uploader(
        "Upload các file HSMT (PDF/DOCX)",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )

    if hsmt_upload:
        for f in hsmt_upload:
            content = extract_text(f)
            st.session_state.hsmt_files[f.name] = content

    if st.session_state.hsmt_files:
        st.success("✅ Đã tách nội dung HSMT theo từng file")
        file_names = list(st.session_state.hsmt_files.keys())
        selected = st.selectbox("Chọn file HSMT để xem", file_names)
        st.text_area(
            f"Nội dung: {selected}",
            st.session_state.hsmt_files[selected],
            height=350
        )

# =========================
# TAB 2 – GÁN NHÃN HSMT
# =========================
with tab2:
    st.header("Gán nhãn tiêu chí đánh giá theo HSMT")

    st.info("Gán tiêu chí CHUẨN THEO HỒ SƠ MỜI THẦU – dùng cho chấm thầu")

    with st.form("criteria_form"):
        col1, col2 = st.columns(2)
        with col1:
            criterion = st.text_input("Tên tiêu chí (VD: Doanh thu bình quân)")
        with col2:
            group = st.selectbox(
                "Nhóm tiêu chí",
                [
                    "A. Thông tin chung",
                    "B. Điều kiện hợp lệ",
                    "C. Năng lực & kinh nghiệm",
                    "D. Đề xuất kỹ thuật",
                    "E. Nhân sự",
                    "F. Thiết bị",
                    "G. Tài chính",
                    "H. Điều kiện hợp đồng"
                ]
            )

        description = st.text_area("Mô tả / yêu cầu theo HSMT")
        required = st.checkbox("Tiêu chí bắt buộc (Đạt / Không đạt)", value=True)

        submitted = st.form_submit_button("➕ Thêm tiêu chí")

        if submitted and criterion:
            st.session_state.criteria.append({
                "group": group,
                "criterion": criterion,
                "description": description,
                "required": required
            })

    if st.session_state.criteria:
        df = pd.DataFrame(st.session_state.criteria)
        st.subheader("Danh sách tiêu chí đã gán")
        st.dataframe(df, use_container_width=True)

# =========================
# TAB 3 – UPLOAD HSDT & CHẤM THẦU
# =========================
with tab3:
    st.header("Upload HSDT & Chấm thầu")

    hsdt_upload = st.file_uploader(
        "Upload HSDT của các nhà thầu (PDF/DOCX)",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        key="hsdt"
    )

    if hsdt_upload:
        for f in hsdt_upload:
            content = extract_text(f)
            st.session_state.hsdt_files[f.name] = content

    if st.session_state.hsdt_files and st.session_state.criteria:
        st.success("✅ Sẵn sàng chấm thầu")

        results = []

        for bidder, hsdt_text in st.session_state.hsdt_files.items():
            for c in st.session_state.criteria:
                matched = c["criterion"].lower() in hsdt_text.lower()
                results.append({
                    "Nhà thầu": bidder,
                    "Nhóm": c["group"],
                    "Tiêu chí": c["criterion"],
                    "Bắt buộc": "Có" if c["required"] else "Không",
                    "Kết quả": "Đạt" if matched else "Không đạt"
                })

        df_result = pd.DataFrame(results)
        st.subheader("📊 KẾT QUẢ CHẤM THẦU (SOI THEO HSMT)")
        st.dataframe(df_result, use_container_width=True)

        # Tổng hợp
        summary = (
            df_result[df_result["Bắt buộc"] == "Có"]
            .groupby("Nhà thầu")["Kết quả"]
            .apply(lambda x: "ĐẠT" if "Không đạt" not in x.values else "KHÔNG ĐẠT")
            .reset_index()
        )
        summary.columns = ["Nhà thầu", "Kết luận sơ bộ"]

        st.subheader("✅ KẾT LUẬN SƠ BỘ")
        st.dataframe(summary, use_container_width=True)

    else:
        st.warning("⚠️ Cần upload HSMT, gán tiêu chí và upload HSDT để chấm thầu")
