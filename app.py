import streamlit as st

st.set_page_config(
    page_title="AI AUDIT",
    page_icon="📑",
    layout="centered"
)

st.title("📑 AI AUDIT – Phân tích hồ sơ")
st.write("Upload hồ sơ (PDF / Word) để bắt đầu đánh giá")

uploaded_file = st.file_uploader(
    "Chọn file hồ sơ",
    type=["pdf", "docx"]
)

if uploaded_file is not None:
    st.success("✅ Đã upload file thành công")
    st.write("📄 Tên file:", uploaded_file.name)
    st.write("📦 Dung lượng:", uploaded_file.size, "bytes")
