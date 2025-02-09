from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, Enum, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from datetime import datetime
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

# Get database URL from environment variable
DATABASE_URL = "sqlite:///example.db"

# Create database engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True)
    student_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    course = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    attendances = relationship("Attendance", back_populates="student")

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True)
    course_id = Column(String, unique=True, nullable=False)
    course_name = Column(String, nullable=False)

class Attendance(Base):
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    student_id = Column(String, ForeignKey('students.student_id'), nullable=False)
    course = Column(String, nullable=False)
    status = Column(Enum('Present', 'Absent', name='attendance_status'), nullable=False)
    student = relationship("Student", back_populates="attendances")

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Integer)
    student_id = Column(Integer, ForeignKey('students.id'))
    payment_date = Column(Date, nullable=False)
    status = Column(Enum('Pending', 'Paid', name='payment_status'), nullable=False)
    student = relationship("Student", backref="payments")

# Create FastAPI instance
app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Example endpoint to get all students
@app.get("/students/")
def read_students(db: Session = Depends(get_db)):
    return db.query(Student).all()

# Example endpoint to create a new student
@app.post("/students/")
def create_student(student: Student, db: Session = Depends(get_db)):
    db.add(student)
    db.commit()
    db.refresh(student)
    return student

# Create all tables
Base.metadata.create_all(bind=engine)