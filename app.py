import streamlit as st

st.set_page_config(layout="wide", page_title="KeyGuard Gateway")

st.markdown("""
# 🛡️ KeyGuard Enterprise

환영합니다. **카드키 통합 관리 포털**입니다.
아래 메뉴를 선택하여 이동해 주세요.
---
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🏢 지사별 판매 현황 등록
    각 지점별로 판매된 카드키의 내역을 스캔하고 데이터화합니다.
    
    [👉 판매 등록 페이지로 이동](Sales_Registration)
    """)

with col2:
    st.markdown("""
    ### 👑 최고 관리자 대시보드
    전국 지점의 남은 재고와 전체 판매 실적을 실시간으로 확인합니다.
    
    [👉 대시보드 페이지로 이동](Admin_Dashboard)
    """)

st.markdown("---")
st.info("💡 **Tip:** 좌측 상단의 화살표(`>`) 모양을 클릭하여 열리는 사이드바 메뉴를 통해서도 언제든지 원하시는 페이지로 이동하실 수 있습니다.")
