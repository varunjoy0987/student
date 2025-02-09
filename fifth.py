import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_students, load_attendance, calculate_attendance_stats
from datetime import datetime, timedelta

st.title("📊 Attendance Reports")

# Load data
students_df = load_students()
attendance_df = load_attendance()

# Date range selection
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
with col2:
    end_date = st.date_input("End Date", datetime.now())

# Course selection
courses = students_df['course'].unique()
selected_course = st.selectbox("Select Course", ['All Courses'] + list(courses))

# Filter attendance data
filtered_attendance = attendance_df[
    (attendance_df['date'] >= start_date.strftime('%Y-%m-%d')) &
    (attendance_df['date'] <= end_date.strftime('%Y-%m-%d'))
]

if selected_course != 'All Courses':
    filtered_attendance = filtered_attendance[filtered_attendance['course'] == selected_course]

# Calculate statistics
if not filtered_attendance.empty:
    st.subheader("Attendance Overview")
    
    # Overall statistics
    total_classes = len(filtered_attendance['date'].unique())
    total_present = len(filtered_attendance[filtered_attendance['status'] == 'Present'])
    total_absent = len(filtered_attendance[filtered_attendance['status'] == 'Absent'])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Classes", total_classes)
    col2.metric("Total Present", total_present)
    col3.metric("Total Absent", total_absent)
    
    # Attendance trend
    st.subheader("Attendance Trend")
    daily_attendance = filtered_attendance.groupby('date').agg({
        'status': lambda x: (x == 'Present').sum() / len(x) * 100
    }).reset_index()
    
    fig = px.line(
        daily_attendance,
        x='date',
        y='status',
        title='Daily Attendance Percentage',
        labels={'date': 'Date', 'status': 'Attendance %'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Student-wise attendance
    st.subheader("Student-wise Attendance")
    student_stats = calculate_attendance_stats()
    student_stats = student_stats.merge(
        students_df[['student_id', 'name']],
        left_index=True,
        right_on='student_id'
    )
    
    st.dataframe(
        student_stats[['name', 'Total', 'Present', 'Percentage']],
        use_container_width=True
    )
    
    # Export options
    st.subheader("Export Data")
    if st.button("Export to CSV"):
        export_df = filtered_attendance.merge(
            students_df[['student_id', 'name']],
            on='student_id'
        )
        st.download_button(
            label="Download CSV",
            data=export_df.to_csv(index=False).encode('utf-8'),
            file_name=f"attendance_report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime='text/csv'
        )
else:
    st.info("No attendance records found for the selected criteria.")

# Footer
st.markdown("---")
st.markdown("Generate and export attendance reports for analysis.")