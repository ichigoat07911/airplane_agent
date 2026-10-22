import datetime
from sqlalchemy import Column,String,Integer,ForeignKey,Float,DateTime,Enum,CheckConstraint
from sqlalchemy.orm import relationship
from initsql import Base

class Schedule(Base):
    __tablename__="schedules"
    id=Column(Integer,primary_key=True,index=True,autoincrement=True)
    mode=Column(Enum("TRAIN","FLIGHT",name="Transport_mode"),nullable=False)
    identifier=Column(String(50),nullable=False)
    origin=Column(String(10),nullable=False,index=True)
    destination=Column(String(10),nullable=False,index=True)
    departure_time=Column(DateTime,nullable=False)
    arrival_time=Column(DateTime,nullable=False)
    travel_class=Column(String(20),nullable=False)
    base_fare=Column(Float,nullable=False)
    available_seats=Column(Integer,nullable=False)


class Booking(Base):
    __tablename__="bookings"
    id=Column(Integer,primary_key=True,index=True,autoincrement=True)
    pnr=Column(String(20),nullable=False,unique=True)
    mode=Column(Enum("TRAIN","FLIGHT",name="Transport_mode"),nullable=False)
    schedule_id = Column(Integer, ForeignKey("schedules.id"), nullable=False)
    passenger_name=Column(String(30),nullable=False)
    passenger_age=Column(Integer,nullable=False)
    seats_required=Column(Integer,default=1,nullable=False)
    refund_amount=Column(Float,default=0.0,nullable=False)
    total_fare=Column(Float,nullable=False)
    travel_class=Column(String(20),nullable=False)
    status=Column(Enum("CONFIRMED","CANCELLED","FAILED",name="booking_status"),default="CONFIRMED",nullable=False)
    schedule=relationship("Schedule")
    __table_args__=(
        CheckConstraint("seats_required > 0",name="chk_seats_required_positive"),
        CheckConstraint("passenger_age > 0", name="chk_passenger_age_positive"),
        CheckConstraint("total_fare >= 0", name="chk_total_fare_non_negative"),
    )


