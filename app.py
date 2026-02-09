import streamlit as st
import pdfplumber
from docx import Document

# =====================
# HÀM ĐỌC FILE
# =====================
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

# =====================
# CẤU HÌNH TRANG
# =====================
st.set_page_config(page_title="AI Audit – Chấm thầu", layout="wide")
st.title("📑 HỆ THỐNG CHẤM THẦU – TỔ CHUYÊN GIA (AI HỖ TRỢ)")

tab1, tab2, tab3 = st.tabs([
    "1️⃣ Upload HSMT",
    "2️⃣ Gán tiêu chí (Chương III)",
    "3️⃣ Chấm thầu"
])

# =====================
# TAB 1 – UPLOAD HSMT
# =====================
with tab1:
    st.header("📂 Upload Hồ sơ mời thầu (HSMT)")
    hsmt_files = st.file_uploader(
        "Chọn file HSMT (PDF / DOCX)",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )

    hsmt_texts = {}

    if hsmt_files:
        for f in hsmt_files:
            hsmt_texts[f.name] = read_file(f)

        st.success(f"Đã upload {len(hsmt_files)} file HSMT")

        selected = st.selectbox(
            "Chọn HSMT để xem nội dung",
            list(hsmt_texts.keys())
        )

        st.text_area(
            "Nội dung HSMT",
            hsmt_texts[selected],
            height=400
        )

    st.session_state["hsmt_texts"] = hsmt_texts

# =====================
# TAB 2 – GÁN TIÊU CHÍ
# =====================
with tab2:
    st.header("🏷️ Gán tiêu chí đánh giá (Chương III – HSMT)")

    if not st.session_state.get("hsmt_texts"):
        st.warning("⚠️ Cần upload HSMT trước")
    else:
        criteria_text = st.text_area(
            "Nhập tiêu chí (mỗi dòng là 1 tiêu chí)",
            height=300,
            placeholder="""
Ví dụ:
- Năng lực, kinh nghiệm
- Nhân sự chủ chốt
- Giải pháp kỹ thuật
- Thiết bị
"""
        )

        criteria = [c.strip() for c in criteria_text.split("\n") if c.strip()]
        st.session_state["criteria"] = criteria

        if criteria:
            st.success(f"Đã ghi nhận {len(criteria)} tiêu chí")

# =====================
# TAB 3 – CHẤM THẦU
# =====================
with tab3:
    st.header("⚖️ CHẤM THẦU – THEO TỔ CHUYÊN GIA")

    if not st.session_state.get("criteria"):
        st.warning("⚠️ Chưa có tiêu chí đánh giá")
        st.stop()

    hsdt_files = st.file_uploader(
        "📂 Upload Hồ sơ dự thầu (HSDT)",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )

    if not hsdt_files:
        st.warning("⚠️ Cần upload HSDT")
        st.stop()

    hsdt_texts = {}
    for f in hsdt_files:
        hsdt_texts[f.name] = read_file(f)

    for hsdt_name, hsdt_text in hsdt_texts.items():
        st.subheader(f"📁 HSDT: {hsdt_name}")

        for idx, criterion in enumerate(st.session_state["criteria"], start=1):
            with st.expander(f"Tiêu chí {idx}: {criterion}", expanded=True):
                result = st.radio(
                    "Kết quả",
                    ["Đạt", "Không đạt"],
                    key=f"{hsdt_name}_{idx}"
                )

                evidence = st.text_area(
                    "Căn cứ (trích từ HSDT)",
                    height=120,
                    key=f"ev_{hsdt_name}_{idx}"
                )

    st.success("✅ Hoàn tất chấm thầu")
                    st.markdown("**🧠 Kết quả AI:**")
                    st.markdown(textwrap.indent(ai_result, "> "))
