import streamlit as st
import pdfplumber
from docx import Document

# ========= HÀM ĐỌC FILE =========
def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    return text

def read_docx(file):
    doc = Document(file)
    return "\n".join(p.text for p in doc.paragraphs)

def read_file(file):
    if file.name.lower().endswith(".pdf"):
        return read_pdf(file)
    if file.name.lower().endswith(".docx"):
        return read_docx(file)
    return ""

# ========= CẤU HÌNH =========
st.set_page_config(page_title="AI Audit – Chấm thầu", layout="wide")
st.title("📑 HỆ THỐNG CHẤM THẦU – TỔ CHUYÊN GIA")

tab1, tab2, tab3 = st.tabs([
    "1️⃣ Upload HSMT",
    "2️⃣ Gán tiêu chí",
    "3️⃣ Chấm thầu"
])

# ========= TAB 1 =========
with tab1:
    st.header("📂 Upload HSMT")
    hsmt_files = st.file_uploader(
        "Chọn HSMT (PDF/DOCX)",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )

    hsmt_texts = {}

    if hsmt_files:
        for f in hsmt_files:
            hsmt_texts[f.name] = read_file(f)

        st.success(f"Đã upload {len(hsmt_files)} file")

        name = st.selectbox("Chọn HSMT", list(hsmt_texts.keys()))
        st.text_area("Nội dung", hsmt_texts[name], height=400)

    st.session_state["hsmt_texts"] = hsmt_texts

# ========= TAB 2 =========
with tab2:
    st.header("🏷️ Gán tiêu chí đánh giá")

    if not st.session_state.get("hsmt_texts"):
        st.warning("Cần upload HSMT trước")
    else:
        criteria_text = st.text_area(
            "Mỗi dòng là 1 tiêu chí",
            height=300
        )
        criteria = [c.strip() for c in criteria_text.split("\n") if c.strip()]
        st.session_state["criteria"] = criteria

        if criteria:
            st.success(f"Đã ghi nhận {len(criteria)} tiêu chí")

# ========= TAB 3 =========
with tab3:
    st.header("⚖️ Chấm thầu")

    if not st.session_state.get("criteria"):
        st.warning("Chưa có tiêu chí")
        st.stop()

    hsdt_files = st.file_uploader(
        "Upload HSDT",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )

    if not hsdt_files:
        st.warning("Cần upload HSDT")
        st.stop()

    for f in hsdt_files:
        st.subheader(f"📁 {f.name}")
        text = read_file(f)

        for i, crit in enumerate(st.session_state["criteria"], 1):
            with st.expander(f"Tiêu chí {i}: {crit}", expanded=True):
                st.radio(
                    "Kết quả",
                    ["Đạt", "Không đạt"],
                    key=f"{f.name}_{i}"
                )
                st.text_area(
                    "Căn cứ",
                    height=100,
                    key=f"ev_{f.name}_{i}"
                )

    st.success("✅ Hoàn tất chấm thầu")
