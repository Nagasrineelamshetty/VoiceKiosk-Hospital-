from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

# ---------- Doctor ----------
class Doctor(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str  # e.g., "Dr. Kiran Kumar"
    specialization: str  # e.g., "Cardiology"
    department: str  # e.g., "Cardiology"
    room_number: Optional[str]  # e.g., "Room 203"
    floor: Optional[str]  # e.g., "First Floor"
    directions: Optional[str]  # e.g., "Go straight, take right, third door on your left"
    experience: Optional[int]  # years
    phone: Optional[str]
    email: Optional[EmailStr]
    visiting_hours_ids: Optional[List[str]] = []  # link to visiting hours

# ---------- Department ----------
class Department(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str  # e.g., "Cardiology"
    description: Optional[str]  # overview of department
    head_of_department: Optional[str]  # doctor name
    location: Optional[str]  # e.g., "First floor, Wing A"
    directions: Optional[str]  # e.g., "Take elevator to first floor, turn left"

# ---------- Service ----------
class Service(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str  # e.g., "ECG"
    description: Optional[str]
    department: Optional[str]  # link to department
    price: Optional[float]

# ---------- Visiting Hour ----------
class VisitingHour(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    doctor_name: str  # link to doctor
    day: str  # e.g., "Monday"
    start_time: str  # e.g., "09:00 AM"
    end_time: str  # e.g., "12:00 PM"

# ---------- Emergency Contact ----------
class EmergencyContact(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str  # e.g., "Security"
    phone: str
    department: Optional[str]  # if department specific
    available_24x7: bool = True

# ---------- FAQ ----------
class FAQ(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    question: str  # patient query text
    answer: str  # pre-formatted text answer

# ---------- Hospital Info ----------
class HospitalInfo(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str  # e.g., "General Hospital"
    address: str
    opening_hours: str  # e.g., "08:00 AM - 08:00 PM"
    mass_timings: Optional[str]  # e.g., "10:00 AM, 5:00 PM"
    general_instructions: Optional[str]  # e.g., parking info, cafeteria, etc.
