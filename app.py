import streamlit as st
import pandas as pd
from student import Student
from utils import calculate_statistics

st.title("Student Performance Analyzer")

uploaded = st.file_uploader("Upload CSV", type=["csv"])

if uploaded:
    df = pd.read_csv(uploaded)
    st.dataframe(df)

    st.subheader("Per Student Analysis")

    students = []
    for index, row in df.iterrows():
        name = row["Name"]
        marks = row[1:].tolist()
        student = Student(name, marks)
        students.append(student)

        st.markdown(f"**{name}**")
        st.write(f"Total: {student.total()} | Avg: {student.average():.2f} | Pass: {'✅' if student.is_pass() else '❌'}")

    st.subheader("Overall Statistics")
    all_scores = df.iloc[:, 1:].values.flatten()
    stats = calculate_statistics(all_scores)
    st.write(stats)
