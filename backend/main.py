from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# Inicialización de la aplicación FastAPI
app = FastAPI(title="API de Tienda de Productos - Asíncrona")

# Configuración de Middleware CORS para permitir solicitudes del Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de datos con Pydantic para validación automática
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

# ==============================================================================
# ACTIVIDAD 2.1: CONVERSIÓN DE ENDPOINTS A FUNCIONES ASÍNCRONAS (async def)
# Nota: Se declara 'async def' para que FastAPI maneje las peticiones en el event loop.
# No se utiliza 'await' internamente porque 'productos_db' es una lista en memoria 
# y no requiere operaciones I/O no bloqueantes (como consultas a BD externas).
# ==============================================================================

# 1. Endpoint GET: Consultar todos los productos (Asíncrono)
@app.get("/productos", response_model=List[Producto])
async def obtener_productos():
    """
    Retorna la lista completa de productos.
    Función asíncrona que maneja peticiones GET.
    """
    return productos_db


# 2. Endpoint POST: Agregar un nuevo producto (Asíncrono)
@app.post("/productos", response_model=Producto, status_code=201)
async def agregar_producto(producto: Producto):
    """
    Recibe un objeto JSON validado por Pydantic y lo agrega a la base de datos.
    Verifica que el ID sea único antes de agregarlo.
    """
    for p in productos_db:
        if p.id == producto.id:
            raise HTTPException(status_code=400, detail="El ID del producto ya existe")
    
    productos_db.append(producto)
    return producto


# 3. Endpoint DELETE: Eliminar un producto por ID (Asíncrono)
@app.delete("/productos/{producto_id}")
async def eliminar_producto(producto_id: int):
    """
    Busca un producto por su ID y lo elimina de la lista.
    Si no lo encuentra, lanza un error 404.
    """
    for index, p in enumerate(productos_db):
        if p.id == producto_id:
            producto_eliminado = productos_db.pop(index)
            return {"mensaje": f"Producto '{producto_eliminado.nombre}' eliminado correctamente"}
    
    raise HTTPException(status_code=404, detail="Producto no encontrado")