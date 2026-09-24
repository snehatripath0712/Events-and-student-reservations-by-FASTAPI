from typing import Literal
from pydantic import BaseModel, EmailStr, Field
class EventCreate(BaseModel):
    title: str = Field(min_length=1)
    venue: str = Field(min_length=1)
    capacity: int = Field(gt=0)
    organizer: str = Field(min_length=1)
    status: Literal["Open", "Closed"]
class EventUpdate(BaseModel):
    title: str = Field(min_length=1)
    venue: str = Field(min_length=1)
    capacity: int = Field(gt=0)
    organizer: str = Field(min_length=1)
    status: Literal["Open", "Closed"]
class ReservationCreate(BaseModel):
    student_name: str = Field(min_length=1)
    roll_number: str = Field(min_length=1)
    email: EmailStr