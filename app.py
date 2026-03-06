import streamlit as st
import os

st.set_page_config(layout="wide", page_title="KeyGuard Management")

# Function to read HTML files
def load_html(file_name):
    with open(file_name, 'r', encoding='utf-8') as f:
        return f.read()

st.title("KeyGuard Web Viewer")
st.write("This app currently hosts the static HTML files for the KeyGuard project.")

page = st.selectbox("Select Page to View:", ["Index (Sales Registration)", "Admin Dashboard"])

if page == "Index (Sales Registration)":
    html_content = load_html("Index.html")
    st.components.v1.html(html_content, height=1000, scrolling=True)
else:
    html_content = load_html("Admin.html")
    st.components.v1.html(html_content, height=1200, scrolling=True)
