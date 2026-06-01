from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from models import GroceryItem, GroceryItemDetails
import json
import os
import uuid  # <-- Added to generate unique IDs for your items

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# FIX 1: Use an absolute directory path so Render can safely read and write your JSON file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "grocery_data.json")

def load_items():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_items(items):
    with open(DATA_FILE, "w") as f:
        json.dump(items, f, indent=4)

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    items = load_items()
    # Pass 'request' first, then the HTML filename, then your context data
    return templates.TemplateResponse(
        request, 
        "index.html", 
        {"items": items}
    )

@app.post("/add")
def add_item(
    name: str = Form(...),
    category: str = Form(...),
    price_per_gram: float = Form(...),
    weight_grams: float = Form(...),
    organic: bool = Form(False),
    availability: str = Form("In stock")
):
    new_item = GroceryItem(
        name=name,
        category=category,
        price_per_gram=price_per_gram,
        details=GroceryItemDetails(
            weight_grams=weight_grams,
            organic=organic,
            availability=availability
        )
    )
    
    # Convert Pydantic model to a python dictionary
    item_dict = new_item.model_dump(mode="json")
    
    # FIX 2: Ensure every added item gets a unique 'id' key if your Pydantic model doesn't supply one
    if "id" not in item_dict or not item_dict["id"]:
        item_dict["id"] = str(uuid.uuid4())
        
    items = load_items()
    items.append(item_dict) 
    save_items(items) 
    return RedirectResponse("/", status_code=303)

@app.post("/delete/{item_id}")
def delete_item(item_id: str):
    items = load_items()
    # Using .get() prevents the application from crashing if an ID is missing
    items = [item for item in items if item.get("id") != item_id]
    save_items(items)
    return RedirectResponse("/", status_code=303)

@app.get("/edit/{item_id}", response_class=HTMLResponse)
def edit_item(request: Request, item_id: str):
    items = load_items()
    for item in items:
        if item.get("id") == item_id:
            # Pass 'request' first, then the HTML filename, then your item data
            return templates.TemplateResponse(
                request, 
                "edit.html", 
                {"item": item}
            )
    raise HTTPException(status_code=404, detail="Item not found")


@app.post("/update/{item_id}")
def update_item(
    item_id: str,
    name: str = Form(...),
    category: str = Form(...),
    price_per_gram: float = Form(...),
    weight_grams: float = Form(...),
    organic: bool = Form(False),
    availability: str = Form(...)
):
    items = load_items()
    for i, item in enumerate(items):
        if item.get("id") == item_id:
            items[i]["name"] = name
            items[i]["category"] = category
            items[i]["price_per_gram"] = price_per_gram
            items[i]["details"]["weight_grams"] = weight_grams
            items[i]["details"]["organic"] = organic
            items[i]["details"]["availability"] = availability
            break
    else:
        raise HTTPException(status_code=404, detail="Item not found")

    save_items(items)
    return RedirectResponse("/", status_code=303)
