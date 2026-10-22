import models
from initsql import engine,Base

def init_table():
    print("create tables in Mysql if they are not present")
    Base.metadata.create_all(bind=engine)
    print("tables of schedule and bookings created succesfully")

if __name__=="__main__":
    init_table()

