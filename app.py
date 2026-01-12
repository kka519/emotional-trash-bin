import streamlit as st
from openai import OpenAI
from streamlit_lottie import st_lottie
import requests

# [로티 애니메이션 불러오는 함수]
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# 1. 페이지 설정
st.set_page_config(
    page_title="감정 쓰레기통",
    page_icon="🗑️",
    layout="centered"
)

# [디자인] 따뜻한 카페 분위기 CSS
st.markdown("""
    <style>
    .stApp {background-color: #FFF9F0;}
    h1, h2, h3, p, div, span {color: #4A4A4A !important;}
    .stChatMessage {
        background-color: #FFFFFF;
        border-radius: 20px;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.05);
        padding: 15px;
        border: 1px solid #F0E6D2;
    }
    .stButton > button {
        background-color: #FFD180;
        color: white;
        border-radius: 10px;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# [비밀 키 로드]
try:
    api_key = st.secrets["OPENAI_API_KEY"]
except:
    st.error("🚨 API 키를 찾을 수 없습니다.")
    st.stop()

# 2. 사이드바 UI
with st.sidebar:
    # [애니메이션 추가] 따뜻한 차 한잔 하는 로티 (힐링 감성)
    lottie_url = "https://lottie.host/5aee9530-555e-400b-93f8-661b0de2931a/j8J4Wv84lO.json"
    lottie_json = load_lottieurl(lottie_url)
    
    if lottie_json:
        st_lottie(lottie_json, height=150, key="coffee")
    
    st.title("🗑️ 감정 쓰레기통")
    st.caption("마음이 편안해지는 대나무숲 🌿")
    st.markdown("---")
    
    # 상담사 선택
    selected_persona = st.selectbox(
        "오늘의 말동무",
        ["사이다 형 (버럭형)", "토닥이 (공감형)", "차분한 박사 (분석형)", "욕쟁이 할매 (유머형)"],
        index=0
    )

    # 상담사별 설정
    if "사이다" in selected_persona:
        avatar_img = "🍺"
        welcome_msg = "왔냐? 오늘 무슨 개같은 일이 있었는데? 썰 좀 풀어봐. 내가 다 들어줄게!"
        system_prompt = "너는 다혈질인 '사이다 형'이다. 반말을 쓰고 화를 내며 위로해라."
        
    elif "토닥이" in selected_persona:
        avatar_img = "🍀"
        welcome_msg = "어서 오세요.. 따뜻한 차 한잔하면서 이야기해요. 다 들어줄게요."
        system_prompt = "너는 따뜻한 '토닥이'다. 존댓말을 쓰고 깊이 공감해라."
        
    elif "박사" in selected_persona:
        avatar_img = "🎓"
        welcome_msg = "반갑습니다. 상황을 객관적으로 말씀해 주세요. 분석해 드리겠습니다."
        system_prompt = "너는 냉철한 '심리 박사'다. 논리적으로 분석해라."
        
    else: # 욕쟁이 할매
        avatar_img = "👵"
        welcome_msg = "아이고 내 새끼 왔나! 얼굴이 와 이리 반쪽이 됐노. 할미한테 다 일러라."
        system_prompt = "너는 구수한 사투리를 쓰는 '욕쟁이 할머니'다."
    
    st.markdown("---")
    
    # [수동 리셋 버튼]
    if st.button("✨ 새 마음으로 대화 지우기"):
        st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]
        st.rerun()

# 3. 메인 로직
if "current_persona" not in st.session_state:
    st.session_state.current_persona = selected_persona

if selected_persona != st.session_state.current_persona:
    st.session_state.current_persona = selected_persona
    st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]
    st.rerun()

st.header(f"{avatar_img} {selected_persona.split('(')[0]}")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": welcome_msg}]

for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        st.chat_message(msg["role"], avatar=avatar_img).write(msg["content"])
    else:
        st.chat_message(msg["role"], avatar="😢").write(msg["content"])

if prompt := st.chat_input("욕을 쓰거나 소리를 질러도 됩니다."):
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
