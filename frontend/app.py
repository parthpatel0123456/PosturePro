import streamlit as st

st.markdown("""
    <style>
        h1 {
            font-size: 4rem;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

st.html("<h1>Posture Pro</h1>")
st.html("<h2>Improve your posture in real time with AI.</h2>")
st.html("<p>This tool uses Google’s MediaPipe Pose model to analyze your body landmarks and classify posture as Good, Slouching, or Leaning — all through your webcam.</p>")
st.html("<p>Built with Python, FastAPI, and Streamlit, it demonstrates how computer vision can help track ergonomic habits and prevent fatigue during long work or study sessions.")
