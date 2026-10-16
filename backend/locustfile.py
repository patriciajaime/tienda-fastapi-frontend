"""
==============================================================================
MÓDULO DE PRUEBAS DE CARGA Y ESTRÉS CON LOCUST
==============================================================================
Descripción:
    Script de simulación de tráfico HTTP concurrente para evaluar el rendimiento
    y validar el comportamiento del Middleware de Rate Limiting en la API.

Asignatura:   Programación IV
Profesor:     Diego Alberto Ayala Vázquez
Autora:       Patricia Jaime
Fecha:        15 de Octubre de 2026
==============================================================================
"""


from locust import HttpUser, task, between

class UsuarioTienda(HttpUser):
    """
    Clase que simula el comportamiento de un cliente en la tienda virtual.
    Genera tráfico HTTP concurrente contra el backend para validar
    el funcionamiento del middleware de Rate Limiting.
    """

    # Pausa entre 0.1 y 0.5 segundos entre peticiones para simular un tráfico rápido
    wait_time = between(0.1, 0.5)

    @task(3)
    def consultar_productos(self):
        """
        Simula el registro de un nuevo producto (Petición POST).
        Tiene un peso relativo de 1 para ejecutarse ocasionalmente.
        """
        self.client.get("/productos")

    @task(1)
    def agregar_producto_prueba(self):
        """Prueba de escritura enviando peticiones POST a /productos"""
        self.client.post("/productos", json={
            "id": 999,
            "nombre": "Producto Test",
            "precio": 10.0
        })