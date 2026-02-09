import streamlit as st

st.set_page_config(page_title="Tool chấm thầu", layout="wide")

st.title("📑 HỆ THỐNG CHẤM THẦU – MODULE A1")

st.subheader("1️⃣ Upload Hồ sơ mời thầu (HSMT)")
hsmt_file = st.file_uploader(
    "Chọn file HSMT (PDF hoặc Word)",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

st.subheader("2️⃣ Upload Hồ sơ dự thầu (HSDT)")
hsdt_files = st.file_uploader(
    "Chọn các file HSDT (PDF hoặc Word)",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

st.divider()
st.subheader("📌 Nội dung trích xuất từ HSMT")

if hsmt_files:
    hsmt_texts = []

    for hsmt_file in hsmt_files:
        if hsmt_file.name.lower().endswith(".pdf"):
            text = read_pdf(hsmt_file)
        elif hsmt_file.name.lower().endswith(".docx"):
            text = read_docx(hsmt_file)
        else:
            text = ""

        if text.strip():
            hsmt_texts.append(
                f"===== FILE: {hsmt_file.name} =====\n{text}"
            )

    full_hsmt_text = "\n\n".join(hsmt_texts)

    st.text_area(
        "📄 Nội dung HSMT (đã trích xuất)",
        full_hsmt_text,
        height=400
    )
else:
    st.info("⬆️ Vui lòng upload ít nhất 1 file HSMT")
