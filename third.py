import streamlit as st
import pandas as pd
import plotly.express as px
from utils import init_data, load_students, load_attendance, calculate_attendance_stats

# Page config
st.set_page_config(
    page_title="Student Attendance System",
    page_icon="📚",
    layout="wide"
)

# Initialize data
init_data()

# Title
st.title("📚 Student Attendance Dashboard")

# Sidebar
st.sidebar.title("Navigation")
st.sidebar.info("Select a page above to manage students, track attendance, or view reports.")

# Main dashboard
col1, col2 = st.columns(2)

with col1:
    st.subheader("Quick Statistics")
    students_df = load_students()
    attendance_df = load_attendance()
    
    total_students = len(students_df)
    total_attendance_records = len(attendance_df)
    
    st.metric("Total Students", total_students)
    st.metric("Total Attendance Records", total_attendance_records)

with col2:
    st.subheader("Recent Attendance Overview")
    if not attendance_df.empty:
        recent_attendance = attendance_df.sort_values('date', ascending=False).head(5)
        recent_attendance = recent_attendance.merge(students_df[['student_id', 'name']], on='student_id')
        st.dataframe(recent_attendance[['date', 'name', 'course', 'status']], use_container_width=True)
    else:
        st.info("No attendance records available")

# Attendance Statistics
st.subheader("Attendance Statistics")
stats = calculate_attendance_stats()

if not stats.empty:
    # Create attendance percentage chart
    fig = px.bar(
        stats.reset_index(),
        x='student_id',
        y='Percentage',
        title='Attendance Percentage by Student',
        labels={'student_id': 'Student ID', 'Percentage': 'Attendance %'}
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No attendance statistics available")

# Footer
st.markdown("---")
st.markdown("### 👥 Student Attendance System")
st.markdown("Navigate to other pages using the sidebar to manage students and track attendance.")