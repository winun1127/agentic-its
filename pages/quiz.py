import streamlit as st

st.set_page_config(
    page_title="AI Tutor",
    initial_sidebar_state="collapsed",
)

st.markdown("""
# [PoC Demo] AI Tutor
            
본 앱은 **퀴즈 생성-채점-피드백 과정을 지원**하는 AI 튜터의 Proof-of-Concept 데모입니다.

1. 퀴즈 생성: 교수자가 PDF 파일을 업로드하고 퀴즈 주제를 입력하면 AI 튜터가 퀴즈를 생성합니다.
2. **퀴즈 풀기**: 학습자가 퀴즈를 풀고 제출합니다.
3. 퀴즈 채점: AI 튜터가 학습자의 답안을 채점하고 피드백을 제공합니다.

> **Tip**: _테스트를 위해 정답 또는 틀린 답변(예: '잘 모르겠다' 등)을 입력해보세요!_
---
""")

# ----------------------------------------------------------------------
# Quiz page
# ----------------------------------------------------------------------
st.markdown("#### Step 2. 퀴즈 풀기")

if "quiz" not in st.session_state:
    st.session_state.quiz = None   
if "student_answers" not in st.session_state:
    st.session_state.student_answers = []

for i, (q, a) in enumerate(zip(
    st.session_state.quiz.questions, st.session_state.quiz.answers
)):
    st.write(f"**Q{i+1}**. {q}")
    student_answer = st.text_input(f"본인이 생각하는 Q{i+1}의 정답을 입력하세요.", key=f"answer_{i}", placeholder=a)
    
    if student_answer:
        st.session_state.student_answers.append("")
        st.write(f"당신이 입력한 정답: '{student_answer}'")
        st.session_state.student_answers[i] = student_answer
    else:
        st.write("정답을 입력하세요.")
        

st.page_link("pages/report.py", label="결과보기", icon="📝")