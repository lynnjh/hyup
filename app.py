import streamlit as st
import pandas as pd

# 1. 페이지 제목 및 디자인 테마 설정
st.set_page_config(page_title="GS25 경영주협의회 명단 시스템", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    h1 { color: #0076BE !important; font-weight: bold; font-family: 'Pretendard', sans-serif; }
    .stButton>button { background-color: #0076BE; color: white; border-radius: 8px; font-weight: bold; }
    .stButton>button:hover { background-color: #005A92; }
    .profile-card {
        background-color: #FFFFFF; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); border: 1px solid #E2E8F0;
        border-top: 5px solid #0076BE; margin-top: 10px; margin-bottom: 25px; text-align: center;
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
            st.error("비밀번호가 틀렸습니다.")
    st.stop()

# 3. 구글 스프레드시트 연동
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ZGO6eR1AoBzGwOLGsgBfwgm2_SFx0sA2JY01tICoEWc/edit?usp=sharing"
CSV_URL = SHEET_URL.split('/edit')[0] + '/export?format=csv'

@st.cache_data(ttl=10)
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        # 💡 공백 때문에 못 찾는 에러 방지 (열 이름의 양옆 띄어쓰기 자동 제거)
        df.columns = df.columns.str.strip()
        return df
    except:
        return pd.DataFrame()

df = load_data()

# 4. 메인 화면 구성
st.title("🏪 경영주협의회 명단 시스템")

if df.empty:
    st.error("⚠️ 데이터를 불러오지 못했습니다.")
else:
    # 🛠️ 내가 작성한 시트가 어떻게 들어오는지 확인하는 버튼 (클릭해서 열어보세요!)
    with st.expander("🛠️ (관리자용) 구글 시트가 어플에 어떻게 들어오는지 확인하기"):
        st.write("아래 표의 첫 번째 줄(회색칸) 글씨들과 코드가 매칭되어야 합니다.")
        st.dataframe(df)

    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        if "지역" in df.columns:
            regions = ["전체"] + sorted(df["지역"].dropna().unique().tolist())
            selected_region = st.selectbox("📍 지역 필터", regions)
        else:
            selected_region = "전체"
            
    with col_filter2:
        search_term = st.text_input("🔍 검색어", "")

    filtered_df = df.copy()
    if selected_region != "전체" and "지역" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["지역"] == selected_region]

    # 검색어가 이름, 경영주명, 점포명 어디에든 있으면 찾아줌
    if search_term:
        cond = pd.Series(False, index=filtered_df.index)
        for col in ["이름", "경영주명", "점포명"]:
            if col in filtered_df.columns:
                cond = cond | filtered_df[col].astype(str).str.contains(search_term, na=False)
        filtered_df = filtered_df[cond]

    st.write(f"**총 {len(filtered_df)}명의 경영주님이 확인되었습니다.**")
    st.divider()

    cols = st.columns(3)
    default_img = "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"

    for index, row in filtered_df.reset_index(drop=True).iterrows():
        col_idx = index % 3
        with cols[col_idx]:
            
            # 💡 스마트 매칭: '사진링크' 열이 없으면 '사진' 열을 찾습니다.
            raw_url = row.get("사진링크", row.get("사진", ""))
            img_url = default_img
            if pd.notna(raw_url) and str(raw_url).strip().startswith("http"):
                img_url = str(raw_url).strip()

            # 💡 스마트 매칭: 시트의 다양한 제목에 맞춰 유연하게 데이터를 가져옵니다.
            val_region = row.get('지역', '지역 미정')
            val_title  = row.get('직책', row.get('구분', '경영주'))
            val_name   = row.get('이름', row.get('경영주명', '무명'))
            val_store  = row.get('점포명', '-')
            val_phone  = row.get('연락처', row.get('연락터', '-'))

            with st.container():
                st.image(img_url, width=140)
                card_html = f"""
                <div class="profile-card">
                    <div class="profile-title">{val_region} · {val_title}</div>
                    <div class="profile-name">{val_name} 경영주님</div>
                    <div class="profile-info">
                        🏪 <b>점포명:</b> {val_store}<br>
                        📞 <b>연락처:</b> {val_phone}
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
