from fastapi import FastAPI, Path, Query, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

app = FastAPI(
    title="Marketplace de Productos Agrícolas API",
    description="API RESTful para E-Commerce y Retail de productos agrícolas",
    version="1.0.0"
)

# ==============================
# RUTA RAÍZ (PARA QUE NO SALGA NOT FOUND)
# ==============================

@app.get("/")
def root():
    return {"message": "Marketplace Agrícola funcionando correctamente 🚜🌱"}


# ==============================
# MODELOS
# ==============================

class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    stock: int
    category: str
    origin: str
    created_at: datetime


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: str
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    category: str
    origin: str


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    category: Optional[str] = None
    origin: Optional[str] = None


# ==============================
# BASE DE DATOS SIMULADA
# ==============================

products: List[Product] = []


# ==============================
# CREAR PRODUCTO
# ==============================

@app.post("/products", response_model=Product)
def create_product(product: ProductCreate):
    new_product = Product(
        id=len(products) + 1,
        created_at=datetime.now(),
        **product.model_dump()
    )
    products.append(new_product)
    return new_product


# ==============================
# OBTENER PRODUCTOS (FILTROS + PAGINACIÓN + ORDENAMIENTO)
# ==============================

@app.get("/products", response_model=List[Product])
def get_products(
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    category: Optional[str] = None,
    origin: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = Query("price"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
):
    result = products

    # FILTRADO
    if min_price is not None:
        result = [p for p in result if p.price >= min_price]

    if max_price is not None:
        result = [p for p in result if p.price <= max_price]

    if category:
        result = [p for p in result if p.category.lower() == category.lower()]

    if origin:
        result = [p for p in result if p.origin.lower() == origin.lower()]

    if search:
        result = [p for p in result if search.lower() in p.name.lower()]

    # ORDENAMIENTO
    if sort_by == "price":
        result.sort(key=lambda x: x.price)
    elif sort_by == "name":
        result.sort(key=lambda x: x.name)

    # PAGINACIÓN
    return result[skip: skip + limit]


# ==============================
# OBTENER PRODUCTO POR ID
# ==============================

@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int = Path(..., ge=1)):
    for product in products:
        if product.id == product_id:
            return product

    raise HTTPException(status_code=404, detail="Producto no encontrado")


# ==============================
# ACTUALIZAR PRODUCTO
# ==============================

@app.put("/products/{product_id}", response_model=Product)
def update_product(
    product_id: int = Path(..., ge=1),
    product_data: ProductUpdate = ...
):
    for product in products:
        if product.id == product_id:
            update_data = product_data.model_dump(exclude_unset=True)

            for key, value in update_data.items():
                setattr(product, key, value)

            return product

    raise HTTPException(status_code=404, detail="Producto no encontrado")


# ==============================
# ELIMINAR PRODUCTO
# ==============================

@app.delete("/products/{product_id}")
def delete_product(product_id: int = Path(..., ge=1)):
    for product in products:
        if product.id == product_id:
            products.remove(product)
            return {"message": "Producto eliminado correctamente"}

    raise HTTPException(status_code=404, detail="Producto no encontrado")


# ==============================
# UPLOAD IMAGEN
# ==============================

@app.post("/products/{product_id}/upload-image")
def upload_image(
    product_id: int = Path(..., ge=1),
    file: UploadFile = File(...)
):
    return {
        "product_id": product_id,
        "filename": file.filename,
        "message": "Imagen subida correctamente"
    }