import streamlit as st
import os
import fitz  # PyMuPDF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from spellchecker import SpellChecker  # Import the SpellChecker class from pyspellchecker
import tempfile
import pandas as pd

st.title("RESUME RANKER")

# User input for skills
skills = st.text_input("Enter Skills (comma-separated):")

# User input for job description
job_description = st.text_area("Enter Job Description:")

# User input for uploading multiple PDF resumes
pdf_resumes = st.file_uploader("Upload Resumes/CVs", type=["pdf"], accept_multiple_files=True)

if st.button("Rank Resumes"):
    if not pdf_resumes:
        st.warning("Please upload PDF resumes.")
    else:
        skills = [skill.strip() for skill in skills.split(',')]
        job_description = job_description.lower()
        resume_data = []

        # Function to extract text from a PDF file using PyMuPDF (fitz)
        def extract_text_from_pdf(pdf_path):
            text = ""
            with fitz.open(pdf_path) as doc:
                for page in doc:
                    text += page.get_text()
            return text

        # Loop through all uploaded PDF resumes and extract text
        for pdf_resume in pdf_resumes:
            if pdf_resume.type == "application/pdf":
                with tempfile.NamedTemporaryFile(delete=False) as temp_pdf:
                    temp_pdf.write(pdf_resume.read())
                    temp_pdf_name = temp_pdf.name
                pdf_text = extract_text_from_pdf(temp_pdf_name).lower()
                resume_data.append((pdf_resume.name, pdf_text))
                os.remove(temp_pdf_name)

        if not resume_data:
            st.warning("No PDF resumes found in the uploaded files.")
        else:
            resume_rankings = []

            # Loop through resumes and check for the presence of input skills
            for resume_name, resume_text in resume_data:
                matching_skills = [skill for skill in skills if skill.lower() in resume_text]
                similarity_score =( len(matching_skills) / len(skills)  )# Calculate a simple similarity score
                missing_skills = [skill for skill in skills if skill.lower() not in resume_text]

                # Calculate the cosine similarity between job description and resume
                tfidf_vectorizer = TfidfVectorizer()
                job_description_matrix = tfidf_vectorizer.fit_transform([job_description])
                resume_matrix = tfidf_vectorizer.transform([resume_text])
                job_description_similarity = cosine_similarity(job_description_matrix, resume_matrix)
                job_description_similarity = (job_description_similarity[0][0])
                
                similarity_score = round(similarity_score * 100, 2)
                job_description_similarity = round(job_description_similarity * 100, 2)

                resume_rankings.append((resume_name, f"{similarity_score}%", f"{job_description_similarity}%", missing_skills))

            # Sort the resumes by similarity score in descending order
            resume_rankings.sort(key=lambda x: x[1], reverse=True)

            # Create a DataFrame to display the results
            df = pd.DataFrame(resume_rankings, columns=["File Name", "Skills Match ", "Job Description Match ", "Missing Skills"])
            

           
            st.subheader("Ranked Resumes:")
            st.dataframe(df)
