import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

load_dotenv()

password = quote_plus(os.getenv('DB_PASSWORD'))
engine = create_engine(f'mysql+mysqlconnector://{os.getenv("DB_USER")}:{password}@{os.getenv("DB_HOST")}/{os.getenv("DB_NAME")}')

df = pd.read_sql("""
    SELECT 
        v.Fecha,
        v.Cantidad,
        (v.Cantidad * v.PrecioVenta) AS TotalVenta,
        (v.Cantidad * p.Costo) AS TotalCosto,
        ((v.Cantidad * v.PrecioVenta) - (v.Cantidad * p.Costo)) AS Ganancia,
        v.Descuento,
        r.Nombre AS Region,
        p.Nombre AS Producto,
        cat.Nombre AS Categoria
    FROM ventas v
    LEFT JOIN vendedores vd ON v.Vendedor = vd.ID
    LEFT JOIN regiones r ON vd.Region = r.ID
    LEFT JOIN productos p ON v.Producto = p.ID
    LEFT JOIN categorias cat ON p.Categoria = cat.ID
""", engine)

df['Fecha'] = pd.to_datetime(df['Fecha'])
df['Año'] = df['Fecha'].dt.year
df['Mes'] = df['Fecha'].dt.month
df['AñoMes'] = df['Fecha'].dt.to_period('M')

# ================================
# ANÁLISIS 1 - CATEGORÍAS POR REGIÓN
# ================================
print("=== VENTAS POR CATEGORÍA Y REGIÓN ===")
cat_region = df.groupby(['Region', 'Categoria'])['TotalVenta'].sum().round(2).unstack()
print(cat_region)

# ================================
# ANÁLISIS 2 - COMPORTAMIENTO 2024 MES A MES
# ================================
print("\n=== COMPORTAMIENTO MENSUAL 2024 ===")
df_2024 = df[df['Año'] == 2024].groupby('Mes')['TotalVenta'].sum().round(2)
print(df_2024)
print(f"\n¿Crecimiento constante 2024? {'✅ Sí' if df_2024.is_monotonic_increasing else '⚠️ No, hay variaciones'}")

# ================================
# VISUALIZACIONES
# ================================
fig, axes = plt.subplots(2, 2, figsize=(18, 12))
fig.suptitle('Análisis Profundo de Ventas', fontsize=16, fontweight='bold')

# GRÁFICA 1 - Categorías por región
cat_region.plot(kind='bar', ax=axes[0,0], colormap='Set2')
axes[0,0].set_title('Ventas por Categoría y Región')
axes[0,0].set_xlabel('Región')
axes[0,0].set_ylabel('Ventas ($)')
axes[0,0].tick_params(axis='x', rotation=45)
axes[0,0].legend(title='Categoría', bbox_to_anchor=(1, 1))

# GRÁFICA 2 - Comportamiento mensual 2024
meses = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
sns.barplot(ax=axes[0,1], x=df_2024.index, y=df_2024.values,
            hue=df_2024.index.astype(str), palette='Blues_r', legend=False)
axes[0,1].set_title('Comportamiento Mensual 2024')
axes[0,1].set_xlabel('Mes')
axes[0,1].set_ylabel('Ventas ($)')
axes[0,1].set_xticks(range(len(df_2024)))
axes[0,1].set_xticklabels(meses[:len(df_2024)], rotation=45)

# GRÁFICA 3 - Tendencia 3 años con línea
ventas_mes = df.groupby('AñoMes')['TotalVenta'].sum().reset_index()
ventas_mes['AñoMes'] = ventas_mes['AñoMes'].astype(str)
axes[1,0].plot(ventas_mes['AñoMes'], ventas_mes['TotalVenta'], 
               marker='o', linewidth=2, color='steelblue', label='Ventas')
z = np.polyfit(range(len(ventas_mes)), ventas_mes['TotalVenta'], 1)
p = np.poly1d(z)
axes[1,0].plot(ventas_mes['AñoMes'], p(range(len(ventas_mes))),
               linestyle='--', color='red', linewidth=1.5, label='Tendencia')
axes[1,0].set_title('Tendencia de Ventas 2022-2024')
axes[1,0].tick_params(axis='x', rotation=90)
axes[1,0].legend()
axes[1,0].grid(True, alpha=0.3)

# GRÁFICA 4 - Margen por categoría
margen_cat = df.groupby('Categoria').agg(
    Ventas=('TotalVenta', 'sum'),
    Ganancia=('Ganancia', 'sum')
).round(2)
margen_cat['Margen_%'] = (margen_cat['Ganancia'] / margen_cat['Ventas'] * 100).round(1)
sns.barplot(ax=axes[1,1], x=margen_cat.index, y=margen_cat['Margen_%'],
            hue=margen_cat.index, palette='Greens_r', legend=False)
axes[1,1].set_title('Margen de Ganancia por Categoría (%)')
axes[1,1].set_xlabel('Categoría')
axes[1,1].set_ylabel('Margen (%)')
axes[1,1].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.show()

# ================================
# GRÁFICA - PROMEDIO 3 AÑOS VS 2024
# ================================

# Promedio mensual de los 3 años
promedio_3años = df.groupby(['Año', 'Mes'])['TotalVenta'].sum().reset_index()
promedio_mensual = promedio_3años.groupby('Mes')['TotalVenta'].mean().round(2)

# Ventas mensuales 2024
ventas_2024 = df[df['Año'] == 2024].groupby('Mes')['TotalVenta'].sum().round(2)

# Crear DataFrame comparativo
df_comparativo = pd.DataFrame({
    'Promedio_3años': promedio_mensual,
    'Ventas_2024': ventas_2024
}).fillna(0)

# Gráfica comparativa
fig, axes = plt.subplots(2, 1, figsize=(14, 12))

# GRÁFICA 1 - Comparativo promedio vs 2024
meses_nombres = ['Ene','Feb','Mar','Abr','May','Jun',
                 'Jul','Ago','Sep','Oct','Nov','Dic']
x = range(1, 13)
axes[0].plot(x, df_comparativo['Promedio_3años'], 
             marker='o', linewidth=2, color='steelblue', 
             label='Promedio 2022-2024')
axes[0].plot(x, df_comparativo['Ventas_2024'], 
             marker='s', linewidth=2, color='orange',
             label='2024')
axes[0].fill_between(x, df_comparativo['Promedio_3años'], 
                     df_comparativo['Ventas_2024'],
                     alpha=0.2, color='green', 
                     label='Diferencia')
axes[0].set_title('Comparativo Ventas 2024 vs Promedio 3 Años', 
                  fontsize=14, fontweight='bold')
axes[0].set_xlabel('Mes')
axes[0].set_ylabel('Ventas ($)')
axes[0].set_xticks(list(x))
axes[0].set_xticklabels(meses_nombres)
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Línea de referencia del promedio general
promedio_general = df_comparativo['Promedio_3años'].mean()
axes[0].axhline(y=promedio_general, color='red', 
                linestyle='--', alpha=0.5, 
                label=f'Promedio general: ${promedio_general:,.0f}')
axes[0].legend()

# GRÁFICA 2 - Clientes por región
clientes_region = pd.read_sql("""
    SELECT r.Nombre AS Region, COUNT(c.ID) AS Total_Clientes
    FROM clientes c
    LEFT JOIN regiones r ON c.Region = r.ID
    GROUP BY r.Nombre
    ORDER BY Total_Clientes DESC
""", engine)

sns.barplot(ax=axes[1], data=clientes_region, 
            x='Region', y='Total_Clientes',
            hue='Region', palette='Blues_r', legend=False)
axes[1].set_title('Cantidad de Clientes por Región', 
                  fontsize=14, fontweight='bold')
axes[1].set_xlabel('Región')
axes[1].set_ylabel('Clientes')
for i, row in clientes_region.iterrows():
    axes[1].text(i, row['Total_Clientes'] + 0.5, 
                str(int(row['Total_Clientes'])), 
                ha='center', fontweight='bold')

print("\n=== TICKET PROMEDIO POR REGIÓN ===")
ticket_region = df.groupby('Region').agg(
    Total_Ventas=('TotalVenta', 'sum'),
    Transacciones=('TotalVenta', 'count'),
).round(2)
ticket_region['Ticket_Promedio'] = (ticket_region['Total_Ventas'] / ticket_region['Transacciones']).round(2)
print(ticket_region.sort_values('Ticket_Promedio', ascending=False))

plt.tight_layout()
plt.show()

print("\n=== CLIENTES POR REGIÓN ===")
print(clientes_region)

print("\n=== VENTAS POR CATEGORÍA Y REGIÓN ===")
cat_region = df.groupby(['Region', 'Categoria'])['TotalVenta'].sum().round(2).unstack()
print(cat_region)

engine.dispose()