from fastapi import FastAPI, HTTPException


app = FastAPI()

receipts = {}


@app.get("/receipts/{receipt_id}/points")
def get_points(receipt_id):
    pass

@app.post("/receipts/process")
def process_receipts(receipt):
    pass
