import streamlit as st

st.set_page_config(layout="wide", page_title="관리자 대시보드", initial_sidebar_state="collapsed")

# Function to read HTML files
def load_html(file_name):
    with open(file_name, 'r', encoding='utf-8') as f:
        return f.read()

# Load and render Admin.html
html_content = load_html("Admin.html")

# Inject a little style to hide Streamlit's default padding to make the HTML look native
st.markdown("""
<div style="display:none;">
    <style>
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            padding-left: 0rem !important;
            padding-right: 0rem !important;
            max-width: 100% !important;
        }
        header {visibility: hidden;}
    </style>
</div>
""", unsafe_allow_html=True)

st.components.v1.html(html_content, height=1500, scrolling=True)
