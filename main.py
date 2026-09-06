import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Literal

app = FastAPI()


def require_admin(x_admin_key: str | None = Header(default=None)):
    admin_key = os.getenv("ADMIN_KEY")
    if not admin_key or x_admin_key != admin_key:
        raise HTTPException(status_code=401, detail="Admin access required")


class Complaint(BaseModel):
    title: str
    description: str
    category: str


class ComplaintStatusUpdate(BaseModel):
    status: Literal["pending", "in_progress", "resolved"]


class OrderItem(BaseModel):
    food_id: int
    quantity: int


class OrderCreate(BaseModel):
    customer_name: str
    items: list[OrderItem]
    payment_method: Literal["pay_at_counter", "upi_demo"]


class OrderStatusUpdate(BaseModel):
    status: Literal["placed", "preparing", "ready", "completed"]


@app.post("/complaints")
def create_complaint(complaint: Complaint):
    response = supabase.table("complaints").insert(
        complaint.model_dump()
    ).execute()

    return {
        "message": "Complaint saved successfully",
        "complaint": response.data[0]
    }


@app.get("/complaints", dependencies=[Depends(require_admin)])
def get_complaints():
    response = (
        supabase.table("complaints")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return response.data


@app.patch("/complaints/{complaint_id}/status", dependencies=[Depends(require_admin)])
def update_complaint_status(
    complaint_id: int, update: ComplaintStatusUpdate
):
    response = (
        supabase.table("complaints")
        .update({"status": update.status})
        .eq("id", complaint_id)
        .execute()
    )

    if not response.data:
        raise HTTPException(status_code=404, detail="Complaint not found")

    return {
        "message": "Complaint status updated successfully",
        "complaint": response.data[0]
    }


@app.get("/")
def home():
    return {
        "message": "Canteen Complaint API is running!",
        "status": "success"
    }

@app.get("/foods")
def get_foods():
    response = supabase.table("foods").select("*").execute()
    return response.data


@app.post("/orders")
def create_order(order: OrderCreate):
    if not order.items or not order.customer_name.strip():
        raise HTTPException(status_code=400, detail="Name and cart items are required")

    foods_response = supabase.table("foods").select("*").execute()
    foods = {food["id"]: food for food in foods_response.data}
    order_items = []
    total = 0.0

    for item in order.items:
        food = foods.get(item.food_id)
        if not food or not food["available"] or item.quantity < 1:
            raise HTTPException(status_code=400, detail="One or more food items are unavailable")
        price = float(food["price"])
        total += price * item.quantity
        order_items.append({
            "food_id": food["id"],
            "name": food["name"],
            "price": price,
            "quantity": item.quantity
        })

    response = supabase.table("orders").insert({
        "customer_name": order.customer_name.strip(),
        "items": order_items,
        "total": total,
        "payment_method": order.payment_method
    }).execute()

    return {"message": "Order placed successfully", "order": response.data[0]}


@app.get("/orders", dependencies=[Depends(require_admin)])
def get_orders():
    response = (
        supabase.table("orders")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return response.data


@app.patch("/orders/{order_id}/status", dependencies=[Depends(require_admin)])
def update_order_status(order_id: int, update: OrderStatusUpdate):
    response = (
        supabase.table("orders")
        .update({"status": update.status})
        .eq("id", order_id)
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order status updated successfully", "order": response.data[0]}


app.mount("/app", StaticFiles(directory="static", html=True), name="app")
