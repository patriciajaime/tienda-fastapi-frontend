"""
Módulo principal de la API de Tienda de Productos.
Implementa arquitectura asíncrona en FastAPI, Middleware CORS, 
gestión de datos con Pydantic y control de tasa de peticiones (Rate Limiting) 
utilizando el paquete nativo 'asyncio' y marcas de tiempo.

Autora: Patricia Jaime
Asignatura: Programación IV
Profesor: Diego Alberto Ayala Vázquez
"""

import time
import asyncio
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# ==============================================================================
# INICIALIZACIÓN Y CONFIGURACIÓN DE LA APLICACIÓN
# ==============================================================================

app = FastAPI(
    title="API de Tienda de Productos - Asíncrona con Rate Limiting",
    description="Backend desarrollado en FastAPI con soporte para peticiones asíncronas y Middleware de Rate Limiting.",
    version="2.0.0"
)

# Configuración de Middleware CORS para permitir comunicación segura con el cliente Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================================
# CONFIGURACIÓN DEL MIDDLEWARE DE RATE LIMITING (Límite de Peticiones)
# ==============================================================================

# Estructura de datos para almacenar el historial de marcas de tiempo (timestamps) de las peticiones
peticiones_historial: List[float] = []

# Cerrojo asíncrono (Lock) para garantizar un acceso seguro en entornos de concurrencia
rate_limit_lock = asyncio.Lock()

# Constantes de configuración (Buenas prácticas: Evitar valores numéricos mágicos en el código)
LIMITE_MAXIMO_PETICIONES: int = 5
VENTANA_TIEMPO_SEGUNDOS: float = 1.0


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next) -> Response:
    """
    Middleware HTTP que intercepta cada solicitud entrante para limitar 
    el tráfico a un máximo de 5 peticiones por segundo por cliente.
    
    Aplica concurrencia segura mediante 'asyncio.Lock' y limpia automáticamente 
    las peticiones fuera de la ventana de tiempo.
    """
    tiempo_actual: float = time.time()

    async with rate_limit_lock:
        global peticiones_historial

        # 1. Filtrar y conservar únicamente las peticiones dentro del último segundo
        peticiones_historial = [
            t for t in peticiones_historial 
            if (tiempo_actual - t) < VENTANA_TIEMPO_SEGUNDOS
        ]

        # 2. Validar si se superó el límite permitido (5 peticiones por segundo)
        if len(peticiones_historial) >= LIMITE_MAXIMO_PETICIONES:
            return Response(
                content='{"detail": "Demasiadas peticiones. Límite máximo de 5 peticiones por segundo alcanzado."}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json"
            )

        # 3. Registrar el timestamp de la petición actual
        peticiones_historial.append(tiempo_actual)

    # 4. Continuar con el procesamiento normal de la petición
    response: Response = await call_next(request)
    return response


# ==============================================================================
# MODELO DE DATOS Y ESTRUCTURA DE MEMORIA
# ==============================================================================

class Producto(BaseModel):
    """
    Modelo de datos Pydantic para la validación y serialización de productos.
    """
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
# ENDPOINTS ASÍNCRONOS DE LA API (GET, POST, DELETE)
# ==============================================================================

@app.get("/productos", response_model=List[Producto], status_code=status.HTTP_200_OK)
async def obtener_productos() -> List[Producto]:
    """
    Endpoint GET Asíncrono: Retorna la lista completa de productos.
    """
    return productos_db


@app.post("/productos", response_model=Producto, status_code=status.HTTP_201_CREATED)
async def agregar_producto(producto: Producto) -> Producto:
    """
    Endpoint POST Asíncrono: Agrega un nuevo producto a la base de datos simulada.
    Verifica que el ID sea único antes de insertar.
    """
    for p in productos_db:
        if p.id == producto.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="El ID del producto ya existe."
            )
    
    productos_db.append(producto)
    return producto


@app.delete("/productos/{producto_id}", status_code=status.HTTP_200_OK)
async def eliminar_producto(producto_id: int) -> Dict[str, str]:
    """
    Endpoint DELETE Asíncrono: Elimina un producto especificando su ID único.
    """
    for index, p in enumerate(productos_db):
        if p.id == producto_id:
            producto_eliminado = productos_db.pop(index)
            return {"mensaje": f"Producto '{producto_eliminado.nombre}' eliminado correctamente."}
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail="Producto no encontrado."
    )