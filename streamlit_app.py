import streamlit as st
import requests
import io
import pandas as pd

# Set the API URL
API_URL = "http://web:8000/api/v1"

st.title("Resume Analyzer")

# File upload
uploaded_file = st.file_uploader("Choose a resume PDF file", type="pdf")

if uploaded_file is not None:
    # Display the uploaded file
    st.write("Uploaded file:", uploaded_file.name)

    # Create a button to trigger the analysis
    if st.button("Analyze Resume"):
        # Send the file to the API
        files = {"file": ("resume.pdf", uploaded_file.getvalue(), "application/pdf")}
        response = requests.post(f"{API_URL}/resumes/upload", files=files)

        if response.status_code == 200:
            result = response.json()
            st.success("Resume analyzed successfully!")

            # Display the results
            st.subheader("Analysis Results")
            st.write(f"Title: {result['title']}")
            st.write(f"Experience: {result['experience']} years")
            st.write(f"Key Skills: {result['key_skills']}")
            st.write(f"Location: {result['location']}")
            st.write(f"Job Type: {result['job_type']}")
            st.write(f"Seniority Level: {result['seniority_level']}")
            st.write(f"Remote: {'Yes' if result['is_remote'] else 'No'}")
            st.write(f"Predicted Salary: ${result['predicted_salary']:,.2f}")
        else:
            st.error("Error analyzing resume. Please try again.")

# Display all resumes
st.subheader("All Resumes")

if st.button("Refresh Resumes"):
    response = requests.get(f"{API_URL}/resumes/")
    if response.status_code == 200:
        resumes = response.json()
        df = pd.DataFrame(resumes)
        st.dataframe(df)
    else:
        st.error("Error fetching resumes. Please try again.")