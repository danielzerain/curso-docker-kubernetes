from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import redis
import json

app = FastAPI(title="Tienda Hardware API - Productos")

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

# Configuración de Redis con manejo de errores
try:
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        db=0,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5
    )
    # Verificar conexión
    redis_client.ping()
    print("✓ Conectado a Redis exitosamente")
except redis.RedisError as e:
    print(f"✗ No se pudo conectar a Redis: {e}")
    redis_client = None

CACHE_TTL = 300

@contextmanager
def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()

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

class ProductoCreate(BaseModel):
    nombre: str
    categoria: str
    precio: float
    stock: int
    marca: str
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None

class ProductoResponse(BaseModel):
    success: bool
    message: str
    producto_id: Optional[int] = None

def get_productos_from_db(categoria: Optional[str] = None):
    """Obtiene productos de la base de datos"""
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

# Endpoints
@app.get("/")
def root():
    return {"mensaje": "API Tienda de Hardware de Computación"}

@app.get("/api/productos", response_model=List[ProductoResumen])
def listar_productos(categoria: Optional[str] = None):
    """Lista todos los productos o filtra por categoría con cache Redis"""
    try:
        cache_key = f"productos:{'all' if not categoria else f'categoria:{categoria}'}"

        if redis_client:
            try:
                cached_data = redis_client.get(cache_key)
                
                if cached_data:
                    print(f"✓ Cache HIT para: {cache_key}")
                    return json.loads(cached_data)
                
                print(f"✗ Cache MISS para: {cache_key}")
            except redis.RedisError as e:
                print(f"Error al leer de Redis: {e}")
        
        productos = get_productos_from_db(categoria)
        if redis_client:
            try:
                redis_client.setex(
                    cache_key,
                    CACHE_TTL,
                    json.dumps(productos, default=str)
                )
                print(f"✓ Datos guardados en cache: {cache_key}")
            except redis.RedisError as e:
                print(f"Error al guardar en Redis: {e}")
        
        return productos
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener productos: {str(e)}")

@app.get("/api/categorias")
def listar_categorias():
    """Lista todas las categorías disponibles"""
    try:
        cache_key = "categorias:all"
        
        # Intentar obtener del cache
        if redis_client:
            try:
                cached_data = redis_client.get(cache_key)
                if cached_data:
                    print(f"✓ Cache HIT para categorías")
                    return json.loads(cached_data)
            except redis.RedisError as e:
                print(f"Error al leer categorías de Redis: {e}")
        
        # Consultar base de datos
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT DISTINCT categoria FROM productos ORDER BY categoria")
                categorias = [row['categoria'] for row in cur.fetchall()]
                resultado = {"categorias": categorias}
                
                # Guardar en cache
                if redis_client:
                    try:
                        redis_client.setex(cache_key, CACHE_TTL, json.dumps(resultado))
                        print(f"✓ Categorías guardadas en cache")
                    except redis.RedisError as e:
                        print(f"Error al guardar categorías en Redis: {e}")
                
                return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener categorías: {str(e)}")

def invalidar_cache_productos(categoria: Optional[str] = None):
    """Invalida el caché de productos"""
    if not redis_client:
        return
    
    try:
        if categoria:
            # Invalidar solo la categoría específica
            redis_client.delete(f"productos:categoria:{categoria}")
            redis_client.delete("productos:all")  # También invalidar la lista completa
            print(f"✓ Cache invalidado para categoría: {categoria}")
        else:
            # Invalidar todos los cachés de productos
            keys = redis_client.keys("productos:*")
            if keys:
                redis_client.delete(*keys)
            redis_client.delete("categorias:all")  # También invalidar categorías
            print(f"✓ Cache invalidado completamente ({len(keys)} claves)")
    except redis.RedisError as e:
        print(f"Error al invalidar caché: {str(e)}")

@app.get("/api/redis/status")
def redis_status():
    """Verifica el estado de la conexión a Redis"""
    if not redis_client:
        return {"status": "disconnected", "message": "Redis no está configurado"}
    
    try:
        redis_client.ping()
        info = redis_client.info()
        return {
            "status": "connected",
            "redis_version": info.get("redis_version"),
            "used_memory_human": info.get("used_memory_human"),
            "connected_clients": info.get("connected_clients")
        }
    except redis.RedisError as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/redis/clear")
def clear_cache():
    """Limpia todo el cache de Redis"""
    if not redis_client:
        raise HTTPException(status_code=503, detail="Redis no está disponible")
    
    try:
        invalidar_cache_productos()
        return {"message": "Cache limpiado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al limpiar cache: {str(e)}")

@app.post("/api/productos", response_model=ProductoResponse, status_code=201)
def registrar_producto(producto: ProductoCreate):
    """Registra un nuevo producto en la base de datos"""
    try:
        # Validar datos
        if producto.precio <= 0:
            raise HTTPException(status_code=400, detail="El precio debe ser mayor a 0")
        
        if producto.stock < 0:
            raise HTTPException(status_code=400, detail="El stock no puede ser negativo")
        
        if not producto.nombre.strip():
            raise HTTPException(status_code=400, detail="El nombre del producto es requerido")
        
        # Insertar producto en la base de datos
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Verificar si ya existe un producto con el mismo nombre
                cur.execute(
                    "SELECT id FROM productos WHERE LOWER(nombre) = LOWER(%s)",
                    (producto.nombre.strip(),)
                )
                if cur.fetchone():
                    raise HTTPException(
                        status_code=409, 
                        detail=f"Ya existe un producto con el nombre '{producto.nombre}'"
                    )
                
                # Insertar el nuevo producto
                cur.execute(
                    """
                    INSERT INTO productos (nombre, categoria, precio, stock, marca, descripcion, imagen_url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        producto.nombre.strip(),
                        producto.categoria.strip(),
                        producto.precio,
                        producto.stock,
                        producto.marca.strip(),
                        producto.descripcion.strip() if producto.descripcion else None,
                        producto.imagen_url
                    )
                )
                
                nuevo_id = cur.fetchone()['id']
                conn.commit()
                
                print(f"✓ Producto registrado con ID: {nuevo_id}")
                
                # Invalidar cache después de crear el producto
                invalidar_cache_productos(producto.categoria)
                
                return ProductoResponse(
                    success=True,
                    message="Producto registrado exitosamente",
                    producto_id=nuevo_id
                )
                
    except HTTPException:
        raise
    except psycopg2.Error as e:
        print(f"Error de base de datos: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error al registrar el producto en la base de datos: {str(e)}"
        )
    except Exception as e:
        print(f"Error inesperado: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error inesperado al registrar el producto: {str(e)}"
        )

@app.get("/api/productos/{producto_id}", response_model=Producto)
def obtener_producto(producto_id: int):
    """Obtiene un producto específico por su ID"""
    try:
        cache_key = f"producto:{producto_id}"
        
        # Intentar obtener del cache
        if redis_client:
            try:
                cached_data = redis_client.get(cache_key)
                if cached_data:
                    print(f"✓ Cache HIT para producto ID: {producto_id}")
                    return json.loads(cached_data)
            except redis.RedisError as e:
                print(f"Error al leer de Redis: {e}")
        
        # Consultar base de datos
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT id, nombre, categoria, precio, stock, marca, descripcion, imagen_url 
                    FROM productos 
                    WHERE id = %s
                    """,
                    (producto_id,)
                )
                
                producto = cur.fetchone()
                
                if not producto:
                    raise HTTPException(
                        status_code=404, 
                        detail=f"Producto con ID {producto_id} no encontrado"
                    )
                
                # Guardar en cache
                if redis_client:
                    try:
                        redis_client.setex(cache_key, CACHE_TTL, json.dumps(producto, default=str))
                        print(f"✓ Producto ID {producto_id} guardado en cache")
                    except redis.RedisError as e:
                        print(f"Error al guardar en Redis: {e}")
                
                return producto
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al obtener el producto: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)