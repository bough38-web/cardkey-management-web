import streamlit as st
import json
import urllib.parse
from data_manager import get_dashboard_data, reset_data, ensure_initial_data

st.set_page_config(layout="wide", page_title="관리자 대시보드", initial_sidebar_state="collapsed")

# 초기 데이터 세팅
ensure_initial_data()

# ─── 쿼리 파라미터로 액션 처리 ───────────────────────────────────
params = st.query_params

action = params.get("action", "")
action_result = None

if action == "reset":
    branch = params.get("branch", "ALL")
    data_type = params.get("dataType", "ALL")
    action_result = reset_data(branch, data_type)
    # 액션 처리 후 파라미터 정리
    st.query_params.clear()

# ─── 대시보드 데이터 로드 ─────────────────────────────────────────
role = params.get("role", "Admin")
branch_filter = params.get("branch", "")

dashboard_data = get_dashboard_data(role, branch_filter)

# ─── HTML 로드 및 데이터 주입 ─────────────────────────────────────
def load_html(file_name):
    with open(file_name, 'r', encoding='utf-8') as f:
        return f.read()

html_content = load_html("Admin.html")

# JavaScript를 주입하여 실제 데이터를 사용하도록 함
inject_script = f"""
<script>
// Python 백엔드에서 주입된 실제 데이터
window.__INJECTED_DATA__ = {json.dumps(dashboard_data, ensure_ascii=False)};
window.__ACTION_RESULT__ = {json.dumps(action_result, ensure_ascii=False) if action_result else 'null'};
window.__USE_PYTHON_BACKEND__ = true;
</script>
"""

# </head> 태그 앞에 스크립트 주입
html_content = html_content.replace('</head>', inject_script + '</head>')

# Streamlit 스타일 숨김
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

# 액션 결과 표시
if action_result:
    st.success(action_result)

st.components.v1.html(html_content, height=1500, scrolling=True)
