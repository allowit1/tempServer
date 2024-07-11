import os
import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Dict, List

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# File paths
DATA_FILE = "data.json"

# Load data from JSON file on startup
grocery_list = {}
next_item_id = 1
item_name_to_id = {}


class ItemPayload(BaseModel):
    item_id: int
    item_name: str
    quantity: int

@app.on_event("startup")
def load_data():
    global next_item_id
    global item_nameg_to_id
    global grocery_list
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            grocery_list = json.load(file)
            print(grocery_list)
            next_item_id = max(map(int, grocery_list.keys())) + 1 if grocery_list else 1
            item_name_to_id = {item["item_name"]: int(item_id) for item_id, item in grocery_list.items()}
            print(item_name_to_id)

@app.on_event("shutdown")
def save_data():
    with open(DATA_FILE, "w") as file:
        json.dump(grocery_list, file)

@app.get("/")
def home(request: Request):
    return RedirectResponse(url="/static/index.html")

@app.post("/items/{item_name}/{quantity}")
def add_item(item_name: str, quantity: int) -> Dict[str, ItemPayload]:
    global next_item_id

    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0.")

    item_id = item_name_to_id.get(item_name)

    if item_id is not None:
        grocery_list[str(item_id)]['quantity'] += quantity
    else:
        item_id = next_item_id
        next_item_id += 1
        grocery_list[str(item_id)] = {"item_name": item_name, "quantity": quantity}
        item_name_to_id[item_name] = item_id

    item = grocery_list[str(item_id)]
    return {
        "item": ItemPayload(item_id=item_id, item_name=item["item_name"], quantity=item["quantity"])
    }

@app.get("/items/{item_id}")
def list_item(item_id: int) -> Dict[str, Dict[str, str]]:
    item_id = str(item_id)
    if item_id not in grocery_list:
        raise HTTPException(status_code=404, detail="Item not found.")
    return {"item": grocery_list[item_id]}

@app.get("/items")
def list_items() -> Dict[str, List[ItemPayload]]:
    items: List[ItemPayload] = [
        ItemPayload(item_id=int(item_id), item_name=item["item_name"], quantity=item["quantity"])
        for item_id, item in grocery_list.items()
    ]
    return {"items": items}

@app.delete("/items/{item_id}")
def delete_item(item_id: int) -> Dict[str, str]:
    item_id = str(item_id)
    if item_id not in grocery_list:
        raise HTTPException(status_code=404, detail="Item not found.")
    
    item_name = grocery_list[item_id]["item_name"]
    del grocery_list[item_id]
    print(item_name_to_id)
    return {"result": "Item deleted."}

@app.delete("/items/{item_id}/{quantity}")
def remove_quantity(item_id: int, quantity: int) -> Dict[str, str]:
    item_id = str(item_id)
    if item_id not in grocery_list:
        raise HTTPException(status_code=404, detail="Item not found.")

    existing_quantity = grocery_list[item_id]["quantity"]

    if existing_quantity <= quantity:
        item_name = grocery_list[item_id]["item_name"]
        del grocery_list[item_id]
        del item_name_to_id[item_name]
        return {"result": "Item deleted."}
    else:
        grocery_list[item_id]["quantity"] -= quantity
        return {"result": f"{quantity} items removed."}
