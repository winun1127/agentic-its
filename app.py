import streamlit as st
from pathlib import Path

from lib.agents import QuizGenerator


st.set_page_config(
    page_title="AI Tutor",
    initial_sidebar_state="collapsed",
)

st.markdown("""
# [PoC Demo] AI Tutor
            
본 앱은 **퀴즈 생성-채점-피드백 과정을 지원**하는 AI 튜터의 Proof-of-Concept 데모입니다.

1. **퀴즈 생성**: 교수자가 PDF 파일을 업로드하고 퀴즈 주제를 입력하면 AI 튜터가 퀴즈를 생성합니다.
2. 퀴즈 풀기: 학습자가 퀴즈를 풀고 제출합니다.
3. 퀴즈 채점: AI 튜터가 학습자의 답안을 채점하고 피드백을 제공합니다.

---
""")

if "quiz" not in st.session_state:
    st.session_state.quiz = None
if "student_answers" not in st.session_state:
    st.session_state.student_answers = []

# ----------------------------------------------------------------------
# Quiz Generator
# ----------------------------------------------------------------------
st.markdown("#### Step 1. 퀴즈 생성")

uploaded_file = st.file_uploader("강의자료 또는 텍스트북과 같은 PDF 파일을 업로드합니다.", type=["pdf"])

if uploaded_file is not None:
    # Save file
    Path("./docs").mkdir(parents=True, exist_ok=True)
    file_path = Path(f"./docs/{uploaded_file.name}")
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getvalue())
        
    if file_path.exists():
        st.success(f"File '{uploaded_file.name}' is successfully uploaded.")
        
        topic = st.text_input("어떤 주제에 대한 퀴즈를 생성하시겠습니까?")
        quiz_generator = QuizGenerator()
        
        if st.button("퀴즈 생성하기"):
            response = quiz_generator.get_response(topic)
            st.session_state.quiz = response["quiz"]
            
    else:
        st.error(f"File '{uploaded_file.name}' is not uploaded.")

if st.session_state.quiz is not None:
    with st.container(border=True):
        with st.chat_message("assistant"):
            st.write(st.session_state.quiz.as_str)

    st.page_link("pages/quiz.py", label="퀴즈 풀어보기", icon="📝")

        