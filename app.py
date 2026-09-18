import streamlit as st
import re
import random
from transformers import pipeline

st.set_page_config(
    page_title="AI MCQ Generator",
    page_icon="📝",
    layout="wide"
)

st.title("📝 AI MCQ Generator")
st.write("Generate multiple-choice questions from any study material using AI.")

@st.cache_resource
def load_model():
    return pipeline(
        "text2text-generation",
        model="google/flan-t5-small"
    )

def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def generate_mcqs(text, number):
    model = load_model()

    prompt = f"""
Create {number} multiple choice questions from the following study material.

Rules:
- Each question must have exactly 4 options.
- Only one option must be correct.
- Questions must be based only on the given material.
- Include the correct answer.
- Include a difficulty level.
- Use this exact format:

Q1: question
A) option
B) option
C) option
D) option
Answer: A
Difficulty: Easy

Study material:
{text}
"""

    result = model(
        prompt,
        max_new_tokens=700,
        do_sample=True,
        temperature=0.7
    )

    return result[0]["generated_text"]


def fallback_mcqs(text, number):
    sentences = re.split(r"(?<=[.!?])\s+", text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 30]

    if not sentences:
        return "Please enter more detailed study material."

    output = []

    for i in range(min(number, len(sentences))):
        sentence = sentences[i]

        words = re.findall(r"\b[A-Za-z]{5,}\b", sentence)

        if not words:
            continue

        answer = words[0]

        options = [answer]

        for word in words[1:]:
            if word not in options:
                options.append(word)

            if len(options) == 4:
                break

        while len(options) < 4:
            options.append("None of the above")

        random.shuffle(options)

        answer_letter = chr(65 + options.index(answer))

        output.append(
            f"""
Q{i + 1}: Which of the following is mentioned in the study material?

A) {options[0]}
B) {options[1]}
C) {options[2]}
D) {options[3]}

Answer: {answer_letter}
Difficulty: Easy
"""
        )

    return "\n".join(output)


with st.sidebar:
    st.header("⚙️ Settings")

    number = st.slider(
        "Number of Questions",
        min_value=1,
        max_value=10,
        value=5
    )

    difficulty = st.selectbox(
        "Difficulty",
        ["Easy", "Medium", "Hard", "Mixed"]
    )

    st.info(
        "Enter your study material in the main area and click "
        "'Generate MCQs'."
    )


st.subheader("📚 Study Material")

text = st.text_area(
    "Paste your notes, paragraph, textbook content, or topic here:",
    height=300,
    placeholder="Example: Artificial Intelligence is a branch of computer science..."
)

generate_button = st.button(
    "🚀 Generate MCQs",
    type="primary",
    use_container_width=True
)

if generate_button:

    if not text.strip():
        st.warning("⚠️ Please enter some study material first.")

    elif len(text.strip()) < 50:
        st.warning("⚠️ Please enter at least a few sentences of study material.")

    else:
        with st.spinner("🤖 Generating MCQs..."):

            try:
                clean_input = clean_text(text)

                generated = generate_mcqs(
                    clean_input,
                    number
                )

                st.session_state["mcqs"] = generated

            except Exception:
                st.warning(
                    "AI model could not generate the questions. "
                    "Using the built-in question generator instead."
                )

                st.session_state["mcqs"] = fallback_mcqs(
                    clean_text(text),
                    number
                )


if "mcqs" in st.session_state:

    st.divider()

    st.subheader("📋 Generated MCQs")

    st.text_area(
        "Your Questions",
        st.session_state["mcqs"],
        height=600
    )

    st.download_button(
        label="📥 Download MCQs",
        data=st.session_state["mcqs"],
        file_name="generated_mcqs.txt",
        mime="text/plain",
        use_container_width=True
    )
