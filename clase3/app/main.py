from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

app = FastAPI(title="Tienda Hardware API")

# Configurar CORS
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
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "tienda_hardware"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres123"),
    "port": int(os.getenv("DB_PORT", "5432"))
}

@contextmanager
def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()

# Modelos Pydantic
class Producto(BaseModel):
    id: int
    nombre: str
    categoria: str
    precio: float
    stock: int
    marca: str
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None

class ProductoResumen(BaseModel):
    id: int
    nombre: str
    categoria: str
    precio: float
    stock: int
    marca: str

# Endpoints
@app.get("/")
def root():
    return {"mensaje": "API Tienda de Hardware de Computación"}

@app.get("/api/productos", response_model=List[ProductoResumen])
def listar_productos(categoria: Optional[str] = None):
    """Lista todos los productos o filtra por categoría"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if categoria:
                    cur.execute(
                        "SELECT id, nombre, categoria, precio, stock, marca FROM productos WHERE categoria = %s ORDER BY nombre",
                        (categoria,)
                    )
                else:
                    cur.execute("SELECT id, nombre, categoria, precio, stock, marca FROM productos ORDER BY nombre")
                
                productos = cur.fetchall()
                return productos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener productos: {str(e)}")

@app.get("/api/productos/{producto_id}", response_model=Producto)
def obtener_producto(producto_id: int):
    """Obtiene el detalle completo de un producto específico"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM productos WHERE id = %s",
                    (producto_id,)
                )
                producto = cur.fetchone()
                
                if not producto:
                    raise HTTPException(status_code=404, detail="Producto no encontrado")
                
                return producto
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener producto: {str(e)}")

@app.get("/api/categorias")
def listar_categorias():
    """Lista todas las categorías disponibles"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT DISTINCT categoria FROM productos ORDER BY categoria")
                categorias = [row['categoria'] for row in cur.fetchall()]
                return {"categorias": categorias}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener categorías: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)