import streamlit as st

st.set_page_config(layout="wide", page_title="KeyGuard Gateway")

st.title("KeyGuard Web Management Portal")
st.markdown("""
### 접속할 시스템을 선택하세요
이 포털에서는 두 가지 시스템으로 접근이 가능합니다. 이 페이지의 URL을 기준으로 끝에 페이지 이름을 붙여 직접 접속할 수도 있습니다.

* **[판매 등록 (현장용) ➡️](./01_Sales_Registration)** : 각 지사에서 카드키 판매를 등록하는 시스템입니다.
* **[관리자 대시보드 (본사용) ➡️](./02_Admin_Dashboard)** : 전체 지사의 판매 현황과 재고를 파악하는 최고관리자용 시스템입니다.

좌측 사이드바(Sidebar) 메뉴를 통해서도 원하시는 페이지로 즉각 이동할 수 있습니다.
""")
