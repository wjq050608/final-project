# frontend/app.py
from pprint import pprint

import pandas as pd
import streamlit as st
import  os
import sys
from dotenv import load_dotenv
from pywin.Demos.cmdserver import flags
import socket

st.set_page_config(page_title="AI Quiz Generator", layout="wide")



current_script_path = os.path.abspath(__file__)
# Gets the directory where the current script is located
current_dir = os.path.dirname(current_script_path)
# Get the upper-level directory
parent_dir = os.path.dirname(current_dir)
# Build the path to the utils directory
project_path = os.path.join(parent_dir)
# Add the utils directory to sys.path
sys.path.append(project_path)

load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

from utils.keyword_extractor import KeywordExtractor
from utils.question_generator import QuestionGenerator
from utils.pdf_processor import PDFProcessor

def check_connection(host="api.deepseek.com", port=443, timeout=5):
    try:
        socket.create_connection((host, port), timeout=timeout)
        return True
    except OSError:
        return False


def main():
    st.title("📝 AI-Powered Quiz Generator")
    st.markdown("Upload a textbook chapter PDF to generate quiz questions")

    # 文件上传
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if not uploaded_file:
        st.stop()

    # Processing PDF
    with st.spinner("Processing PDF..."):
        # Save temporary files
        temp_path = "temp.pdf"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

            # Extract text
            processor = PDFProcessor(temp_path)
            text = processor.extract_text()
            st.session_state['full_text'] = text  # Save to session state

    # Keyword extraction
    extractor = KeywordExtractor()
    keywords = extractor.extract_keywords(text)
    st.sidebar.subheader("Detected Keywords")
    st.sidebar.write(", ".join(keywords[:10]))

    # User configuration
    st.sidebar.subheader("Settings")
    question_types = st.sidebar.multiselect(
        "Question Types",
        ["MCQ", "True/False", "Fill-in-the-Blank"],
        default=["MCQ"]
    )
    num_questions = st.sidebar.slider("Number of Questions", 1, 20, 5)

    if not check_connection():
        st.error("Unable to connect to DeepSeek API, please check network connection")
        st.stop()

    # Generating problem
    if st.button("✨ Generate Questions"):
        generator = QuestionGenerator()
        with st.spinner("Generating questions..."):
            print("===="*20)
            pprint("question_types:{}".format(question_types))
            pprint("num_questions:{}".format(num_questions))
            questions = generator.generate_questions(
                text, keywords, question_types, num_questions
            )

        if not questions:
            st.error("Failed to generate questions. Please try again.")
            return

        # Display problem
        st.subheader("Generated Questions")
        df = pd.DataFrame(questions)

        # Edit mode
        edited_df = st.data_editor(
            df,
            column_config={
                "type": st.column_config.SelectboxColumn(
                    "Type", options=["MCQ", "True/False", "Fill-in-the-Blank"]
                ),
                "question": "Question",
                "options": st.column_config.ListColumn(
                    "Options", help="For MCQ only"
                ),
                "answer": "Answer",
                "explanation": "Explanation"
            },
            num_rows="dynamic"
        )

        # Export function
        st.download_button(
            label="📥 Export to CSV",
            data=edited_df.to_csv(index=False).encode(),
            file_name="generated_questions.csv",
            mime="text/csv"
        )



if __name__ == "__main__":
    main()