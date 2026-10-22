from datetime import datetime, timedelta
from initsql import Session_local
from models import Schedule

def seed_database():
    db = Session_local()
    try:
        # Check if records already exist so we don't duplicate rows
        existing_count = db.query(Schedule).count()
        if existing_count > 0:
            print(f"Database already contains {existing_count} schedules. Skipping seeding.")
            return

        print("Seeding flight and train schedules into MySQL...")

        # Base departure time set to tomorrow morning at 06:00 AM
        base_time = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0) + timedelta(days=1)

        schedules = [
            # ----------------- FLIGHTS -----------------
            # Delhi (DEL) -> Mumbai (BOM)
            Schedule(
                mode="FLIGHT",
                identifier="6E-2044 (IndiGo)",
                origin="DEL",
                destination="BOM",
                departure_time=base_time + timedelta(hours=2),           # 08:00
                arrival_time=base_time + timedelta(hours=4, minutes=15),    # 10:15
                travel_class="ECONOMY",
                base_fare=4500.0,
                available_seats=45
            ),
            Schedule(
                mode="FLIGHT",
                identifier="AI-805 (Air India)",
                origin="DEL",
                destination="BOM",
                departure_time=base_time + timedelta(hours=8),           # 14:00
                arrival_time=base_time + timedelta(hours=10, minutes=20),   # 16:20
                travel_class="BUSINESS",
                base_fare=12500.0,
                available_seats=12
            ),
            # Bangalore (BLR) -> Delhi (DEL)
            Schedule(
                mode="FLIGHT",
                identifier="QP-1302 (Akasa Air)",
                origin="BLR",
                destination="DEL",
                departure_time=base_time + timedelta(hours=5),           # 11:00
                arrival_time=base_time + timedelta(hours=7, minutes=50),    # 13:50
                travel_class="ECONOMY",
                base_fare=5200.0,
                available_seats=30
            ),

            # ----------------- TRAINS -----------------
            # New Delhi (NDLS) -> Mumbai Central (MMCT)
            Schedule(
                mode="TRAIN",
                identifier="12952 Mumbai Rajdhani",
                origin="NDLS",
                destination="MMCT",
                departure_time=base_time + timedelta(hours=10, minutes=55), # 16:55
                arrival_time=base_time + timedelta(days=1, hours=2, minutes=35), # 08:35 next day
                travel_class="3A",
                base_fare=2150.0,
                available_seats=20
            ),
            Schedule(
                mode="TRAIN",
                identifier="12952 Mumbai Rajdhani",
                origin="NDLS",
                destination="MMCT",
                departure_time=base_time + timedelta(hours=10, minutes=55),
                arrival_time=base_time + timedelta(days=1, hours=2, minutes=35),
                travel_class="2A",
                base_fare=3050.0,
                available_seats=8
            ),
            # New Delhi (NDLS) -> Thiruvananthapuram (TVC)
            Schedule(
                mode="TRAIN",
                identifier="12626 Kerala Express",
                origin="NDLS",
                destination="TVC",
                departure_time=base_time + timedelta(hours=14, minutes=10), # 20:10
                arrival_time=base_time + timedelta(days=2, hours=18),       # 42 hours later
                travel_class="SL",
                base_fare=890.0,
                available_seats=60
            ),
            Schedule(
                mode="TRAIN",
                identifier="12626 Kerala Express",
                origin="NDLS",
                destination="TVC",
                departure_time=base_time + timedelta(hours=14, minutes=10),
                arrival_time=base_time + timedelta(days=2, hours=18),
                travel_class="3A",
                base_fare=2340.0,
                available_seats=25
            ),
            #0 available seats
            Schedule(
                mode="FLIGHT",
                identifier="AI-506 (Air India)",
                origin="DEL",
                destination="BOM",
                departure_time=base_time + timedelta(hours=14),
                arrival_time=base_time + timedelta(hours=16, minutes=15),
                travel_class="ECONOMY",
                base_fare=4200.0,
                available_seats=0  
            ),

            # 6hrs 25%refund
            Schedule(
                mode="FLIGHT",
                identifier="6E-5512 (IndiGo)",
                origin="DEL",
                destination="BLR",
                departure_time=datetime.now() + timedelta(hours=6),
                arrival_time=datetime.now() + timedelta(hours=8, minutes=45),
                travel_class="ECONOMY",
                base_fare=5800.0,
                available_seats=15
            ),

            # 2 hrs
            Schedule(
                mode="TRAIN",
                identifier="12004 Shatabdi Express",
                origin="NDLS",
                destination="LKO",
                departure_time=datetime.now() + timedelta(hours=2),
                arrival_time=datetime.now() + timedelta(hours=8),
                travel_class="CC",
                base_fare=1165.0,
                available_seats=10
            )
        ]

        # Bulk insert into MySQL
        db.add_all(schedules)
        db.commit()
        print(f" Successfully inserted {len(schedules)} schedules into MySQL!")

    except Exception as e:
        db.rollback()
        print(f" Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()