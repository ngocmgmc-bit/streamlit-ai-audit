import streamlit as st

st.set_page_config(page_title="Tool chấm thầu", layout="wide")

st.title("📑 HỆ THỐNG CHẤM THẦU – MODULE A1")

st.subheader("1️⃣ Upload Hồ sơ mời thầu (HSMT)")
hsmt_file = st.file_uploader(
    "Chọn file HSMT (PDF hoặc Word)",
    type=["pdf", "docx"],
    accept_multiple_files=False
)

st.subheader("2️⃣ Upload Hồ sơ dự thầu (HSDT)")
hsdt_files = st.file_uploader(
    "Chọn các file HSDT (PDF hoặc Word)",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

st.divider()

if hsmt_file and hsdt_files:
    st.success("✅ Đã nhận đủ HSMT và HSDT")
    st.write(f"📄 HSMT: **{hsmt_file.name}**")
    st.write("📂 Danh sách HSDT:")
    for f in hsdt_files:
        st.write(f"– {f.name}")
else:
    st.warning("⚠️ Vui lòng upload đủ 1 HSMT và ít nhất 1 HSDT")
