-- Crear base de datos
--CREATE DATABASE tienda_hardware;

-- Conectar a la base de datos
\c tienda_hardware;

-- Crear tabla de productos
CREATE TABLE IF NOT EXISTS productos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    marca VARCHAR(100) NOT NULL,
    descripcion TEXT,
    imagen_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear tabla de pedidos
CREATE TABLE IF NOT EXISTS pedidos (
    id SERIAL PRIMARY KEY,
    cliente_nombre VARCHAR(255) NOT NULL,
    cliente_email VARCHAR(255) NOT NULL,
    total DECIMAL(10, 2) NOT NULL,
    estado VARCHAR(50) DEFAULT 'pendiente',
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pedido_items (
    id SERIAL PRIMARY KEY,
    pedido_id INTEGER NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE,
    producto_id INTEGER NOT NULL REFERENCES productos(id),
    cantidad INTEGER NOT NULL,
    precio_unitario DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL
);

CREATE INDEX idx_categoria ON productos(categoria);
CREATE INDEX idx_marca ON productos(marca);
CREATE INDEX idx_precio ON productos(precio);

CREATE INDEX IF NOT EXISTS idx_pedidos_fecha ON pedidos(fecha DESC);
CREATE INDEX IF NOT EXISTS idx_pedidos_estado ON pedidos(estado);
CREATE INDEX IF NOT EXISTS idx_pedido_items_pedido ON pedido_items(pedido_id);
CREATE INDEX IF NOT EXISTS idx_pedido_items_producto ON pedido_items(producto_id);



-- Insertar datos de ejemplo
INSERT INTO productos (nombre, categoria, precio, stock, marca, descripcion, imagen_url) VALUES
('Procesador Intel Core i9-14900K', 'Procesadores', 589.99, 15, 'Intel', 
 'Procesador de 14ra generación con 24 núcleos (8P+16E), 32 threads, frecuencia máxima de 6.0 GHz. Socket LGA1700. Ideal para gaming y productividad extrema.', 
 'https://via.placeholder.com/300x200?text=Intel+i9'),

('Procesador AMD Ryzen 9 7950X', 'Procesadores', 549.99, 12, 'AMD', 
 'Procesador de 16 núcleos y 32 threads, arquitectura Zen 4, frecuencia boost de 5.7 GHz. Socket AM5. Excelente para multitarea y renderizado.', 
 'https://via.placeholder.com/300x200?text=AMD+Ryzen+9'),

('Tarjeta Gráfica NVIDIA RTX 4090', 'Tarjetas Gráficas', 1899.99, 8, 'NVIDIA', 
 '24GB GDDR6X, arquitectura Ada Lovelace, Ray Tracing de 3ra generación. La mejor GPU para gaming 4K y creación de contenido profesional.', 
 'https://via.placeholder.com/300x200?text=RTX+4090'),

('Tarjeta Gráfica AMD Radeon RX 7900 XTX', 'Tarjetas Gráficas', 999.99, 10, 'AMD', 
 '24GB GDDR6, arquitectura RDNA 3, excelente rendimiento en 4K. Compatible con FSR 3.0 y Ray Tracing.', 
 'https://via.placeholder.com/300x200?text=RX+7900+XTX'),

('Memoria RAM Corsair Vengeance DDR5 32GB', 'Memoria RAM', 149.99, 25, 'Corsair', 
 'Kit de 2x16GB, 6000MHz, CL36, perfil XMP 3.0. Compatible con Intel y AMD. Diseño con disipador térmico de aluminio.', 
 'https://via.placeholder.com/300x200?text=Corsair+RAM'),

('Memoria RAM G.Skill Trident Z5 64GB', 'Memoria RAM', 279.99, 18, 'G.Skill', 
 'Kit de 2x32GB, 6400MHz, CL32, RGB personalizable. Diseñada para workstations y gaming extremo.', 
 'https://via.placeholder.com/300x200?text=GSkill+RAM'),

('SSD Samsung 990 PRO 2TB', 'Almacenamiento', 199.99, 30, 'Samsung', 
 'NVMe M.2, velocidades de lectura hasta 7,450 MB/s. Interfaz PCIe 4.0, ideal para gaming y transferencia de archivos grandes.', 
 'https://via.placeholder.com/300x200?text=Samsung+990+PRO'),

('SSD WD Black SN850X 4TB', 'Almacenamiento', 349.99, 20, 'Western Digital', 
 'NVMe M.2, velocidades de lectura hasta 7,300 MB/s. PCIe Gen4, perfecto para almacenar juegos y proyectos multimedia.', 
 'https://via.placeholder.com/300x200?text=WD+Black'),

('Placa Madre ASUS ROG Strix Z790-E', 'Placas Madre', 449.99, 14, 'ASUS', 
 'Socket LGA1700, chipset Z790, DDR5, PCIe 5.0, WiFi 6E. Diseño premium con iluminación RGB Aura Sync y VRM robusto.', 
 'https://via.placeholder.com/300x200?text=ASUS+ROG'),

('Placa Madre MSI MAG B650 TOMAHAWK', 'Placas Madre', 259.99, 16, 'MSI', 
 'Socket AM5, chipset B650, DDR5, PCIe 5.0. Excelente relación calidad-precio para procesadores Ryzen serie 7000.', 
 'https://via.placeholder.com/300x200?text=MSI+Tomahawk'),

('Fuente de Poder Corsair RM1000x', 'Fuentes de Poder', 189.99, 22, 'Corsair', 
 '1000W, certificación 80+ Gold, modular completa. Ventilador silencioso de 135mm, garantía de 10 años.', 
 'https://via.placeholder.com/300x200?text=Corsair+PSU'),

('Gabinete NZXT H7 Flow', 'Gabinetes', 139.99, 18, 'NZXT', 
 'Mid-tower ATX, panel frontal de malla para flujo de aire óptimo. Incluye 3 ventiladores RGB, soporte para refrigeración líquida 360mm.', 
 'https://via.placeholder.com/300x200?text=NZXT+H7');

