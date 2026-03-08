from data_manager import (
    get_dashboard_data, reset_data, save_inventory, save_issuance, 
    get_all_workers, ensure_initial_data, generate_excel_export,
    get_all_admins, save_admin, reset_admin_password
)

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
    st.query_params.clear()

elif action == "inventory_save":
    inv_data = {
        'branch': params.get('branch', ''),
        'type': params.get('type', '') or f"{params.get('type1', '')}({params.get('type2', '')})",
        'qty': params.get('qty', '0'),
        'memo': params.get('memo', ''),
        'worker': params.get('worker', '')
    }
    action_result = save_inventory(inv_data)
    st.query_params.clear()

elif action == "issuance_save":
    iss_data = {
        'branch': params.get('branch', ''),
        'worker': params.get('worker', ''),
        'type1': params.get('type1', ''),
        'type2': params.get('type2', ''),
        'qty': params.get('qty', '0'),
        'memo': params.get('memo', '')
    }
    action_result = save_issuance(iss_data)
    st.query_params.clear()

elif action == "download_excel":
    excel_data = generate_excel_export()
    st.download_button(
        label="📥 엑셀 파일 다운로드 (클릭)",
        data=excel_data,
        file_name=f"카드키_데이터_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="excel_download_btn"
    )
    st.info("위 버튼을 눌러 엑셀 파일을 다운로드하세요.")
    action_result = "✅ 엑셀 내보내기가 준비되었습니다."
    # st.query_params.clear() # 다운로드 버튼 유지를 위해 클리어 유예

elif action == "sa_action":
    sa_sub_action = params.get("sub", "")
    if sa_sub_action == "register" or sa_sub_action == "edit":
        admin_data = {
            'userId': params.get('userId', ''),
            'name': params.get('name', ''),
            'password': params.get('password', ''),
            'role': params.get('role_type', 'Admin'),
            'branch': params.get('branch_name', 'HQ')
        }
        action_result = save_admin(admin_data)
    elif sa_sub_action == "reset_pwd":
        action_result = reset_admin_password(params.get('userId', ''), params.get('password', ''))
    st.query_params.clear()

# ─── 사원/관리자 데이터 준비 ─────────────────────────────────────
all_workers = get_all_workers()
workers_map = {}
for w in all_workers:
    b = w.get('branch', '')
    if b not in workers_map:
        workers_map[b] = []
    workers_map[b].append(w.get('name', ''))

all_admins = get_all_admins()

# ─── 대시보드 데이터 로드 ─────────────────────────────────────────
role = params.get("role", "Admin")
branch_filter = params.get("branch", "")
year = params.get("year", "2026")
month = params.get("month", "ALL")
day = params.get("day", "ALL")

dashboard_data = get_dashboard_data(role, branch_filter, year, month, day)

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
window.__WORKERS_MAP__ = {json.dumps(workers_map, ensure_ascii=False)};
window.__ADMINS_LIST__ = {json.dumps(all_admins, ensure_ascii=False)};
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
