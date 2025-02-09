import pandas as pd
from datetime import datetime
import streamlit as st
from sqlalchemy.orm import Session
from models import Student, Course, Attendance, Payment, get_db
from contextlib import contextmanager

@contextmanager
def get_db_session():
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()

def init_data():
    # Database tables are already created by SQLAlchemy
    pass

def load_students():
    with get_db_session() as db:
        students = db.query(Student).all()
        data = [{
            'student_id': s.student_id,
            'name': s.name,
            'course': s.course,
            'year': s.year
        } for s in students]
        return pd.DataFrame(data)

def load_attendance():
    with get_db_session() as db:
        attendances = db.query(Attendance).all()
        data = [{
            'date': str(a.date),
            'student_id': a.student_id,
            'course': a.course,
            'status': a.status
        } for a in attendances]
        return pd.DataFrame(data)

def load_courses():
    with get_db_session() as db:
        courses = db.query(Course).all()
        data = [{
            'course_id': c.course_id,
            'course_name': c.course_name
        } for c in courses]
        return pd.DataFrame(data)

def save_students(df):
    with get_db_session() as db:
        # Instead of deleting all students, update or insert as needed
        existing_students = {s.student_id: s for s in db.query(Student).all()}

        for _, row in df.iterrows():
            student_id = row['student_id']
            if student_id in existing_students:
                # Update existing student
                student = existing_students[student_id]
                student.name = row['name']
                student.course = row['course']
                student.year = row['year']
            else:
                # Add new student
                student = Student(
                    student_id=student_id,
                    name=row['name'],
                    course=row['course'],
                    year=row['year']
                )
                db.add(student)

        # Remove students that are no longer in the dataframe and have no attendance records
        current_student_ids = set(df['student_id'])
        for student_id, student in existing_students.items():
            if student_id not in current_student_ids:
                # Check if student has attendance records
                has_attendance = db.query(Attendance).filter_by(student_id=student_id).first() is not None
                if not has_attendance:
                    db.delete(student)

        db.commit()

def save_attendance(df):
    with get_db_session() as db:
        for _, row in df.iterrows():
            attendance = Attendance(
                date=datetime.strptime(row['date'], '%Y-%m-%d').date(),
                student_id=row['student_id'],
                course=row['course'],
                status=row['status']
            )
            db.add(attendance)
        db.commit()

def save_courses(df):
    with get_db_session() as db:
        existing_courses = {c.course_id: c for c in db.query(Course).all()}

        for _, row in df.iterrows():
            course_id = row['course_id']
            if course_id in existing_courses:
                # Update existing course
                course = existing_courses[course_id]
                course.course_name = row['course_name']
            else:
                # Add new course
                course = Course(
                    course_id=course_id,
                    course_name=row['course_name']
                )
                db.add(course)

        db.commit()

def load_payments():
    with get_db_session() as db:
        payments = db.query(Payment).all()
        data = [{
            'student_id': p.student_id,
            'amount': p.amount,
            'payment_date': str(p.payment_date),
            'status': p.status
        } for p in payments]
        return pd.DataFrame(data)

def save_payment(student_id, amount, payment_date, status='Pending'):
    with get_db_session() as db:
        payment = Payment(
            student_id=student_id,
            amount=amount,
            payment_date=payment_date,
            status=status
        )
        db.add(payment)
        db.commit()

def calculate_attendance_stats():
    with get_db_session() as db:
        attendance_df = load_attendance()
        if len(attendance_df) == 0:
            return pd.DataFrame()

        stats = attendance_df.groupby('student_id').agg({
            'status': ['count', lambda x: (x == 'Present').sum()]
        })
        stats.columns = ['Total', 'Present']
        stats['Percentage'] = (stats['Present'] / stats['Total'] * 100).round(2)
        return stats