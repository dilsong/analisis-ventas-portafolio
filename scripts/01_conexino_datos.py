import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os

load_dotenv()

# ================================
# CONEXIÓN A LA BASE DE DATOS
# ================================
password = quote_plus(os.getenv('DB_PASSWORD'))
user = os.getenv('DB_USER')
host = os.getenv('DB_HOST')
db = os.getenv('DB_NAME')

engine = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{db}')
print("✅ Conexión exitosa a MySQL!")

# ================================
# CARGA DE DATOS
# ================================
df_ventas = pd.read_sql("""
    SELECT 
        v.ID,
        v.Fecha,
        v.Cantidad,
        v.PrecioVenta,
        v.Descuento,
        (v.Cantidad * v.PrecioVenta) AS TotalVenta,
        (v.Cantidad * p.Costo) AS TotalCosto,
        ((v.Cantidad * v.PrecioVenta) - (v.Cantidad * p.Costo)) AS Ganancia,
        vd.Nombre AS Vendedor,
        vd.Apellido AS ApellidoVendedor,
        c.Nombre AS Cliente,
        c.Apellido AS ApellidoCliente,
        r.Nombre AS Region,
        p.Nombre AS Producto,
        cat.Nombre AS Categoria
    FROM ventas v
    LEFT JOIN vendedores vd ON v.Vendedor = vd.ID
    LEFT JOIN clientes c ON v.Cliente = c.ID
    LEFT JOIN productos p ON v.Producto = p.ID
    LEFT JOIN categorias cat ON p.Categoria = cat.ID
    LEFT JOIN regiones r ON vd.Region = r.ID
""", engine)

# Procesamiento de fechas
df_ventas['Fecha'] = pd.to_datetime(df_ventas['Fecha'])
df_ventas['Año'] = df_ventas['Fecha'].dt.year
df_ventas['Mes'] = df_ventas['Fecha'].dt.month
df_ventas['AñoMes'] = df_ventas['Fecha'].dt.to_period('M')

print(f"✅ Datos cargados correctamente!")
print(f"   Total registros: {len(df_ventas)}")
print(f"   Período: {df_ventas['Fecha'].min().date()} al {df_ventas['Fecha'].max().date()}")
print(f"   Total ventas: ${df_ventas['TotalVenta'].sum():,.2f}")
print(f"   Total ganancia: ${df_ventas['Ganancia'].sum():,.2f}")

engine.dispose()