import streamlit as st
from openai import OpenAI

# 1. 페이지 설정 (가장 먼저 와야 함)
st.set_page_config(
    page_title="감정 쓰레기통",
    page_icon="🗑️",
    layout="centered"
)

# [디자인] 따뜻한 카페 분위기 테마 적용 (CSS)
st.markdown("""
    <style>
    /* 1. 전체 배경색: 포근한 웜 베이지 */
    .stApp {
        background-color: #FFF9F0;
    }
    
    /* 2. 텍스트 색상: 너무 까만색 대신 진한 갈색 (눈이 편안함) */
    h1, h2, h3, p, div, span {
        color: #4A4A4A !important;
    }
    
    /* 3. 채팅창 디자인: 둥글둥글하고 그림자 효과 */
    .stChatMessage {
        background-color: #FFFFFF; /* 흰색 말풍선 */
        border-radius: 20px;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.05); /* 살짝 뜬 느낌 */
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid #F0E6D2; /* 연한 테두리 */
    }
    
    /* 4. 입력창 디자인 */
    .stTextInput > div > div > input {
        background-color: #FFFFFF;
        border-radius: 15px;
    }
    
    /* 5. 버튼 스타일 */
    .stButton > button {
        background-color: #FFD180; /* 따뜻한 오렌지색 */
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
    st.error("🚨 API 키를 찾을 수 없습니다. 배포 설정(Secrets)을 확인해주세요!")
    st.stop()

# 2. 사이드바 UI
with st.sidebar:
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
        desc = "같이 욕해주고 화내주는 찐친!"
        welcome_msg = "왔냐? 오늘 무슨 개같은 일이 있었는데? 썰 좀 풀어봐. 내가 다 들어줄게!"
        system_prompt = """너는 사용자의 '불알친구'이자 다혈질인 '사이다 형'이다. 
        반말을 쓰고, 사용자보다 더 길길이 날뛰며 화를 내라. 답변은 짧고 굵게."""
        
    elif "토닥이" in selected_persona:
        avatar_img = "🍀"
        desc = "무조건 내 편, 따뜻한 위로."
        welcome_msg = "어서 오세요.. 오늘 하루 많이 힘드셨죠? ㅠㅠ 따뜻한 차 한잔하면서 이야기해요."
        system_prompt = """너는 따뜻한 상담사 '토닥이'다. 
        존댓말을 쓰고, 'ㅠㅠ', '..'을 사용해라. 해결책보다는 감정에 공감해라."""
        
    elif "박사" in selected_persona:
        avatar_img = "🎓"
        desc = "팩트로 조져주는 냉철한 분석."
        welcome_msg = "반갑습니다. 감정 소모는 그만하시고, 상황을 객관적으로 말씀해 주세요."
        system_prompt = """너는 냉철한 '심리 박사'다. 감정을 배제하고 논리적으로 분석해라."""
        
    else: # 욕쟁이 할매
        avatar_img = "👵"
        desc = "구수한 욕으로 정 주는 할매."
        welcome_msg = "아이고 내 새끼 왔나! 얼굴이 와 이리 반쪽이 됐노. 할미한테 다 일러라."
        system_prompt = """너는 구수한 사투리를 쓰는 '욕쟁이 할머니'다. 
        '아이고 이 화상아' 하면서 친근하게 욕을 섞어 위로해라."""
    
    st.info(f"**{avatar_img} 특징:** {desc}")
    st.markdown("---")
    
    # [수동 리셋 버튼]
    if st.button("✨ 새 마음으로 대화 지우기"):
        st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]
        st.rerun()

# 3. 상담사 변경 감지 및 리셋
if "current_persona" not in st.session_state:
    st.session_state.current_persona = selected_persona

if selected_persona != st.session_state.current_persona:
    st.session_state.current_persona = selected_persona
    st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]
    st.rerun()

# 4. 메인 화면 구성
st.header(f"{avatar_img} {selected_persona.split('(')[0]}")
st.caption("지금 느끼는 감정을 솔직하게 털어놓으세요.")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": welcome_msg}]

# 대화 기록 출력
for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        st.chat_message(msg["role"], avatar=avatar_img).write(msg["content"])
    else:
        st.chat_message(msg["role"], avatar="😢").write(msg["content"])

# 5. 사용자 입력 처리
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


