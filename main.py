from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from uuid import uuid4
import hashlib

app = FastAPI()

# In-memory databases
users_db = {}
products_db = {}

# Models
class RegisterUser(BaseModel):
    username: str
    password: str

class LoginUser(BaseModel):
    username: str
    password: str

class Product(BaseModel):
    id: str
    name: str
    price: float
    description: str

# Helpers
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Routes

@app.post("/register")
def register(user: RegisterUser):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    users_db[user.username] = hash_password(user.password)
    return {"message": "User registered successfully"}

@app.post("/login")
def login(user: LoginUser):
    hashed = users_db.get(user.username)
    if not hashed or hashed != hash_password(user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful"}

@app.get("/products", response_model=List[Product])
def get_products():
    return list(products_db.values())

@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: str):
    product = products_db.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Add sample products on startup
@app.on_event("startup")
def startup_data():
    p1 = Product(id=str(uuid4()), name="Phone", price=29999.99, description="Smartphone with 6GB RAM")
    p2 = Product(id=str(uuid4()), name="Laptop", price=59999.99, description="14-inch laptop with SSD")
    products_db[p1.id] = p1
    products_db[p2.id] = p2
