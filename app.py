import streamlit as st
import pandas as pd
from logic import calculate_stats, get_grade_distribution

# Page configuration
st.set_page_config(page_title="Grade Analytics Dashboard", layout="wide")
st.title("📊 Grade Analytics Dashboard")

# Initialize session state for student list
if 'students' not in st.session_state:
    st.session_state.students = []

# Task B: Sidebar for Data Entry
st.sidebar.header("📝 Add Student Grade")

with st.sidebar.form("student_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        student_name = st.text_input(
            "Student Last Name",
            placeholder="e.g., Smith"
        )
    
    with col2:
        student_grade = st.number_input(
            "Grade",
            min_value=0,
            max_value=100,
            step=1,
            value=0
        )
    
    submitted = st.form_submit_button("➕ Add Student")
    
    if submitted:
        if student_name:
            st.session_state.students.append({
                'Name': student_name,
                'Grade': int(student_grade)
            })
            st.sidebar.success(f"Added {student_name} with grade {student_grade}!")
        else:
            st.sidebar.error("Please enter a student name")

# Create DataFrame from session state
if st.session_state.students:
    df = pd.DataFrame(st.session_state.students)
    
    # Task C: Display Metrics and Statistics
    st.header("📈 Statistics")
    
    stats = calculate_stats(df)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(label="📊 Mean", value=f"{stats['mean']:.2f}")
    
    with col2:
        st.metric(label="📌 Median", value=f"{stats['median']:.2f}")
    
    with col3:
        st.metric(label="⬇️ Min", value=f"{stats['min']}")
    
    with col4:
        st.metric(label="⬆️ Max", value=f"{stats['max']}")
    
    with col5:
        st.metric(label="📊 Std Dev", value=f"{stats['std']:.2f}")
    
    # Display student data table
    st.subheader("👥 Student Grades")
    st.dataframe(
        df.sort_values('Grade', ascending=False),
        use_container_width=True,
        hide_index=True
    )
    
    # Task D: Visualization - Grade Distribution
    st.header("📉 Grade Distribution")
    
    distribution = get_grade_distribution(df)
    
    st.bar_chart(
        distribution.set_index('Grade Bracket')['Count'],
        use_container_width=True
    )
    
    # Additional visualization options
    st.subheader("Grade Breakdown by Bracket")
    st.dataframe(
        distribution,
        use_container_width=True,
        hide_index=True
    )
    
    # Clear data button
    if st.button("🗑️ Clear All Data"):
        st.session_state.students = []
        st.rerun()

else:
    st.info("👈 Use the sidebar to add student grades and get started!")
