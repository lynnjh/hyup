import streamlit as st
import pandas as pd

# 1. 페이지 제목 및 디자인 설정
st.set_page_config(page_title="GS25 경영주협의회 명단 확인", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    h1 { color: #0076BE; }
    .stButton>button { background-color: #0076BE; color: white; border-radius: 8px; font-weight: bold;}
    </style>
    """, unsafe_allow_html=True)

# 2. 비밀번호 체크 (5525)
if "access" not in st.session_state:
    st.session_state.access = False

if not st.session_state.access:
    st.title("🔒 보안 접속")
    st.write("경영주협의회 명단을 확인하시려면 비밀번호를 입력해주세요.")
    pw = st.text_input("비밀번호", type="password")
    if st.button("입장하기"):
        if pw == "5525":
            st.session_state.access = True
            st.rerun()
        else:
            st.error("비밀번호가 틀렸습니다.")
    st.stop()

# 3. 구글 시트 가져오기 (10초마다 새 기억으로 업데이트!)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ZGO6eR1AoBzGwOLGsgBfwgm2_SFx0sA2JY01tICoEWc/edit?usp=sharing"
CSV_URL = SHEET_URL.split('/edit')[0] + '/export?format=csv'

@st.cache_data(ttl=10) # 핵심: 10초 지나면 옛날 기억 지우고 무조건 새로 고침
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        return df
    except:
        return pd.DataFrame()

df = load_data()

# 4. 메인 화면
st.title("🏪 경영주협의회 명단 확인 시스템")

# 만약 데이터가 비어있다면 안내문 띄우기
if df.empty:
    st.error("⚠️ 데이터를 불러오는 중이거나 구글 시트가 비어있습니다. 잠시 후 새로고침(F5)을 눌러주세요.")
else:
    st.write("지역별로 경영주님들의 명단을 편리하게 확인하고 검색하세요.")

    # --- 기능 1: 검색창 ---
    search_term = st.text_input("🔍 이름 또는 점포명으로 검색", "")

    # --- 기능 2: 지역 필터 ---
    st.sidebar.header("📍 지역 필터")
    
    # 시트에 '지역'이라는 글씨가 있는지 확인 후 필터 만들기
    if "지역" in df.columns:
        # 비어있는 칸 제외하고 지역 목록 만들기
        all_regions = ["전체"] + sorted(df["지역"].dropna().unique().tolist())
        selected_region = st.sidebar.selectbox("보고 싶은 지역을 선택하세요", all_regions)

        filtered_df = df.copy()
        
        if selected_region != "전체":
            filtered_df = filtered_df[filtered_df["지역"] == selected_region]

        # 검색어 필터링 (이름이나 점포명에 글자가 포함되어 있으면 찾아줌)
        if search_term and "이름" in filtered_df.columns and "점포명" in filtered_df.columns:
            filtered_df = filtered_df[
                filtered_df["이름"].astype(str).str.contains(search_term, na=False) | 
                filtered_df["점포명"].astype(str).str.contains(search_term, na=False)
            ]

        # --- 기능 3: 예쁘게 표로 보여주기 ---
        st.write(f"**총 {len(filtered_df)}명의 명단이 검색되었습니다.**")
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)

        # --- 기능 4: 엑셀 다운로드 ---
        csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 현재 화면 명단 다운로드 (엑셀용)",
            data=csv,
            file_name='council_list.csv',
            mime='text/csv',
        )
    else:
        st.warning("구글 시트의 A1 칸에 '지역'이라고 정확히 적혀있는지 확인해주세요!")
        st.dataframe(df) # 만약 에러가 나면 시트 내용을 그대로 보여줌
