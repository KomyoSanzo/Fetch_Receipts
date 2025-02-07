from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, time, date
from typing import List, Dict
import uuid, math

app = FastAPI()

receipts: Dict[str, float] = {}

class Item(BaseModel):
    shortDescription: str
    price: float

class Receipt(BaseModel):
    retailer: str
    purchaseDate: date
    purchaseTime: time
    total: float
    items: List[Item]

class GetPointsResponse(BaseModel):
    points : float

class ProcessReceiptsResponse(BaseModel):
    receipt_id : uuid.UUID
    points : float

def calculate_points (receipt: Receipt):
    retailer = receipt.retailer
    purchase_date = receipt.purchaseDate
    purchase_time = receipt.purchaseTime
    total = receipt.total
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
            points += math.ceil(item.price * 0.2)

    # Rule 6 is funny
    # Rule 7
    if purchase_date.day % 2 == 1:
        points += 6
    
    # Rule 8
    if time(14, 0, 0) < purchase_time < time(16, 0, 0): # Note: I am interpreting the ruling as non-inclusive of the boundary hours
        points += 10
    
    return points

@app.get("/receipts/{receipt_id}/points", response_model=GetPointsResponse)
def get_points(receipt_id: str):
    converted_id = uuid.UUID(receipt_id)
    if converted_id not in receipts:
        raise HTTPException(status_code=404, detail=f"Receipt with id {receipt_id} does not exist.")
    points: int = receipts[converted_id]
    return {"points" : points}

@app.post("/receipts/process", response_model=ProcessReceiptsResponse)
def process_receipts(receipt: Receipt):
    new_uuid = uuid.uuid4()
    points = calculate_points(receipt)
    receipts[new_uuid] = points
    return {"receipt_id" : new_uuid, "points" : points}


