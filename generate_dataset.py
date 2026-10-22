import json
import random

tools_schema=[
    {
        "type":"function",
        "function":{
           "name":"search_route",
            "description":"Search available flights or trains between origin and destination codes. Returns schedule IDs, times, fares, and available seats.",
            "parameters":{
                "type":"object",
                "properties":{
                    "origin":{"type":"string" , "description":"few-letter uppercase origin code (e.g., 'DEL' for Delhi airport, 'NDLS' for New Delhi railway station, 'BLR')."},
                    "destination":{"type":"string","description":"few-letter uppercase destination code (e.g., 'BOM' for Mumbai airport, 'MMCT' for Mumbai Central station, 'TVC')."},
                    "mode":{"type":"string","enum":["TRAIN","FLIGHT"]}
                },
                "required":["origin","destination"]
            }
        }
    }
    ,
    {
        "type":"function",
        "function":{
            "name":"book_ticket",
            "description":"Book a confirmed seat on a schedule ID for a named passenger. Decrements inventory and outputs a confirmed PNR.",
            "parameters":{
                "type":"object",
                "properties":{
                "schedule_id":{"type":"integer","description":"the integer database id of the selected schedule."},
                "passenger_name":{"type":"string","description":"Full name of the passenger."},
                "passenger_age":{"type":"integer","description":"age of the passenger in years (2 to 90)."},
                "seats_required":{"type":"integer","description":"number of seats must be greater than or equal to one"}

            },
            "required":["schedule_id","passenger_name","passenger_age"]
        }

        }
    },
    {
        "type":"function",
        "function":{
            "name":"getpnr_status",
            "description":"Retrieve journey timings, passenger details, route, and current status for an existing PNR.",
            "parameters":{
                "type":"object",
                "properties":{
                    "pnr":{"type":"string","description":"The unique booking reference string (e.g., 'T4F8A1' or 10-digit numeric '4291847192')."}
                },
                "required":["pnr"]
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"canceltickets",
            "description":"Cancel an active booking using its PNR, restore seat inventory, and calculate tiered refund.",
            "parameters":{
                "type":"object",
                "properties":{
                    "pnr":{"type":"string","description":"The unique booking reference string to cancel (e.g., 'T4F8A1' or 10-digit numeric '4291847192')."}
                },
                "required":["pnr"]

            }
        }
    }
]

system_prompt=(
    "You are a helpful transport reservation assistant. You help users search routes, "
    "book travel tickets, inspect PNR statuses, and cancel existing bookings.\n"
    "# Tools\n"
    "You have access to the following tools:\n"
    f"{json.dumps(tools_schema, indent=2)}\n\n"
    "When calling a tool, respond with a JSON object within <tool_call></tool_call> tags:\n"
    "<tool_call>\n"
    '{"name": "<tool_name>", "arguments": <args_dict>}\n'
    "</tool_call>"

)



STATIONS = [
    ("Delhi", "DEL", "NDLS"),
    ("Mumbai", "BOM", "MMCT"),
    ("Bengaluru", "BLR", "SBC"),
    ("Chennai", "MAA", "MAS"),
    ("Hyderabad", "HYD", "SC"),
    ("Kolkata", "CCU", "HWH"),
    ("Thiruvananthapuram", "TRV", "TVC"),
    ("Ahmedabad", "AMD", "ADI"),
]

PASSENGERS = [
    "Aarav Sharma", "Priya Nair", "Rohan Mehta", "Ananya Iyer",
    "Vikram Patel", "Sneha Reddy", "Arjun Das", "Neha Verma",
    "Kavya Pillai", "Rahul Kapoor", "M S Srikar", "Deepak Gupta"
]

def make_flight_pnr():
    suffix = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=6))
    return suffix
def make_train_pnr():
    zone_digit = str(random.choice([2, 3, 4, 5, 6, 7, 8, 9]))
    remaining = "".join(random.choices("0123456789", k=9))
    return f"{zone_digit}{remaining}"
def make_any_pnr():
    return random.choice([make_flight_pnr, make_train_pnr])()

#creating a booking sample
def make_search_sample():
    origin_city, origin_air, origin_rail = random.choice(STATIONS)
    dest_opt = [s for s in STATIONS if s[0] != origin_city]
    dest_city, dest_air, dest_rail = random.choice(dest_opt)

    # Allow explicit mode or generalized queries
    requested_mode = random.choice(["FLIGHT", "TRAIN", None])

    if requested_mode == "TRAIN":
        mode = "TRAIN"
        o_code, d_code = origin_rail, dest_rail
        query = random.choice([
            f"Show me trains from {origin_city} to {dest_city}.",
            f"Any trains running between {origin_city} ({origin_rail}) and {dest_city} ({dest_rail})?",
            f"Check train options leaving {origin_city} station for {dest_city}."
        ])
    elif requested_mode == "FLIGHT":
        mode = "FLIGHT"
        o_code, d_code = origin_air, dest_air
        query = random.choice([
            f"Show me flights from {origin_city} to {dest_city}?",
            f"Search flights between {origin_city} and {dest_city}.",
            f"Check flight options from {origin_city} to {dest_city}."
        ])
    else:
        # General query: user doesn't specify mode upfront
        mode = random.choice(["FLIGHT", "TRAIN"])
        o_code = origin_rail if mode == "TRAIN" else origin_air
        d_code = dest_rail if mode == "TRAIN" else dest_air
        query = random.choice([
            f"How can I travel from {origin_city} to {dest_city}?",
            f"Check available routes from {origin_city} to {dest_city}.",
            f"Find travel options between {origin_city} and {dest_city}."
        ])

    call_args = {"origin": o_code, "destination": d_code, "mode": mode}

    # Generate synthetic attributes aligned with models.py & services.py
    sched_id = random.randint(101, 899)
    seats = random.randint(4, 52)
    departure_time = "2026-10-15 08:30:00"
    arrival_time = "2026-10-15 14:15:00"

    if mode == "TRAIN":
        identifier = f"{random.randint(12000, 22999)}"
        travel_class = random.choice(["SL", "3A", "2A", "1A"])
        base_fare = random.choice([650.0, 1150.0, 1750.0, 2450.0])
    else:
        carrier = random.choice(["6E", "AI", "UK", "QP"])
        identifier = f"{carrier}-{random.randint(100, 999)}"
        travel_class = random.choice(["Economy", "Premium Economy", "Business"])
        base_fare = random.choice([3200.0, 4800.0, 6500.0, 9200.0])

    # Exactly matches the return dict in services.py
    tool_response = [{
        "success":True,
        "id": sched_id,
        "mode": mode,
        "identifier": identifier,
        "origin": o_code,
        "destination": d_code,
        "departure_time": departure_time,
        "arrival_time": arrival_time,
        "travel_class": travel_class,
        "base_fare": base_fare,
        "available_seats": seats
    }]

    assistant_reply = (
        f"I found {mode.lower()} options from {o_code} to {d_code}. "
        f"{identifier} in {travel_class} class has {seats} seats available at ₹{base_fare:,.2f}, "
        f"departing at {departure_time} and arriving at {arrival_time}. "
        f"Would you like me to book it (Schedule ID: {sched_id})?"
    )

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query},
        {
            "role": "assistant",
            "content": f"<tool_call>\n{json.dumps({'name': 'search_route', 'arguments': call_args})}\n</tool_call>"
        },
        {"role": "tool", "name": "search_route", "content": json.dumps(tool_response)},
        {"role": "assistant", "content": assistant_reply}
    ]

def make_booking_sample():
    name = random.choice(PASSENGERS)
    age = random.randint(18, 70)
    sched_id = random.randint(101, 899)
    available_seats = random.randint(0, 15)  # Intentionally allow low/zero seat scenarios
    requested_seats = random.randint(1, 5)
    is_train = random.choice([True, False])
    pnr = make_train_pnr() if is_train else make_flight_pnr()
    mode = "TRAIN" if is_train else "FLIGHT"
    query=random.choice([
            f"Book {requested_seats} tickets at schedule ID {sched_id} for {name}, age {age}.",
            f"Please confirm {requested_seats} tickets on schedule {sched_id} under {name}, age {age}.",
            f"Reserve {requested_seats} seats on schedule {sched_id}. Passenger name is {name} and age is {age}."
        ])
    call_args=({
        "schedule_id":sched_id,
        "passenger_name":name,
        "passenger_age":age,
        "seats_required":requested_seats
    })
    if available_seats<requested_seats:
        tool_response={
            "success":False,
            "status":"FAILED",
            "message":"no seats are available",
            "available_seats":available_seats,
            "seats_required":requested_seats
        }

        assistant_reply=(
            f"ticket could not be booked because there are not enough tickets available."
            f"requested tickets-{requested_seats}"
            f"available tickets-{available_seats}"
        )

    else:
        if mode=="TRAIN":
            travel_class = random.choice(["SL", "3A", "2A", "1A"])
            fare = random.choice([650.0, 1150.0, 1750.0, 2450.0])

        else:
            travel_class= random.choice(["Economy","Premium Economy","Business"])
            fare=random.choice([3200.0, 4800.0, 6500.0, 9200.0])



        tool_response={
            "success":True,
            "pnr":pnr,
            "mode":mode,
            "passenger":name,
            "passenger_age":age,
            "total_fare":fare*requested_seats,
            "seats_required":requested_seats,
            "travel_class":travel_class,
            "status":"CONFIRMED"

        }

        assistant_reply=(
            f"you have successfully booked a ticket with pnr- {pnr} travelling by {mode}."
            f"Passenger name- {name} and passenger age- {age}."
            f"total fare- {fare*requested_seats}."
            f"travel_class- {travel_class}."
    )
    return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
            {
                "role": "assistant",
                "content": f"<tool_call>\n{json.dumps({'name': 'book_ticket', 'arguments': call_args})}\n</tool_call>"
            },
            {"role": "tool", "name": "book_ticket", "content": json.dumps(tool_response)},
            {"role": "assistant", "content": assistant_reply}
        ]

def search_pnr_sample():
    is_found=random.random()>0.15
    is_train=random.choice([True,False])
    pnr=make_train_pnr() if is_train else make_flight_pnr()

    query=random.choice([
        f"Check status for PNR {pnr}.",
        f"What is the status of my booking {pnr}?",
        f"Can you track PNR {pnr}?",
        f"Show journey details for booking reference {pnr}."
    ])

    call_args={"pnr":pnr}

    if is_found:
        name=random.choice(PASSENGERS)
        age=random.randint(2,90)
        status = random.choice(["CONFIRMED", "CANCELLED"])
        origin_city, origin_air, origin_rail = random.choice(STATIONS)
        dest_opt = [s for s in STATIONS if s[0] != origin_city]
        dest_city, dest_air, dest_rail = random.choice(dest_opt)

        if is_train:
            identifier = f"{random.randint(12000, 22999)}"
            route = f"{origin_rail} -> {dest_rail}"
        else:
            carrier = random.choice(["6E", "AI", "UK", "QP"])
            identifier = f"{carrier}-{random.randint(100, 999)}"
            route = f"{origin_air} -> {dest_air}"

        departure = "2026-10-16 10:30"
        refund_amount = 0.0

        tool_response = {
            "success": True,
            "pnr": pnr,
            "status": status,
            "passenger": name,
            "age": age,
            "identifier": identifier,
            "route": route,
            "departure": departure,
            "refund_amount": refund_amount
        }

        if status == "CONFIRMED":
            assistant_reply = (
                f"Booking {pnr} is CONFIRMED for {name} (Age: {age}). "
                f"Route: {route} on {identifier}, departing at {departure}."
            )
        elif status == "CANCELLED":
            assistant_reply = (
                f"Booking {pnr} is CANCELLED for {name}. "
                f"Route: {route} on {identifier}."
            )
    else:
        tool_response = {
            "success": False,
            "message": f"pnr-{pnr} not found"
        }
        assistant_reply = (
            f"No booking found for PNR {pnr}. Please check the reference number and try again."
        )

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query},
        {
            "role": "assistant",
            "content": f"<tool_call>\n{json.dumps({'name': 'getpnr_status', 'arguments': call_args})}\n</tool_call>"
        },
        {"role": "tool", "name": "getpnr_status", "content": json.dumps(tool_response)},
        {"role": "assistant", "content": assistant_reply}
    ]

def cancel_sample():
    is_found=random.random()>0.15
    status=random.choice(["CONFIRMED","CANCELLED"])
    is_train=random.choice([False,True])
    pnr=make_train_pnr() if is_train else make_flight_pnr()
    query = random.choice([
        f"Cancel my booking with PNR {pnr}.",
        f"Please cancel ticket {pnr}.",
        f"I want to cancel my reservation {pnr}."
    ])

    call_args={"pnr":pnr}
    if is_found:
        if status=="CANCELLED":
            tool_response={
                "success":False,
                "message":f"the booking has already been cancelled"
            }
            assistant_reply=(
                f"your ticket with pnr-{pnr} has already been cancelled"
            )
        else:
            total_fare=random.choice([1500.0,2234.0,830.0,6000.1])
            hours_to_departure=random.choice([24,12,4,1])
            if hours_to_departure==24:
                refund_rate = 0.90
                policy_note = "Cancelled >= 24hours prior: 90% refund."
            elif hours_to_departure==12:
                refund_rate = 0.50
                policy_note = "Cancelled between 12hours-24hours prior: 50% refund."
            elif hours_to_departure==4:
                refund_rate = 0.25
                policy_note ="Cancelled between 4hours-12hours prior: 25% refund."
            else:
                refund_rate=0
                policy_note="Cancelled < 4hours: 0% refund."
            tool_response={
                "success": True,
                "pnr": pnr,
                "status": "CANCELLED",
                "hours_before_departure": round(hours_to_departure, 1),
                "refund_rate": f"{int(refund_rate * 100)}%",
                "refund_amount": refund_rate*total_fare,
                "policy": policy_note,
                "message": "Booking cancelled successfully. Seat returned to inventory."
            }
            assistant_reply=(
                f"you ticket with pnr {pnr} has been successfully been cancelled"
                f"acording to the policy note ({policy_note} your refund rate is {refund_rate})"
                f"the amount you will recieve is {tool_response["refund_amount"]}"
                
            )
    else:
        tool_response = {
            "success": False,
            "message": f"there is no booking of this {pnr} found"
        }
        assistant_reply = (
            f"No booking found for PNR {pnr}. Please check the reference number and try again."
        )

    return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
            {
                "role": "assistant",
                "content": f"<tool_call>\n{json.dumps({'name': 'canceltickets', 'arguments': call_args})}\n</tool_call>"
            },
            {"role": "tool", "name": "canceltickets", "content": json.dumps(tool_response)},
            {"role": "assistant", "content": assistant_reply}
        ]

            










