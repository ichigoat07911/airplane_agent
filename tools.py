from pydantic import Field,BaseModel
from typing import Literal,Optional
import json
from langchain_core.tools import tool

from services import search_routes,book_tickets,cancel_tickets,pnr_status

class Searchroutesinput(BaseModel):
    origin: str=Field(
        ...,
        description="few letter uppercase origin code (e.g., 'DEL' for Delhi airport, 'NDLS' for New Delhi railway station, 'BLR')."
    )
    destination: str=Field(
        ...,
        description="few letter uppercase destination code (e.g., 'BOM' for Mumbai airport, 'MMCT' for Mumbai Central station, 'TVC')."
    )
    mode:Optional[Literal["FLIGHT","TRAIN"]] = Field(
        default=None,
        description="Optional filter for travel mode: must be uppercase 'FLIGHT' or 'TRAIN'. Omit if not specified."
    )

class BookticketsInput(BaseModel):
    schedule_id:int=Field(
            ...,
            description="The integer database ID of the selected schedule from search results."
        )
    passenger_name:str=Field(
            ...,
            min_length=2,
            description="Full name of the passenger."
        )
    passenger_age:int=Field(
        ...,
        ge=2,
        le=90,
        description="Age of the person (must be at between 2 and 90)."
    )
    seats_required:int=Field(
        default=1,
        ge=1,
        description="Number of seats to reserve (must be at least 1)."
    )

class getpnrInput(BaseModel):
    pnr:str=Field(
        ...,
        description="The unique booking reference string (e.g., 'T4F8A1' or 10-digit numeric '4291847192')."

        )

class cancelticketInput(BaseModel):
    pnr:str=Field(
        ...,
        description="The unique booking reference string (e.g., 'T4F8A1' or 10-digit numeric '4291847192')."
        )

@tool(args_schema=Searchroutesinput)
def search_route(origin:str,destination:str,mode:Optional[str]=None):
    """Search available flights or trains between origin and destination codes. Returns schedule IDs, times, fares, and available seats."""
    result=search_routes(origin=origin.upper(),destination=destination.upper(),mode=mode)
    return json.dumps(result,default=str)

@tool(args_schema=BookticketsInput)
def book_ticket(schedule_id:int,passenger_name:str,passenger_age:int,seats_required: int=1):
    """Book a confirmed seat on a schedule ID for a named passenger. Decrements inventory and outputs a confirmed PNR."""
    result=book_tickets(schedule_id=schedule_id,passenger_name=passenger_name.strip(),passenger_age=passenger_age,seats_required=seats_required)
    return json.dumps(result,default=str)

    
@tool(args_schema=getpnrInput)
def getpnr_status(pnr:str):
    """Retrieve journey timings, passenger details, route, and current status for an existing PNR."""
    result=pnr_status(pnr=pnr.strip().upper())
    return json.dumps(result,default=str)

@tool(args_schema=cancelticketInput)
def canceltickets(pnr:str):
    """Cancel an active booking using its PNR, restore seat inventory, and calculate tiered refund."""
    result = cancel_tickets(pnr=pnr.strip().upper())
    return json.dumps(result, default=str)
