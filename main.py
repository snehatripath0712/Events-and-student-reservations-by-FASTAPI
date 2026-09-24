from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from models import Event, Reservation
from schemas import EventCreate, EventUpdate, ReservationCreate
from database import get_session
router = APIRouter()
@router.post(
    "/events",
    response_model=Event,
    status_code=status.HTTP_201_CREATED
)
def create_event(
    event: EventCreate,
    session: Session = Depends(get_session)
):
    new_event = Event(**event.model_dump())
    session.add(new_event)
    session.commit()
    session.refresh(new_event)
    return new_event
@router.get("/events", response_model=list[Event])
def get_events(
    session: Session = Depends(get_session)
):
    events = session.exec(
        select(Event)
    ).all()
    return events
@router.get("/events/{event_id}", response_model=Event)
def get_event(
    event_id: int,
    session: Session = Depends(get_session)
):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )
    return event
@router.put("/events/{event_id}", response_model=Event)
def update_event(
    event_id: int,
    updated_event: EventUpdate,
    session: Session = Depends(get_session)
):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )
    booked = session.exec(
        select(Reservation).where(
            Reservation.event_id == event_id
        )
    ).all()
    if updated_event.capacity < len(booked):
        raise HTTPException(
            status_code=400,
            detail="Capacity cannot be less than current bookings"
        )
    event.title = updated_event.title
    event.venue = updated_event.venue
    event.capacity = updated_event.capacity
    event.organizer = updated_event.organizer
    event.status = updated_event.status
    session.add(event)
    session.commit()
    session.refresh(event)
    return event
@router.delete("/events/{event_id}")
def delete_event(
    event_id: int,
    session: Session = Depends(get_session)
):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )
    reservations = session.exec(
        select(Reservation).where(
            Reservation.event_id == event_id
        )
    ).all()

    for reservation in reservations:
        session.delete(reservation)

    session.delete(event)
    session.commit()

    return {
        "message": "Event deleted successfully"
    }
@router.post(
    "/events/{event_id}/reserve",
    response_model=Reservation,
    status_code=status.HTTP_201_CREATED
)
def create_reservation(
    event_id: int,
    reservation: ReservationCreate,
    session: Session = Depends(get_session)
):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )
    if event.status != "Open":
        raise HTTPException(
            status_code=400,
            detail="Reservations are closed for this event"
        )
    existing_reservations = session.exec(
        select(Reservation).where(
            Reservation.event_id == event_id
        )
    ).all()
    booked = len(existing_reservations)
    if booked >= event.capacity:
        raise HTTPException(
            status_code=400,
            detail="Event is already full"
        )
    new_reservation = Reservation(
        event_id=event_id,
        **reservation.model_dump()
    )
    session.add(new_reservation)
    session.commit()
    session.refresh(new_reservation)
    return new_reservation
@router.get(
    "/events/{event_id}/reservations",
    response_model=list[Reservation]
)
def get_reservations(
    event_id: int,
    session: Session = Depends(get_session)
):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )
    reservations = session.exec(
        select(Reservation).where(
            Reservation.event_id == event_id
        )
    ).all()
    return reservations
@router.delete("/reservations/{reservation_id}")
def delete_reservation(
    reservation_id: int,
    session: Session = Depends(get_session)
):
    reservation = session.get(
        Reservation,
        reservation_id
    )
    if not reservation:
        raise HTTPException(
            status_code=404,
            detail="Reservation not found"
        )
    session.delete(reservation)
    session.commit()
    return {
        "message": "Reservation cancelled successfully"
    }
@router.get("/events/{event_id}/availability")
def get_availability(
    event_id: int,
    session: Session = Depends(get_session)
):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )
    reservations = session.exec(
        select(Reservation).where(
            Reservation.event_id == event_id
        )
    ).all()
    booked = len(reservations)
    remaining = event.capacity - booked
    return {
        "capacity": event.capacity,
        "booked": booked,
        "remaining": remaining
    }