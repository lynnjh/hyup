import streamlit as st
import pandas as pd

# 1. 페이지 제목 및 디자인 설정
st.set_page_config(page_title="GS25 경영주협의회 명단 확인", layout="wide")

# GS25 느낌의 파란색 디자인 적용
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    h1 { color: #0076BE; }
    .stButton>button { background-color: #0076BE; color: white; }
    </style>
    """, unsafe_allow_html=True)

# 2. 비밀번호 체크 (5525)
if "access" not in st.session_state:
    st.session_state.access = False

if not st.session_state.access:
    st.title("🔒 보안 접속")
    pw = st.text_input("비밀번호를 입력하세요", type="password")
    if st.button("입장하기"):
        if pw == "5525":
            st.session_state.access = True
            st.rerun()
        else:
            st.error("비밀번호가 틀렸습니다.")
    st.stop() # 비밀번호 틀리면 여기서 멈춤

# 3. 구글 시트 데이터 불러오기 (여기에 알려주신 주소를 쏙 넣었어요!)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ZGO6eR1AoBzGwOLGsgBfwgm2_SFx0sA2JY01tICoEWc/edit?usp=sharing"
CSV_URL = SHEET_URL.split('/edit')[0] + '/export?format=csv'

@st.cache_data
def load_data():
    try:
        return pd.read_csv(CSV_URL)
    except:
        return pd.DataFrame(columns=["지역", "이름", "점포명", "직책", "연락처"])

df = load_data()

# 4. 메인 화면 구성
st.title("🏪 경영주협의회 명단 확인 시스템")
st.write("지역별로 경영주님들의 명단을 편리하게 확인하고 검색하세요.")

# --- 편리한 기능 1: 검색창 ---
search_term = st.text_input("🔍 이름 또는 점포명으로 검색", "")

# --- 편리한 기능 2: 지역별 필터 (사이드바) ---
st.sidebar.header("📍 지역 필터")
# 데이터가 없을 경우를 대비한 안전 장치
if not df.empty and "지역" in df.columns:
    all_regions = ["전체"] + sorted(df["지역"].dropna().unique().tolist())
else:
    all_regions = ["전체"]
selected_region = st.sidebar.selectbox("보고 싶은 지역을 선택하세요", all_regions)

# 데이터 필터링 로직
filtered_df = df.copy()
if not filtered_df.empty:
    if selected_region != "전체" and "지역" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["지역"] == selected_region]

    if search_term and "이름" in filtered_df.columns and "점포명" in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df["이름"].astype(str).str.contains(search_term, na=False) | 
            filtered_df["점포명"].astype(str).str.contains(search_term, na=False)
        ]

# --- 편리한 기능 3: 보기 좋게 표로 출력 ---
st.write(f"**총 {len(filtered_df)}명의 명단이 검색되었습니다.**")
st.dataframe(filtered_df, use_container_width=True, hide_index=True)

# --- 편리한 기능 4: 엑셀로 저장하기 버튼 ---
if not filtered_df.empty:
    csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 현재 명단 다운로드 (엑셀용 CSV)",
        data=csv,
        file_name='council_list.csv',
        mime='text/csv',
    )
