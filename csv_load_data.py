import random
import plotly.graph_objects as go
import streamlit as st
import pandas as pd

# Define the possible subjects
subjects = ["English Language", "Social Studies", "Mathematics", "Integrated Science", "Zambian Languages", "Creative and Technology Studies"]

# Define student pathways
pathways = {
    "STEM": ["Mathematics", "Integrated Science"],
    "Humanities and Social Sciences": ["English Language", "Social Studies"],
    "Linguistic and Cultural Studies": ["Zambian Languages", "English Language"],
    "Creative and Design": ["Creative and Technology Studies"],
}

# Load student data from CSV
@st.cache
def load_student_data(file_path):
    return pd.read_csv(file_path)

# Function to filter students based on user-selected criteria
def filter_students(students, min_age=None, max_age=None, min_grade=None, max_grade=None, school=None):
    filtered_students = students
    if min_age:
        filtered_students = [student for student in filtered_students if student['Age'] >= min_age]
    if max_age:
        filtered_students = [student for student in filtered_students if student['Age'] <= max_age]
    if min_grade:
        filtered_students = [student for student in filtered_students if student['Grade'] >= min_grade]
    if max_grade:
        filtered_students = [student for student in filtered_students if student['Grade'] <= max_grade]
    if school and school != "All":
        filtered_students = [student for student in filtered_students if student['School'] == school]
    return filtered_students

# Function to generate and display a radar chart
def generate_radar_chart(student, title):
    subject_scores = student["Subjects"]
    values = [subject_scores.get(subject, 0) for subject in subjects]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=subjects,
        fill='toself',
        name=student['Name']
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[50, 100]  # Set the range of the radar chart
            ),
        ),
        showlegend=True,
        title=title,
        height=600,
        width=800,
    )

    st.plotly_chart(fig)

# Function to generate and display a subject analysis report
def generate_subject_analysis(students):
    subject_data = {subject: [] for subject in subjects}
    for student in students:
        for subject, score in student["Subjects"].items():
            subject_data[subject].append(score)

    show_details = st.checkbox("Show Subject Details")

    for subject, scores in subject_data.items():
        st.subheader(f"{subject} Analysis")
        st.write(f"Average Score: {sum(scores) / len(scores):.2f}")
        st.write(f"Minimum Score: {min(scores)}")
        st.write(f"Maximum Score: {max(scores)}")

        if show_details:
            # Plot the score distribution for the subject
            fig = go.Figure(data=[go.Histogram(x=scores, nbinsx=10)])
            fig.update_layout(
                title=f"{subject} Score Distribution",
                xaxis_title="Score",
                yaxis_title="Count",
            )
            st.plotly_chart(fig)

# Function to generate and display a pathway analysis report
def generate_pathway_analysis(students):
    pathway_data = {pathway: [] for pathway in pathways}

    for student in students:
        student_subjects = set(subject for subject, score in student["Subjects"].items() if score >= 70)
        for pathway, required_subjects in pathways.items():
            if set(required_subjects).issubset(student_subjects):
                pathway_data[pathway].append(student)

    show_details = st.checkbox("Show Pathway Details")

    for pathway, students_in_pathway in pathway_data.items():
        st.subheader(f"{pathway} Pathway")

        if show_details:
            for student in students_in_pathway:
                st.write(f"{student['Name']}: {', '.join([f'{subject}: {student['Subjects'][subject]}' for subject in pathways[pathway]])}")

            # Plot radar charts for students in the pathway
            for student in students_in_pathway:
                generate_radar_chart(student, f"{pathway} Pathway - {student['Name']}")

# Function to generate and display a grade comparison report
def generate_grade_comparison(students):
    grade_data = {}
    for student in students:
        grade = student["Grade"]
        if grade not in grade_data:
            grade_data[grade] = []
        grade_data[grade].append(student)

    show_details = st.checkbox("Show Grade Details")
    show_at_risk = st.checkbox("Show At-Risk Students")
    show_excelling = st.checkbox("Show Excelling Students")

    for grade, students_in_grade in grade_data.items():
        st.subheader(f"Grade {grade} Performance Analysis")

        # Calculate the overall score for each student
        student_scores = [sum(student["Subjects"].values()) / len(subjects) for student in students_in_grade]

        # Plot the score distribution for the grade
        fig = go.Figure(data=[go.Histogram(x=student_scores, nbinsx=10)])
        fig.update_layout(
            title=f"Grade {grade} Score Distribution",
            xaxis_title="Overall Score",
            yaxis_title="Count",
        )
        st.plotly_chart(fig)

        # Display grade performance summary
        st.write("**Grade Performance Summary:**")
        st.write(f"Average Score: {sum(student_scores) / len(student_scores):.2f}")
        st.write(f"Minimum Score: {min(student_scores)}")
        st.write(f"Maximum Score: {max(student_scores)}")

        if show_details:
            # Display student details and radar charts
            st.write("**Student Details:**")
            for student in students_in_grade:
                st.write(f"{student['Name']}: {', '.join([f'{subject}: {score}' for subject, score in student['Subjects'].items()])}")
                generate_radar_chart(student, f"Grade {grade} - {student['Name']}")

        if show_at_risk:
            st.write("**At-Risk Students:**")
            at_risk_students = [student for student in students_in_grade if sum(student["Subjects"].values()) / len(subjects) < 60]
            for student in at_risk_students:
                st.write(f"{student['Name']}: {', '.join([f'{subject}: {score}' for subject, score in student['Subjects'].items()])}")

        if show_excelling:
            st.write("**Excelling Students:**")
            excelling_students = [student for student in students_in_grade if sum(student["Subjects"].values()) / len(subjects) >= 90]
            for student in excelling_students:
                st.write(f"{student['Name']}: {', '.join([f'{subject}: {score}' for subject, score in student['Subjects'].items()])}")

# Streamlit app
st.set_page_config(
    page_title="ScholarSense",
    page_icon="📚",
    layout="wide",
)

# Title and sidebar
st.title("ScholarSense")

# Sidebar menu to choose reports
report_choice = st.sidebar.radio("Choose Report:", ("STUDENT PROFILES", "SUBJECT ANALYSIS", "PATHWAY ANALYSIS", "GRADE COMPARISON"))

# Load student data
st.write("Please upload the CSV file containing student data.")
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file is not None:
    students_df = load_student_data(uploaded_file)
    random_students = students_df.to_dict(orient="records")
    filtered_students = filter_students(random_students, None, None, None, None, "All")

    if report_choice == "STUDENT PROFILES":
        # Create a dropdown menu to select students
        selected_student_index = st.selectbox("Select a Student:", range(len(filtered_students)))
        selected_student = filtered_students[selected_student_index]

        # Display selected student details
        if 'Name' in selected_student:
            st.write(f"**STUDENT:** {selected_student['Name']}")
        else:
            st.write("No student name found in the selected student data.")
        st.write(f"**AGE:** {selected_student['Age']}")
        st.write(f"**GRADE:** {selected_student['Grade']}")
        st.write(f"**SCHOOL:** {selected_student['School']}")

        # Generate and display radar chart for the selected student
        generate_radar_chart(selected_student, f"Subject Radar Chart for {selected_student['Name']}")

    elif report_choice == "SUBJECT ANALYSIS":
        # Generate and display subject analysis report
        generate_subject_analysis(filtered_students)

    elif report_choice == "PATHWAY ANALYSIS":
        # Generate and display pathway analysis report
        generate_pathway_analysis(filtered_students)

    elif report_choice == "GRADE COMPARISON":
        # Generate and display grade comparison report
        generate_grade_comparison(filtered_students)