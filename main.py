from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List

app = FastAPI()

receipts = {}

class Item(BaseModel):
    shortDescription: str
    price: float

class Receipt(BaseModel):
    retailer: str
    purchaseDate: datetime.date
    purchaseTime: datetime.time
    total: float
    items: List[Item]


@app.get("/receipts/{receipt_id}/points")
def get_points(receipt_id: str):
    if receipt_id not in receipts:
        raise HTTPException(status_code=404, detail=f"Receipt with id {receipt_id} does not exist.")
    return {"points" : receipts[receipt_id]}

@app.post("/receipts/process")
def process_receipts(receipt: Receipt):
    pass
