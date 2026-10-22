from initsql import Session_local
import os
import uuid
from models import Schedule,Booking
from datetime import timedelta
import datetime
from dotenv import load_dotenv
import requests
import random

load_dotenv()

TRAVELPAYOUTS_TOKEN=os.getenv("TRAVEL_PAYOUTS_TOKEN", "")

AIRLINE_NAMES = {
    "6E": "IndiGo",
    "AI": "Air India",
    "IX": "Air India Express",
    "QP": "Akasa Air",
    "SG": "SpiceJet",
    "UK": "Vistara",
}

def search_routes(origin:str,destination:str,mode:str=None):
    db=Session_local()
    try:
        origin_code=origin.strip().upper()
        dest_code=destination.strip().upper()
        now=datetime.datetime.now()

        current_month = now.strftime("%Y-%m")
        next_month_date = (now.replace(day=1) + timedelta(days=32))
        next_month = next_month_date.strftime("%Y-%m")
        months_to_fetch = [current_month, next_month]
        if (mode is None or mode.upper() == "FLIGHT") and TRAVELPAYOUTS_TOKEN:
            for target_month in months_to_fetch:
                url = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates"
                headers = {"x-access-token": TRAVELPAYOUTS_TOKEN}
                params = {
                    "origin": origin_code,
                    "destination": dest_code,
                    "departure_at": target_month,
                    "currency": "INR",
                    "sorting": "price",
                    "limit": 5
                }
                res = requests.get(url, headers=headers, params=params, timeout=5)
                data = res.json()
                if data.get("success"):
                    for item in data.get("data",[]):
                        code = item.get("airline")
                        flight_num = item.get("flight_number")
                        raw_price = item.get("price")
                        dep_str = item.get("departure_at")
                        flight_minutes = item.get("duration") or item.get("duration_to")
                        


                        if not (code and flight_num and raw_price and dep_str and flight_minutes):
                            continue
                        dep_clean = dep_str.split("+")[0]
                        dep_time = datetime.datetime.fromisoformat(dep_clean)

                        if dep_time<now:
                            continue
                        arr_time = dep_time + timedelta(minutes=int(flight_minutes))
                        name = AIRLINE_NAMES.get(code,code)
                        ident = f"{code}-{flight_num} ({name})"
                        price = float(raw_price)

                        exists = db.query(Schedule).filter(
                        Schedule.identifier == ident,
                        Schedule.origin == origin_code,
                        Schedule.destination == dest_code,
                        Schedule.departure_time == dep_time
                        ).first()

                        if not exists:
                            db.add(Schedule(
                                mode="FLIGHT",
                                identifier=ident,
                                origin=origin_code,
                                destination=dest_code,
                                departure_time=dep_time,
                                arrival_time=arr_time,          # Exact arrival time calculated from API duration
                                travel_class="Economy",
                                base_fare=price,
                                available_seats=random.randint(15, 50)
                            ))
            db.commit()

        query=db.query(Schedule).filter(
            Schedule.origin==origin.upper(),
            Schedule.destination==destination.upper(),
            Schedule.available_seats>0
        )
        if mode:
            query=query.filter(
                Schedule.mode==mode.upper()
            )
        results=query.all()
        if not results:
            return{
                "success": False,
                "status": "FAILED",
                "message": f"route not found from {origin} to {destination} "
            }
        return [
            {
                "success":True,
               "id":s.id,
               "mode":s.mode,
               "identifier":s.identifier,
               "origin":s.origin,
               "destination":s.destination,
               "departure_time":s.departure_time,
               "arrival_time":s.arrival_time,
               "travel_class":s.travel_class,
               "base_fare":s.base_fare,
               "available_seats":s.available_seats

                
            } 
        for s in results]            
    finally:
        db.close()


def book_tickets(schedule_id:int,passenger_name:str,passenger_age:int,seats_required :int=1):
    db=Session_local()
    try:
        schedule=db.query(Schedule).filter(Schedule.id==schedule_id).first()
        if not schedule:
            return {
            "success": False,
            "status": "FAILED",
            "message": f"Schedule id {schedule_id} not found"
            }
        if schedule.available_seats-seats_required<0:
            return {"success":False,"status":"FAILED","message":"no seats are available","available_seats":schedule.available_seats,"seats_required":seats_required}
        schedule.available_seats-=seats_required

        if schedule.mode=="FLIGHT":
            pnr=f"{uuid.uuid4().hex[:6].upper()}"
        elif schedule.mode=="TRAIN":
            zone_digit=str(random.choice([2,3,4,5,6,7,8,9]))
            next_digits="".join(str(random.randint(0,9)) for _ in range(9))
            pnr=f"{zone_digit}{next_digits}"


        new_booking=Booking(
            pnr=pnr,
            mode=schedule.mode,
            schedule_id=schedule.id,
            passenger_name=passenger_name,
            passenger_age=passenger_age,
            seats_required=seats_required,
            travel_class=schedule.travel_class,
            total_fare=schedule.base_fare*seats_required,
            status="CONFIRMED"
        )
        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)

        return {
            "success":True,
            "pnr": new_booking.pnr,
            "mode": new_booking.mode,
            "passenger": new_booking.passenger_name,
            "passenger_age":new_booking.passenger_age,
            "total_fare": new_booking.total_fare,
            "seats_required":seats_required,
            "travel_class": new_booking.travel_class,
            "status": new_booking.status
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"Transaction failed: {str(e)}"}
    finally:
        db.close()


def pnr_status(pnr:str):
    db=Session_local()
    try:
        booking=db.query(Booking).filter(Booking.pnr==pnr.upper()).first()
        if not booking:
            return {"success":False,"message":f"pnr-{pnr} not found"}

        return {
            "success":True,
            "pnr":pnr,
            "status":booking.status,
            "passenger": booking.passenger_name,
            "age": booking.passenger_age,
            "identifier": booking.schedule.identifier,
            "route": f"{booking.schedule.origin} -> {booking.schedule.destination}",
            "departure": booking.schedule.departure_time.strftime("%Y-%m-%d %H:%M"),
            "refund_amount": booking.refund_amount
        }
    finally:
        db.close()

def cancel_tickets(pnr:str):
    db=Session_local()
    try:
        booking=db.query(Booking).filter(Booking.pnr==pnr.upper()).first()
        if not booking:
            return {"success":False,"message":f"there is no booking of this {pnr} found"}
        if booking.status=="CANCELLED":
            return {"success":False,"message":f"the booking has already been cancelled"}
        booking.status="CANCELLED"
        now=datetime.datetime.now()
        departure_time=booking.schedule.departure_time
        time_diff=departure_time-now
        hours_to_departure=time_diff.total_seconds()/3600.0
        if hours_to_departure >= 24:
            refund_rate = 0.90
            policy_note = "Cancelled >= 24h prior: 90% refund."
        elif hours_to_departure >= 12 :
            refund_rate = 0.50
            policy_note = "Cancelled between 12h-24h prior: 50% refund."
        elif hours_to_departure >= 4:
            refund_rate = 0.25
            policy_note = "Cancelled between 4h-12h prior: 25% refund."
        else:
            refund_rate = 0.00
            policy_note = "Cancelled < 4h prior or after departure: Non-refundable."
        refund_ammount=round(booking.total_fare*refund_rate,2)
        booking.refund_amount=refund_ammount
        schedule=db.query(Schedule).filter(Schedule.id==booking.schedule_id).first()
        if schedule:
            schedule.available_seats+=booking.seats_required
            db.commit()
            return {
            "success": True,
            "pnr": booking.pnr,
            "status": booking.status,
            "hours_before_departure": round(hours_to_departure, 1),
            "refund_rate": f"{int(refund_rate * 100)}%",
            "refund_amount": booking.refund_amount,
            "policy": policy_note,
            "message": "Booking cancelled successfully. Seat returned to inventory."
        }
        else:
            return {"success": False, "status": "FAILED", "message": "Associated schedule not found"}
    except Exception as e:
        db.rollback()
        return {"success":False,"message":f"Cancellation failed {str(e)}"}
    finally:
        db.close()


        