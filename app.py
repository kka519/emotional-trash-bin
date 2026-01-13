import streamlit as st
from openai import OpenAI
from streamlit_lottie import st_lottie
import requests

# [로티 애니메이션 불러오는 함수]
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# 1. 페이지 설정
st.set_page_config(
    page_title="감정 쓰레기통",
    page_icon="🗑️",
    layout="wide"  # 카드를 넓게 보여주기 위해 wide 모드 사용
)

# [디자인] 따뜻한 카페 분위기 CSS
st.markdown("""
    <style>
    .stApp {background-color: #FFF9F0;}
    h1, h2, h3, p, div, span {color: #4A4A4A !important;}
    
    /* 채팅창 디자인 */
    .stChatMessage {
        background-color: #FFFFFF;
        border-radius: 20px;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.05);
        padding: 15px;
        border: 1px solid #F0E6D2;
    }
    
    /* 버튼 디자인 */
    .stButton > button {
        background-color: #FFD180;
        color: white;
        border-radius: 10px;
        border: none;
        width: 100%; /* 버튼 꽉 차게 */
    }
    .stButton > button:hover {
        background-color: #FFB74D;
    }
    
    /* 카드 디자인 (인트로) */
    .persona-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 20px;
        border: 1px solid #E0E0E0;
    }
    </style>
    """, unsafe_allow_html=True)

# [비밀 키 로드]
try:
    api_key = st.secrets["OPENAI_API_KEY"]
except:
    st.error("🚨 API 키를 찾을 수 없습니다.")
    st.stop()

# --- 상태 관리 (페이지 이동 로직) ---
if "page" not in st.session_state:
    st.session_state.page = "intro" # 기본값: 인트로 페이지
if "selected_persona" not in st.session_state:
    st.session_state.selected_persona = None

# --- 함수: 인트로 페이지 보여주기 ---
def show_intro():
    # 힐링 로티 애니메이션
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        lottie_url = "https://lottie.host/5aee9530-555e-400b-93f8-661b0de2931a/j8J4Wv84lO.json"
        lottie_json = load_lottieurl(lottie_url)
        if lottie_json:
            st_lottie(lottie_json, height=200, key="welcome")
    
    st.markdown("<h1 style='text-align: center;'>🗑️ 감정 쓰레기통</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>오늘 당신의 마음을 받아줄 친구를 선택하세요.</p>", unsafe_allow_html=True)
    st.write("") # 여백
    
    # 상담사 선택 카드 (4개 배치)
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.header("🍺 사이다 형")
            st.write("🔥 특징: 같이 욕해주고 화내주는 찐친")
            st.write("💬 '무슨 일이야! 내가 다 들어줄게!'")
            if st.button("대화하기", key="btn_cider"):
                st.session_state.selected_persona = "사이다 형 (버럭형)"
                st.session_state.page = "chat"
                st.rerun()

        with st.container(border=True):
            st.header("🎓 차분한 박사")
            st.write("📊 특징: 팩트로 조져주는 냉철한 분석")
            st.write("💬 '상황을 객관적으로 분석해 봅시다.'")
            if st.button("대화하기", key="btn_doctor"):
                st.session_state.selected_persona = "차분한 박사 (분석형)"
                st.session_state.page = "chat"
                st.rerun()
                
    with col2:
        with st.container(border=True):
            st.header("🍀 토닥이")
            st.write("💖 특징: 무조건 내 편, 따뜻한 위로")
            st.write("💬 '많이 힘드셨죠.. 이리 와요.'")
            if st.button("대화하기", key="btn_todak"):
                st.session_state.selected_persona = "토닥이 (공감형)"
                st.session_state.page = "chat"
                st.rerun()
        
        with st.container(border=True):
            st.header("👵 욕쟁이 할매")
            st.write("🍱 특징: 구수한 욕으로 정 주는 할매")
            st.write("💬 '아이고 내 새끼! 누가 괴롭히드나!'")
            if st.button("대화하기", key="btn_grandma"):
                st.session_state.selected_persona = "욕쟁이 할매 (유머형)"
                st.session_state.page = "chat"
                st.rerun()

# --- 함수: 채팅 페이지 보여주기 ---
def show_chat():
    # 상단: 뒤로가기 버튼 & 현재 상담사 표시
    c1, c2 = st.columns([1, 5])
    with c1:
        if st.button("⬅️ 뒤로가기"):
            st.session_state.page = "intro"
            st.session_state.messages = [] # 대화 기록 초기화 (선택사항)
            st.rerun()
            
    persona = st.session_state.selected_persona
    
    # 상담사별 설정 (시스템 프롬프트 등)
    if "사이다" in persona:
        avatar_img = "🍺"
        welcome_msg = "왔냐? 오늘 무슨 개같은 일이 있었는데? 썰 좀 풀어봐. 내가 다 들어줄게!"
        system_prompt = "너는 다혈질인 '사이다 형'이다. 반말을 쓰고 화를 내며 위로해라."
    elif "토닥이" in persona:
        avatar_img = "🍀"
        welcome_msg = "어서 오세요.. 따뜻한 차 한잔하면서 이야기해요. 다 들어줄게요."
        system_prompt = "너는 따뜻한 '토닥이'다. 존댓말을 쓰고 깊이 공감해라."
    elif "박사" in persona:
        avatar_img = "🎓"
        welcome_msg = "반갑습니다. 상황을 객관적으로 말씀해 주세요. 분석해 드리겠습니다."
        system_prompt = "너는 냉철한 '심리 박사'다. 논리적으로 분석해라."
    else:
        avatar_img = "👵"
        welcome_msg = "아이고 내 새끼 왔나! 얼굴이 와 이리 반쪽이 됐노. 할미한테 다 일러라."
        system_prompt = "너는 구수한 사투리를 쓰는 '욕쟁이 할머니'다."

    # 메인 채팅 화면
    with c2:
        st.subheader(f"{avatar_img} {persona.split('(')[0]}와의 대화")

    # 세션 메시지 초기화
    if "messages" not in st.session_state or not st.session_state.messages:
        st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]

    # 대화 기록 출력
    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            st.chat_message(msg["role"], avatar=avatar_img).write(msg["content"])
        else:
            st.chat_message(msg["role"], avatar="😢").write(msg["content"])

    # 입력창
    if prompt := st.chat_input("하고 싶은 말을 입력하세요..."):
        client = OpenAI(api_key=api_key)
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user", avatar="😢").write(prompt)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages
        )
        msg = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant", avatar=avatar_img).write(msg)

# --- 메인 실행 로직 ---
if st.session_state.page == "intro":
    show_intro()
else:
    show_chat()
