from typing import Optional
from sqlmodel import SQLModel, Field
class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    venue: str
    capacity: int
    organizer: str
    status: str
class Reservation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: int
    student_name: str
    roll_number: str
    email: str