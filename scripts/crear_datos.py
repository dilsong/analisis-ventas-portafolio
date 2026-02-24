import mysql.connector
from faker import Faker
import random
from datetime import date
from dotenv import load_dotenv
import os

load_dotenv()
fake = Faker('es_MX')  # Datos en español

conexion = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database='ventas_portafolio'
)
cursor = conexion.cursor()

# REGIONES
regiones = ['Norte', 'Sur', 'Este', 'Oeste', 'Centro']
for region in regiones:
    cursor.execute("INSERT INTO regiones (Nombre) VALUES (%s)", (region,))

# CATEGORÍAS
categorias = ['Electrónica', 'Ropa', 'Hogar', 'Deportes', 'Alimentos']
for categoria in categorias:
    cursor.execute("INSERT INTO categorias (Nombre) VALUES (%s)", (categoria,))

conexion.commit()
print("✅ Regiones y categorías creadas!")

# PRODUCTOS con costos y precios coherentes por categoría
productos = [
    ('Laptop', 1, 800, 1200),
    ('Smartphone', 1, 400, 650),
    ('Tablet', 1, 300, 480),
    ('Audífonos', 1, 50, 90),
    ('Smart TV', 1, 500, 800),
    ('Camisa', 2, 15, 35),
    ('Pantalón', 2, 20, 50),
    ('Zapatos', 2, 30, 80),
    ('Vestido', 2, 25, 65),
    ('Chaqueta', 2, 40, 100),
    ('Sofá', 3, 300, 600),
    ('Mesa', 3, 150, 300),
    ('Lámpara', 3, 30, 70),
    ('Silla', 3, 80, 160),
    ('Estante', 3, 60, 120),
    ('Bicicleta', 4, 200, 380),
    ('Pesas', 4, 40, 80),
    ('Tenis', 4, 45, 90),
    ('Mochila', 4, 25, 55),
    ('Tienda Camping', 4, 100, 200),
    ('Arroz 5kg', 5, 5, 10),
    ('Aceite 1L', 5, 3, 6),
    ('Café 500g', 5, 8, 15),
    ('Azúcar 2kg', 5, 4, 8),
    ('Pasta 500g', 5, 2, 5),
]

for producto in productos:
    cursor.execute("""
        INSERT INTO productos (Nombre, Categoria, Costo, PrecioVenta) 
        VALUES (%s, %s, %s, %s)
    """, producto)

conexion.commit()
print("✅ Productos creados!")

# CLIENTES - 200 clientes
for _ in range(200):
    cursor.execute("""
        INSERT INTO clientes (Nombre, Apellido, Email, Region, FechaRegistro)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        fake.first_name(),
        fake.last_name(),
        fake.email(),
        random.randint(1, 5),
        fake.date_between(start_date=date(2020, 1, 1), end_date=date(2021, 12, 31))
    ))

conexion.commit()
print("✅ 200 clientes creados!")

# VENDEDORES - 20 vendedores
for _ in range(20):
    cursor.execute("""
        INSERT INTO vendedores (Nombre, Apellido, Region, FechaIngreso)
        VALUES (%s, %s, %s, %s)
    """, (
        fake.first_name(),
        fake.last_name(),
        random.randint(1, 5),
        fake.date_between(start_date=date(2019, 1, 1), end_date=date(2022, 12, 31))
    ))

conexion.commit()
print("✅ 20 vendedores creados!")

# VENTAS - 2000 registros coherentes
cursor.execute("SELECT ID, PrecioVenta FROM productos")
productos_db = cursor.fetchall()

for _ in range(2000):
    producto = random.choice(productos_db)
    descuento = random.choice([0, 0, 0, 5, 10, 15, 20])  # Mayoría sin descuento
    precio_final = round(float(producto[1]) * (1 - descuento/100), 2)
    
    cursor.execute("""
        INSERT INTO ventas (Fecha, Cliente, Vendedor, Producto, Cantidad, PrecioVenta, Descuento)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        fake.date_between(start_date=date(2022, 1, 1), end_date=date(2024, 12, 31)),
        random.randint(1, 200),
        random.randint(1, 20),
        producto[0],
        random.randint(1, 5),
        precio_final,
        descuento
    ))

conexion.commit()
print("✅ 2000 registros de ventas creados!")

cursor.close()
conexion.close()
print("\n🎉 Base de datos lista para el análisis!")