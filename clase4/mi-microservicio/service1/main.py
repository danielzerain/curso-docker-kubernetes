from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import redis
import json

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

redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True 
)

CACHE_TTL = 300

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

    try:
            # Crear una clave única para el caché
            cache_key = f"productos:{'all' if not categoria else f'categoria:{categoria}'}"
            
            # Intentar obtener datos del caché
            cached_data = redis_client.get(cache_key)
            
            if cached_data:
                # Si hay datos en caché, devolverlos
                print(f"Cache HIT para: {cache_key}")
                return json.loads(cached_data)
            
            # Si no hay caché, consultar la base de datos
            print(f"Cache MISS para: {cache_key}")
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
                    
                    # Guardar en caché
                    redis_client.setex(
                        cache_key,
                        CACHE_TTL,
                        json.dumps(productos, default=str)  # default=str para serializar tipos especiales
                    )
                    
                    return productos
                    
    except redis.RedisError as e:
        # Si Redis falla, continuar sin caché
        print(f"Error de Redis: {str(e)}")
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if categoria:
                    cur.execute(
                        "SELECT id, nombre, categoria, precio, stock, marca FROM productos WHERE categoria = %s ORDER BY nombre",
                        (categoria,)
                    )
                else:
                    cur.execute("SELECT id, nombre, categoria, precio, stock, marca FROM productos ORDER BY nombre")
                
                return cur.fetchall()
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener productos: {str(e)}")

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
    

def invalidar_cache_productos(categoria: Optional[str] = None):
    """Invalida el caché de productos"""
    try:
        if categoria:
            # Invalidar solo la categoría específica
            redis_client.delete(f"productos:categoria:{categoria}")
        else:
            # Invalidar todos los cachés de productos
            keys = redis_client.keys("productos:*")
            if keys:
                redis_client.delete(*keys)
    except redis.RedisError as e:
        print(f"Error al invalidar caché: {str(e)}")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)