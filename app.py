import streamlit as st
import pandas as pd

# 1. 페이지 제목 및 GS25 BI 디자인 테마 설정
st.set_page_config(page_title="GS25 경영주협의회 명단 시스템", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    h1 { color: #0076BE !important; font-weight: bold; font-family: 'Pretendard', sans-serif; }
    .stButton>button { background-color: #0076BE; color: white; border-radius: 8px; font-weight: bold; }
    .stButton>button:hover { background-color: #005A92; }
    
    /* 명함 카드 테두리 및 디자인 */
    .profile-card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #E2E8F0;
        border-top: 5px solid #0076BE;
        margin-top: 10px;
        margin-bottom: 25px;
        text-align: center;
    }
    .profile-title { font-size: 14px; color: #0076BE; font-weight: bold; margin-bottom: 4px; }
    .profile-name { font-size: 20px; font-weight: bold; color: #1E293B; margin-bottom: 12px; }
    .profile-info { font-size: 14px; color: #475569; text-align: left; line-height: 1.6; background: #F1F5F9; padding: 10px; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 비밀번호 보안 접속 (5525)
if "access" not in st.session_state:
    st.session_state.access = False

if not st.session_state.access:
    st.title("🔒 경영주협의회 보안 접속")
    st.write("명단을 확인하시려면 비밀번호를 입력해주세요.")
    pw = st.text_input("비밀번호 4자리", type="password")
    if st.button("입장하기", use_container_width=True):
        if pw == "5525":
            st.session_state.access = True
            st.rerun()
        else:
            st.error("비밀번호가 틀렸습니다. 다시 입력해주세요.")
    st.stop()

# 3. 구글 스프레드시트 연동 (알려주신 주소 자동 반영)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ZGO6eR1AoBzGwOLGsgBfwgm2_SFx0sA2JY01tICoEWc/edit?usp=sharing"
CSV_URL = SHEET_URL.split('/edit')[0] + '/export?format=csv'

@st.cache_data(ttl=10) # 10초마다 구글 시트의 최신 내용을 확인합니다.
def load_data():
    try:
        return pd.read_csv(CSV_URL)
    except:
        return pd.DataFrame()

df = load_data()

# 4. 메인 화면 구성
st.title("🏪 경영주협의회 명단 시스템")

if df.empty:
    st.error("⚠️ 구글 시트 데이터를 읽어오지 못했습니다. 시트의 공유 설정이나 컬럼명을 확인해주세요.")
else:
    # 필터 기능 (검색창과 지역선택)
    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        if "지역" in df.columns:
            regions = ["전체"] + sorted(df["지역"].dropna().unique().tolist())
            selected_region = st.selectbox("📍 지역 필터", regions)
        else:
            selected_region = "전체"
            
    with col_filter2:
        search_term = st.text_input("🔍 이름 또는 점포명 검색", "")

    # 검색 및 필터링 적용
    filtered_df = df.copy()
    if selected_region != "전체" and "지역" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["지역"] == selected_region]
        
    if search_term:
        cond_name = filtered_df["이름"].astype(str).str.contains(search_term, na=False) if "이름" in filtered_df.columns else False
        cond_store = filtered_df["점포명"].astype(str).str.contains(search_term, na=False) if "점포명" in filtered_df.columns else False
        filtered_df = filtered_df[cond_name | cond_store]

    st.write(f"**총 {len(filtered_df)}명의 경영주님이 확인되었습니다.**")
    st.divider()

    # 5. 명함 형태로 사진과 정보 출력 (한 줄에 3명씩 나란히 배치)
    cols = st.columns(3)
    
    # 혹시나 사진 주소가 비어있거나 오류가 있을 때 대신 띄울 기본 사람 모양 아이콘
    default_img = "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"

    for index, row in filtered_df.reset_index(drop=True).iterrows():
        col_idx = index % 3
        with cols[col_idx]:
            
            # 💡 핵심: 구글 시트의 '사진링크' 열에서 주소를 가져옵니다.
            img_url = default_img
            if "사진링크" in row and pd.notna(row["사진링크"]):
                url_str = str(row["사진링크"]).strip()
                if url_str.startswith("http"):
                    img_url = url_str

            # 명함 상자 만들기
            with st.container():
                # 1. 실제 얼굴 사진 띄우기
                st.image(img_url, width=140)
                
                # 2. 사진 밑에 인적 사항 적기
                card_html = f"""
                <div class="profile-card">
                    <div class="profile-title">{row.get('지역', '지역 미정')} · {row.get('직책', '경영주')}</div>
                    <div class="profile-name">{row.get('이름', '무명')} 경영주님</div>
                    <div class="profile-info">
                        🏪 <b>점포명:</b> {row.get('점포명', '-')}<br>
                        📞 <b>연락처:</b> {row.get('연락처', '-')}
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
