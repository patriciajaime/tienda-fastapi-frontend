from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI(title="API de Tienda de Productos")

# Permitir comunicación con el servidor del Frontend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de datos
class Producto(BaseModel):
    id: int
    nombre: str
    precio: float

# Base de datos simulada en memoria
productos_db: List[Producto] = [
    Producto(id=1, nombre="Manzana", precio=15.5),
    Producto(id=2, nombre="Leche 1L", precio=26.0),
    Producto(id=3, nombre="Pan Integral", precio=38.0)
]

# 1. GET: Consultar productos
@app.get("/productos", response_model=List[Producto])
def obtener_productos():
    return productos_db

# 2. POST: Agregar nuevo producto
@app.post("/productos", response_model=Producto, status_code=201)
def agregar_producto(producto: Producto):
    for p in productos_db:
        if p.id == producto.id:
            raise HTTPException(status_code=400, detail="El ID del producto ya existe")
    productos_db.append(producto)
    return producto

# 3. DELETE: Eliminar producto por ID
@app.delete("/productos/{producto_id}")
def eliminar_producto(producto_id: int):
    for index, p in enumerate(productos_db):
        if p.id == producto_id:
            producto_eliminado = productos_db.pop(index)
            return {"mensaje": f"Producto '{producto_eliminado.nombre}' eliminado correctamente"}
    raise HTTPException(status_code=404, detail="Producto no encontrado")