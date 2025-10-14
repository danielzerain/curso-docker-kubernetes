from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import json
from decimal import Decimal

app = FastAPI(title="Tienda Hardware API - Carrito Compra")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de la base de datos
import os

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": int(os.getenv("DB_PORT"))
}



CACHE_TTL = 300

class ItemCarrito(BaseModel):
    producto_id: int
    cantidad: int

class CarritoCreate(BaseModel):
    cliente_nombre: str
    cliente_email: str
    items: List[ItemCarrito]

class PedidoResponse(BaseModel):
    success: bool
    message: str
    pedido_id: Optional[int] = None
    total: Optional[float] = None


@contextmanager
def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()

@app.get("/")
def root():
    return {"mensaje": "API Tienda de Hardware de Computación - Carrito de Compra"}

@app.get("/cart/health")
def root():
    return {"estado": "OK"}    


@app.post("/cart/pedidos", response_model=PedidoResponse, status_code=201)
def crear_pedido(carrito: CarritoCreate):
    """Crea un nuevo pedido con los items del carrito"""
    try:
        # Validaciones básicas
        if not carrito.items:
            raise HTTPException(status_code=400, detail="El carrito está vacío")
        
        if not carrito.cliente_nombre.strip():
            raise HTTPException(status_code=400, detail="El nombre del cliente es requerido")
        
        if not carrito.cliente_email.strip():
            raise HTTPException(status_code=400, detail="El email del cliente es requerido")
        
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Iniciar transacción
                total_pedido = Decimal('0.00')
                items_detalle = []
                
                # Validar productos y calcular total
                for item in carrito.items:
                    if item.cantidad <= 0:
                        raise HTTPException(
                            status_code=400, 
                            detail=f"La cantidad debe ser mayor a 0"
                        )
                    
                    # Obtener información del producto
                    cur.execute(
                        "SELECT id, nombre, precio, stock FROM productos WHERE id = %s",
                        (item.producto_id,)
                    )
                    producto = cur.fetchone()
                    
                    if not producto:
                        raise HTTPException(
                            status_code=404, 
                            detail=f"Producto con ID {item.producto_id} no encontrado"
                        )
                    
                    if producto['stock'] < item.cantidad:
                        raise HTTPException(
                            status_code=400, 
                            detail=f"Stock insuficiente para {producto['nombre']}. Disponible: {producto['stock']}"
                        )
                    
                    # Convertir precio a Decimal si no lo es
                    precio = Decimal(str(producto['precio']))
                    subtotal = precio * item.cantidad
                    total_pedido += subtotal
                    
                    items_detalle.append({
                        'producto_id': item.producto_id,
                        'nombre': producto['nombre'],
                        'cantidad': item.cantidad,
                        'precio_unitario': precio,
                        'subtotal': subtotal
                    })
                
                # Crear el pedido
                cur.execute(
                    """
                    INSERT INTO pedidos (cliente_nombre, cliente_email, total, estado, fecha)
                    VALUES (%s, %s, %s, %s, NOW())
                    RETURNING id
                    """,
                    (
                        carrito.cliente_nombre.strip(),
                        carrito.cliente_email.strip(),
                        total_pedido,
                        'pendiente'
                    )
                )
                
                pedido_id = cur.fetchone()['id']
                
                # Insertar los items del pedido y actualizar stock
                for item_det in items_detalle:
                    # Insertar item
                    cur.execute(
                        """
                        INSERT INTO pedido_items (pedido_id, producto_id, cantidad, precio_unitario, subtotal)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            pedido_id,
                            item_det['producto_id'],
                            item_det['cantidad'],
                            item_det['precio_unitario'],
                            item_det['subtotal']
                        )
                    )
                    
                    # Actualizar stock
                    cur.execute(
                        """
                        UPDATE productos 
                        SET stock = stock - %s 
                        WHERE id = %s
                        """,
                        (item_det['cantidad'], item_det['producto_id'])
                    )
                
                conn.commit()
                
                print(f"✓ Pedido creado con ID: {pedido_id}, Total: Bs.{float(total_pedido):.2f}")
                
                
                return PedidoResponse(
                    success=True,
                    message="Pedido creado exitosamente",
                    pedido_id=pedido_id,
                    total=float(total_pedido)
                )
                
    except HTTPException:
        raise
    except psycopg2.Error as e:
        print(f"Error de base de datos: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error al crear el pedido: {str(e)}"
        )
    except Exception as e:
        print(f"Error inesperado: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error inesperado al crear el pedido: {str(e)}"
        )

@app.get("/cart/pedidos/{pedido_id}")
def obtener_pedido(pedido_id: int):
    """Obtiene los detalles de un pedido específico"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Obtener información del pedido
                cur.execute(
                    """
                    SELECT id, cliente_nombre, cliente_email, total, estado, fecha
                    FROM pedidos
                    WHERE id = %s
                    """,
                    (pedido_id,)
                )
                
                pedido = cur.fetchone()
                
                if not pedido:
                    raise HTTPException(
                        status_code=404, 
                        detail=f"Pedido con ID {pedido_id} no encontrado"
                    )
                
                # Obtener items del pedido
                cur.execute(
                    """
                    SELECT 
                        pi.producto_id,
                        p.nombre as producto_nombre,
                        pi.cantidad,
                        pi.precio_unitario,
                        pi.subtotal
                    FROM pedido_items pi
                    JOIN productos p ON pi.producto_id = p.id
                    WHERE pi.pedido_id = %s
                    """,
                    (pedido_id,)
                )
                
                items = cur.fetchall()
                
                return {
                    "pedido": pedido,
                    "items": items
                }
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al obtener el pedido: {str(e)}"
        )

@app.get("/cart/pedidos")
def listar_pedidos(limite: int = 50):
    """Lista los últimos pedidos"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT id, cliente_nombre, cliente_email, total, estado, fecha
                    FROM pedidos
                    ORDER BY fecha DESC
                    LIMIT %s
                    """,
                    (limite,)
                )
                
                pedidos = cur.fetchall()
                return {"pedidos": pedidos}
                
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al listar pedidos: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)