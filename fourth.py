import streamlit as st
import pandas as pd
from datetime import datetime
from utils import load_students, load_attendance, save_attendance

st.title("📋 Attendance Tracking")

# Date selection
selected_date = st.date_input("Select Date", datetime.now())

# Course selection
students_df = load_students()
courses = students_df['course'].unique()
selected_course = st.selectbox("Select Course", courses)

# Filter students by course
course_students = students_df[students_df['course'] == selected_course]

if not course_students.empty:
    st.subheader(f"Mark Attendance for {selected_course}")
    
    # Create attendance form
    with st.form("attendance_form"):
        attendance_data = []
        
        for _, student in course_students.iterrows():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"{student['student_id']} - {student['name']}")
            with col2:
                status = st.selectbox(
                    "Status",
                    options=['Present', 'Absent'],
                    key=f"status_{student['student_id']}"
                )
            attendance_data.append({
                'date': selected_date.strftime('%Y-%m-%d'),
                'student_id': student['student_id'],
                'course': selected_course,
                'status': status
            })
        
        submit_button = st.form_submit_button("Submit Attendance")
        
        if submit_button:
            attendance_df = load_attendance()
            
            # Check if attendance already exists for the date and course
            mask = (attendance_df['date'] == selected_date.strftime('%Y-%m-%d')) & \
                   (attendance_df['course'] == selected_course)
            
            if any(mask):
                st.error("Attendance already marked for this date and course!")
            else:
                new_attendance = pd.DataFrame(attendance_data)
                attendance_df = pd.concat([attendance_df, new_attendance], ignore_index=True)
                save_attendance(attendance_df)
                st.success("Attendance marked successfully!")

else:
    st.warning("No students found for the selected course.")

# View Today's Attendance
st.subheader("View Today's Attendance")
attendance_df = load_attendance()

if not attendance_df.empty:
    today_attendance = attendance_df[
        attendance_df['date'] == selected_date.strftime('%Y-%m-%d')
    ]
    
    if not today_attendance.empty:
        # Merge with student names
        display_df = today_attendance.merge(
            students_df[['student_id', 'name']],
            on='student_id'
        )
        st.dataframe(
            display_df[['name', 'course', 'status']],
            use_container_width=True
        )
    else:
        st.info("No attendance records for selected date.")
else:
    st.info("No attendance records available.")