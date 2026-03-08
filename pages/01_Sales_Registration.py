import streamlit as st
import json
import urllib.parse
from datetime import datetime
from data_manager import save_sale, save_inventory, get_workers_by_branch, get_all_workers, ensure_initial_data

st.set_page_config(layout="wide", page_title="카드키 판매 등록", initial_sidebar_state="collapsed")

# 초기 데이터 세팅
ensure_initial_data()

# ─── 쿼리 파라미터로 액션 처리 ───────────────────────────────────
params = st.query_params

action = params.get("action", "")
action_result = None

if action == "save":
    try:
        sale_data = {
            'date': params.get('date', datetime.now().strftime('%Y-%m-%d')),
            'branch': params.get('branch', ''),
            'worker': params.get('worker', ''),
            'serviceNo': params.get('serviceNo', ''),
            'keyType': params.get('keyType', ''),
            'keySubType': params.get('keySubType', ''),
            'qty': params.get('qty', '0'),
            'unitPrice': params.get('unitPrice', '0'),
            'totalPrice': params.get('totalPrice', '0'),
            'saleType': params.get('saleType', 'paid'),
            'memo': params.get('memo', '')
        }
        action_result = save_sale(sale_data)
    except Exception as e:
        action_result = f"❌ 저장 중 오류: {str(e)}"
    st.query_params.clear()

if action == "inventory_save":
    try:
        inv_data = {
            'branch': params.get('branch', ''),
            'type': params.get('type', ''),
            'qty': params.get('qty', '0'),
            'memo': params.get('memo', ''),
            'worker': params.get('worker', '')
        }
        action_result = save_inventory(inv_data)
    except Exception as e:
        action_result = f"❌ 재고 등록 중 오류: {str(e)}"
    st.query_params.clear()

# ─── 사원 데이터 준비 ─────────────────────────────────────────────
all_workers = get_all_workers()

# 지사별 사원 맵 생성
workers_map = {}
for w in all_workers:
    branch = w.get('branch', '')
    if branch not in workers_map:
        workers_map[branch] = []
    workers_map[branch].append(w.get('name', ''))

# ─── HTML 로드 및 데이터 주입 ─────────────────────────────────────
def load_html(file_name):
    with open(file_name, 'r', encoding='utf-8') as f:
        return f.read()

html_content = load_html("Index.html")

# JavaScript를 주입하여 사원 데이터 및 액션 결과 전달
inject_script = f"""
<script>
// Python 백엔드에서 주입된 사원 데이터
window.__WORKERS_MAP__ = {json.dumps(workers_map, ensure_ascii=False)};
window.__ACTION_RESULT__ = {json.dumps(action_result, ensure_ascii=False) if action_result else 'null'};
window.__USE_PYTHON_BACKEND__ = true;
</script>
"""

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
    if action_result.startswith("✅"):
        st.success(action_result)
    else:
        st.error(action_result)

st.components.v1.html(html_content, height=1200, scrolling=True)
