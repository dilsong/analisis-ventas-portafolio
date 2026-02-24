import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os

load_dotenv()

password = quote_plus(os.getenv('DB_PASSWORD'))
engine = create_engine(f'mysql+mysqlconnector://{os.getenv("DB_USER")}:{password}@{os.getenv("DB_HOST")}/{os.getenv("DB_NAME")}')

df_ventas = pd.read_sql("""
    SELECT 
        v.Fecha,
        v.Cantidad,
        (v.Cantidad * v.PrecioVenta) AS TotalVenta,
        (v.Cantidad * p.Costo) AS TotalCosto,
        ((v.Cantidad * v.PrecioVenta) - (v.Cantidad * p.Costo)) AS Ganancia,
        v.Descuento,
        vd.Nombre AS Vendedor,
        vd.Apellido AS ApellidoVendedor,
        r.Nombre AS Region,
        p.Nombre AS Producto,
        cat.Nombre AS Categoria
    FROM ventas v
    LEFT JOIN vendedores vd ON v.Vendedor = vd.ID
    LEFT JOIN productos p ON v.Producto = p.ID
    LEFT JOIN categorias cat ON p.Categoria = cat.ID
    LEFT JOIN regiones r ON vd.Region = r.ID
""", engine)

df_ventas['Fecha'] = pd.to_datetime(df_ventas['Fecha'])
df_ventas['Año'] = df_ventas['Fecha'].dt.year
df_ventas['Mes'] = df_ventas['Fecha'].dt.month
df_ventas['AñoMes'] = df_ventas['Fecha'].dt.to_period('M')

print("=== RESUMEN GENERAL ===")
print(f"Total ventas: ${df_ventas['TotalVenta'].sum():,.2f}")
print(f"Total ganancia: ${df_ventas['Ganancia'].sum():,.2f}")
print(f"Margen general: {(df_ventas['Ganancia'].sum() / df_ventas['TotalVenta'].sum() * 100):.1f}%")

print("\n=== VENTAS POR CATEGORÍA ===")
categoria = df_ventas.groupby('Categoria').agg(
    Total_Ventas=('TotalVenta', 'sum'),
    Total_Ganancia=('Ganancia', 'sum'),
    Transacciones=('TotalVenta', 'count')
).round(2)
categoria['Margen_%'] = (categoria['Total_Ganancia'] / categoria['Total_Ventas'] * 100).round(1)
print(categoria.sort_values('Total_Ventas', ascending=False))

print("\n=== VENTAS POR REGIÓN ===")
print(df_ventas.groupby('Region')['TotalVenta'].sum().round(2).sort_values(ascending=False))

print("\n=== VENTAS POR AÑO ===")
print(df_ventas.groupby('Año')['TotalVenta'].sum().round(2))

engine.dispose()