import streamlit as st

st.set_page_config(layout="centered", page_title="KeyGuard Gateway", initial_sidebar_state="collapsed")

# Custom CSS for premium landing page
st.markdown("""
<style>
    /* Global Style adjustments */
    body, .stApp {
        background-color: #f8fafc;
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, 'Helvetica Neue', 'Segoe UI', 'Apple SD Gothic Neo', 'Noto Sans KR', 'Malgun Gothic', 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', sans-serif;
    }
    
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.5rem;
        text-align: center;
        letter-spacing: -0.02em;
    }
    
    .sub-title {
        font-size: 1.125rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 3rem;
        font-weight: 500;
    }
    
    /* Card Styles */
    .nav-card {
        background: white;
        border-radius: 1.5rem;
        padding: 2rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .nav-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
        border-color: #cbd5e1;
    }
    
    .card-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: inline-block;
        padding: 1rem;
        border-radius: 1rem;
        background: #f1f5f9;
    }
    
    .card-icon.admin {
        background: #e0e7ff;
        color: #4338ca;
    }
    
    .card-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.75rem;
    }
    
    .card-desc {
        color: #64748b;
        line-height: 1.6;
        flex-grow: 1;
        margin-bottom: 1.5rem;
        font-size: 1rem;
    }

    /* Important: Hide default Streamlit elements that distract */
    .stDeployButton {display:none;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    hr {
        margin: 3rem 0;
        border-color: #e2e8f0;
    }
</style>

<div class="main-title">🛡️ KeyGuard Enterprise</div>
<div class="sub-title">통합 카드키 관리 포털에 오신 것을 환영합니다.<br>원하시는 시스템을 선택하여 접속해주세요.</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
    <div class="nav-card">
        <div>
            <div class="card-icon">🏢</div>
            <div class="card-title">현장 판매 등록</div>
            <div class="card-desc">
                각 지사 현장에서 카드키 <b>판매 내역을 등록</b>하고 즉각적으로 재고를 차감하는 시스템입니다. 현장 담당자를 위한 직관적인 인터페이스를 제공합니다.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/01_Sales_Registration.py", label="판매 등록 페이지 접속", icon="👉", use_container_width=True)

with col2:
    st.markdown("""
    <div class="nav-card">
        <div>
            <div class="card-icon admin">👑</div>
            <div class="card-title">관리자 대시보드</div>
            <div class="card-desc">
                전국 지점의 전체 <b>판매 실적, 재고 현황, 모니터링 인사이트</b>를 실시간으로 파악하는 본사 및 최고 관리자 전용 시스템입니다.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/02_Admin_Dashboard.py", label="관리자 대시보드 접속", icon="👉", use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)
st.info("💡 **안내:** 접근 권한이 없는 메뉴에 접속 시 제한될 수 있습니다. 사이드바 메뉴를 통해서도 이동 가능합니다.")
