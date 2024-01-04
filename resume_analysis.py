import streamlit as st
import openai
import docx  # Library for handling .docx files
import pdfplumber  # Library for handling .pdf files

def extract_text_from_docx(file):
    text = ""
    try:
        doc = docx.Document(file)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        print(f"Error while extracting text from .docx: {str(e)}")
        return None

def extract_text_from_pdf(file):
    text = ""
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error while extracting text from .pdf: {str(e)}")
        return None

def query_gpt_3(docx_text, user_query, api_key):
    try:
        openai.api_key = api_key
        prompt = f"{docx_text}\nUser query: {user_query}\nAI response:"
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=100  # Reducing the completion length
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    st.title("GPT-3 Text Generation")

    api_key = st.text_input("Enter your OpenAI API key")

    uploaded_file = st.file_uploader("Upload a file", type=["docx", "pdf"])

    if uploaded_file is not None:
        if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":  # Check for .docx MIME type
            docx_text = extract_text_from_docx(uploaded_file)
        elif uploaded_file.type == "application/pdf":  # Check for .pdf MIME type
            docx_text = extract_text_from_pdf(uploaded_file)
        else:
            st.error("Invalid file type. Only .docx and .pdf files are supported.")
            return

        user_query = st.text_input("Enter your query")

        if user_query != "":
            gpt_response = query_gpt_3(docx_text, user_query, api_key)
            st.write("GPT-3 Response:")
            st.text(gpt_response)

if __name__ == "__main__":
    main()
