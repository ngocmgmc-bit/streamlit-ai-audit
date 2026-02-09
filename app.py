import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
import textwrap

# =========================
# CẤU HÌNH TRANG
# =========================
st.set_page_config(
    page_title="Hệ thống chấm thầu – Tổ chuyên gia",
    layout="wide"
)

st.title("📑 HỆ THỐNG CHẤM THẦU – TỔ CHUYÊN GIA")

# =========================
# HÀM ĐỌC FILE
# =========================
def read_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def read_docx(file):
    doc = Document(file)
    return "\n".join(p.text for p in doc.paragraphs)

def read_file(file):
    if file.name.lower().endswith(".pdf"):
        return read_pdf(file)
    elif file.name.lower().endswith(".docx"):
        return read_docx(file)
    return ""

# =========================
# SESSION STATE
# =========================
if "hsmt_texts" not in st.session_state:
    st.session_state.hsmt_texts = {}

if "criteria" not in st.session_state:
    st.session_state.criteria = []

# =========================
# TAB
# =========================
tab1, tab2, tab3 = st.tabs([
    "1️⃣ Upload HSMT",
    "2️⃣ Gán tiêu chí",
    "3️⃣ Chấm thầu"
])

# ==========================================================
# TAB 1 – UPLOAD HSMT
# ==========================================================
with tab1:
    st.subheader("📤 Upload Hồ sơ mời thầu (HSMT)")

    hsmt_files = st.file_uploader(
        "Upload HSMT (PDF / DOCX – có thể nhiều file)",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )

    if hsmt_files:
        st.session_state.hsmt_texts = {}

        for f in hsmt_files:
            text = read_file(f)
            st.session_state.hsmt_texts[f.name] = text

        st.success(f"✅ Đã tải {len(hsmt_files)} file HSMT")

        with st.expander("📄 Xem nội dung trích xuất"):
            for name, txt in st.session_state.hsmt_texts.items():
                st.markdown(f"**{name}**")
                st.text_area(
                    label=name,
                    value=txt[:5000],
                    height=200
                )

# ==========================================================
# TAB 2 – GÁN TIÊU CHÍ
# ==========================================================
with tab2:
    st.subheader("🏷️ Gán tiêu chí đánh giá theo HSMT")

    if not st.session_state.hsmt_texts:
        st.warning("⚠️ Cần upload HSMT trước")
    else:
        st.info("👉 Mỗi tiêu chí tương ứng **MỘT nội dung chấm thầu** trong HSMT")

        with st.form("criteria_form"):
            ten = st.text_input("Tên tiêu chí")
            mo_ta = st.text_area("Mô tả / yêu cầu theo HSMT")
            can_cu = st.text_area("Căn cứ HSMT (trích đoạn điều/chương/mục)")

            submitted = st.form_submit_button("➕ Thêm tiêu chí")

            if submitted and ten:
                st.session_state.criteria.append({
                    "ten": ten,
                    "mo_ta": mo_ta,
                    "can_cu": can_cu
                })
                st.success("✅ Đã thêm tiêu chí")

        if st.session_state.criteria:
            st.markdown("### 📋 Danh sách tiêu chí")
            for i, c in enumerate(st.session_state.criteria, 1):
                st.markdown(f"""
**{i}. {c['ten']}**  
- Mô tả: {c['mo_ta']}  
- Căn cứ: {c['can_cu']}
""")

# ==========================================================
# TAB 3 – CHẤM THẦU
# ==========================================================
with tab3:
    st.subheader("⚖️ Chấm thầu – Có căn cứ & AI hỗ trợ")

    if not st.session_state.criteria:
        st.warning("⚠️ Chưa có tiêu chí")
    else:
        hsdt_files = st.file_uploader(
            "Upload HSDT (PDF / DOCX)",
            type=["pdf", "docx"],
            accept_multiple_files=True,
            key="hsdt"
        )

        if hsdt_files:
            hsdt_text = ""
            for f in hsdt_files:
                hsdt_text += read_file(f)

            st.markdown("---")
            st.markdown("## 📊 KẾT QUẢ CHẤM THẦU")

            for i, c in enumerate(st.session_state.criteria, 1):
                st.markdown(f"### {i}. {c['ten']}")

                # ====== LOGIC CHẤM CƠ BẢN (RULE-BASED) ======
                dat = c["mo_ta"].lower() in hsdt_text.lower()

                ket_qua = "ĐẠT" if dat else "KHÔNG ĐẠT"

                st.markdown(f"""
- **Kết quả:** **{ket_qua}**
- **Căn cứ HSMT:** {c['can_cu']}
- **Nhận xét tổ chuyên gia:**  
{ "HSDT có nội dung đáp ứng yêu cầu." if dat else "HSDT không thể hiện nội dung theo yêu cầu HSMT." }
""")

            st.success("✅ Hoàn thành chấm thầu theo tiêu chí HSMT")

# =========================
# FOOTER
# =========================
st.markdown("---")
st.caption("AI hỗ trợ phân tích – Quyết định cuối cùng thuộc Tổ chuyên gia")
