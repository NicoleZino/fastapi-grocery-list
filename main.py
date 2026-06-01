from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from models import GroceryItem, GroceryItemDetails
import json
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

DATA_FILE = "grocery_data.json"
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
    return templates.TemplateResponse("index.html", {"request": request, "items": items})

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
    items = load_items()
    items.append(new_item.model_dump(mode="json")) # Convert Pydantic model to dict
    save_items(items) 
    return RedirectResponse("/", status_code=303)

@app.post("/delete/{item_id}")
def delete_item(item_id: str):
    items = load_items()
    items = [item for item in items if item["id"] != item_id]
    save_items(items)
    return RedirectResponse("/", status_code=303)

@app.get("/edit/{item_id}", response_class=HTMLResponse)
def edit_item(request: Request, item_id: str):
    items = load_items()
    for item in items:
        if item["id"] == item_id:
            return templates.TemplateResponse("edit.html", {"request": request, "item": item})
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
        if item["id"] == item_id:
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