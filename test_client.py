from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

NOT_FOUND = "No receipt found for that ID."
BAD_INPUT = "The receipt is invalid."

def test_process_receipt():
    response = client.post("/receipts/process", json={
        "retailer": "Target",
        "purchaseDate": "2024-02-07",
        "purchaseTime": "15:30",
        "total": "19.99",
        "items": [
            {"shortDescription": "Milk", "price": "3.99"},
            {"shortDescription": "Bread", "price": "16.00"}
        ]
    })
    
    assert response.status_code == 200  
    assert "id" in response.json()  


def test_get_receipt():
    response = client.post("/receipts/process", json={
        "retailer": "Target",
        "purchaseDate": "2024-02-07",
        "purchaseTime": "15:30",
        "total": "19.99",
        "items": [
            {"shortDescription": "Milk", "price": "3.99"},
            {"shortDescription": "Bread", "price": "16.00"}
        ]
    })
    
    assert response.status_code == 200  
    assert "id" in response.json()  

    receipt_id = response.json()["id"]
    
    response = client.get(f"/receipts/{receipt_id}/points")
    
    assert response.status_code == 200
    assert response.json()["points"] == 27


def test_invalid_id():
    response = client.get(f"/receipts/1111/points")
    assert response.status_code == 404
    assert response.json()["detail"]["description"] == NOT_FOUND


def test_malformed_receipts_wrong_date():
    response = client.post("/receipts/process", json={
        "retailer": "Target",
        "purchaseDate": "2024-13-07",
        "purchaseTime": "15:30",
        "total": "3.99",
        "items": [
            {"shortDescription": "Milk", "price": "3.99"},
        ]
    })
    
    assert response.status_code == 400
    assert response.json()["detail"]["description"] == BAD_INPUT


def test_malformed_receipts_wrong_time():
    response = client.post("/receipts/process", json={
        "retailer": "Target",
        "purchaseDate": "2024-11-07",
        "purchaseTime": "25:30",
        "total": "3.99",
        "items": [
            {"shortDescription": "Milk", "price": "3.99"},
        ]
    })
    
    assert response.status_code == 400
    assert response.json()["detail"]["description"] == BAD_INPUT

def test_malformed_receipts_wrong_total_price():
    response = client.post("/receipts/process", json={
        "retailer": "Target",
        "purchaseDate": "2024-13-07",
        "purchaseTime": "15:30",
        "total": "19.99",
        "items": [
            {"shortDescription": "Milk", "price": "3.99"},
            {"shortDescription": "Eggs", "price": "4.99"},
        ]
    })
    
    assert response.status_code == 400
    assert response.json()["detail"]["description"] == BAD_INPUT

def test_malformed_receipts_wrong_item_price():
    response = client.post("/receipts/process", json={
        "retailer": "Target",
        "purchaseDate": "2024-13-07",
        "purchaseTime": "15:30",
        "total": "15.339",
        "items": [
            {"shortDescription": "Eggs", "price": "15.339"},
        ]
    })
    
    assert response.status_code == 400
    assert response.json()["detail"]["description"] == BAD_INPUT

def test_malformed_receipts_missing_field():
    response = client.post("/receipts/process", json={
        "retailer": "Target",
        "purchaseTime": "15:30",
        "total": "15.339",
        "items": [
            {"shortDescription": "Eggs", "price": "15.339"},
        ]
    })
    
    assert response.status_code == 400
    assert response.json()["detail"]["description"] == BAD_INPUT
