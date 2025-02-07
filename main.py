from decimal import Decimal
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime, time, date
from typing import List, Dict
import uuid, math
import re

app = FastAPI(
    title="Receipt Processor",
    description="A simple receipt processor",
    version="1.0.0"
)

receipts: Dict[str, int] = {}

#####
#SCHEMAS
#####
class Item(BaseModel):
    shortDescription: str
    price: str

class Receipt(BaseModel):
    retailer: str
    purchaseDate: str
    purchaseTime: str
    total: str
    items: List[Item]

class GetPointsResponse(BaseModel):
    points : int

class ProcessReceiptsResponse(BaseModel):
    id : str

class BadRequestResponse (BaseModel):
    description : str = "The receipt is invalid."

class NotFoundResponse (BaseModel):
    description : str = "No receipt found for that ID."



@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exception):
    raise HTTPException(
        status_code=400,
        detail = "The receipt is invalid"
    )


#####
#VALIDATORS
#####
def validate_price(price: str):
    if not re.fullmatch("^\\d+\\.\\d{2}$", price):
        raise HTTPException(status_code=400)


def validate_alphanum(s: str):
    if not re.fullmatch("^[\\w\\s\\-&]+$", s):
        raise HTTPException(status_code=400)

def validate_receipt(receipt: Receipt):
    try:
        datetime.strptime(receipt.purchaseDate, "%Y-%m-%d").date()
        datetime.strptime(receipt.purchaseTime, "%H:%M").time()

        retailer = receipt.retailer
        validate_alphanum(retailer)
        
        total = receipt.total
        validate_price(total)
        
        items = receipt.items
        running_total = Decimal(0.0)
        for item in items:
            item_desc = item.shortDescription
            item_price = item.price
            validate_alphanum(item_desc)
            validate_price(item_price)

            running_total += Decimal(item_price)
        
        if running_total != Decimal(total):
            raise HTTPException(status_code=400)
    except:
        raise HTTPException(status_code=400)

#####
# BUSINESS LOGIC
#####

def calculate_points (receipt: Receipt):
    validate_receipt(receipt)
    
    retailer = receipt.retailer
    purchase_date = datetime.strptime(receipt.purchaseDate, "%Y-%m-%d").date()
    purchase_time = datetime.strptime(receipt.purchaseTime, "%H:%M").time()
    total = float(receipt.total)
    items = receipt.items
    points = 0
    
    # Calculate rule 1: alphanumeric in name
    for c in retailer:
        if c.isalnum():
            points += 1

    # Calculate rules 2 and 3
    if total.is_integer():
        points += 50
    if total % 0.25 == 0:
        points += 25
    
    # Rule 4
    points += 5 * (len(items) // 2)

    # Rule 5
    for item in items:
        desc = item.shortDescription.strip()
        if len(desc) % 3 == 0:
            points += math.ceil(float(item.price) * 0.2)

    # Rule 6 is funny
    # Rule 7
    if purchase_date.day % 2 == 1:
        points += 6
    
    # Rule 8
    if time(14, 0, 0) < purchase_time < time(16, 0, 0): # Note: I am interpreting the ruling as non-inclusive of the boundary hours
        points += 10
    
    return points


#####
# END POINTS
#####
@app.get("/receipts/{receipt_id}/points", response_model=GetPointsResponse, responses = {404: {"model" : NotFoundResponse}})
def get_points(receipt_id: str):
    try:
        converted_id = uuid.UUID(receipt_id)
        points: int = receipts[converted_id]
    except:
        raise HTTPException(status_code=404, detail={"description" : "No receipt found for that ID."})
    
    return GetPointsResponse(points = points)

@app.post("/receipts/process", response_model=ProcessReceiptsResponse, responses = {400: {"model" : BadRequestResponse}})
def process_receipts(receipt: Receipt):
    new_uuid = uuid.uuid4()
    try:
        points = calculate_points(receipt)
    except:
        raise HTTPException(status_code = 400, detail={"description" : "The receipt is invalid."})
    
    receipts[new_uuid] = points
    return ProcessReceiptsResponse(id = str(new_uuid))

