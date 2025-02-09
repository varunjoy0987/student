import pandas as pd
from models import Student, Course, Attendance, get_db
from datetime import datetime

def import_initial_data():
    # Read CSV files
    students_df = pd.read_csv('data/students.csv')
    courses_df = pd.read_csv('data/courses.csv')
    attendance_df = pd.read_csv('data/attendance.csv')

    db = next(get_db())
    try:
        # Clear existing data
        db.query(Attendance).delete()
        db.query(Student).delete()
        db.query(Course).delete()
        db.commit()

        # Import students
        for _, row in students_df.iterrows():
            student = Student(
                student_id=row['student_id'],
                name=row['name'],
                course=row['course'],
                year=row['year']
            )
            db.add(student)

        # Import courses
        for _, row in courses_df.iterrows():
            course = Course(
                course_id=row['course_id'],
                course_name=row['course_name']
            )
            db.add(course)

        # Import attendance
        for _, row in attendance_df.iterrows():
            attendance = Attendance(
                date=datetime.strptime(row['date'], '%Y-%m-%d').date(),
                student_id=row['student_id'],
                course=row['course'],
                status=row['status']
            )
            db.add(attendance)

        db.commit()
        print("Data imported successfully!")
    except Exception as e:
        print(f"Error importing data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import_initial_data()