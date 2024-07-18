import streamlit as st

from lib.agents import Chatbot
from lib.prompts import REPORT_PROMPT


st.set_page_config(
    page_title="AI Tutor",
    initial_sidebar_state="collapsed",
)

st.markdown("""
# [PoC Demo] AI Tutor
            
본 앱은 **퀴즈 생성-채점-피드백 과정을 지원**하는 AI 튜터의 Proof-of-Concept 데모입니다.

1. 퀴즈 생성: 교수자가 PDF 파일을 업로드하고 퀴즈 주제를 입력하면 AI 튜터가 퀴즈를 생성합니다.
2. 퀴즈 풀기: 학습자가 퀴즈를 풀고 제출합니다.
3. **퀴즈 채점**: AI 튜터가 학습자의 답안을 채점하고 피드백을 제공합니다.

---
""")

# ----------------------------------------------------------------------
# Report page
# ----------------------------------------------------------------------
st.markdown("#### Step 3. 퀴즈 채점")

reporter = Chatbot(system_prompt=REPORT_PROMPT)

for i, (q, a, a_student) in enumerate(zip(
    st.session_state.quiz.questions, st.session_state.quiz.answers, st.session_state.student_answers
)):
    st.write(f"**Q{i+1}**. {q}")
    st.write(f"**내가 입력한 정답**: {a_student}")

    with st.container(border=True):
        with st.chat_message("assistant"):
            st.write_stream(reporter.get_response(
                {
                    "question": q, "answer": a, "student_answer": a_student
                },
                streaming=True,
            ))