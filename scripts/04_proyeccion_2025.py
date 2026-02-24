import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os
import matplotlib.pyplot as plt
import numpy as np

load_dotenv()

password = quote_plus(os.getenv('DB_PASSWORD'))
engine = create_engine(f'mysql+mysqlconnector://{os.getenv("DB_USER")}:{password}@{os.getenv("DB_HOST")}/{os.getenv("DB_NAME")}')

df = pd.read_sql("""
    SELECT 
        v.Fecha,
        (v.Cantidad * v.PrecioVenta) AS TotalVenta
    FROM ventas v
""", engine)

df['Fecha'] = pd.to_datetime(df['Fecha'])
df['Año'] = df['Fecha'].dt.year
df['Mes'] = df['Fecha'].dt.month

# ================================
# FACTORES ESTACIONALES POR MES
# ================================
# Basado en el análisis de temporadas comerciales
factores_estacionales = {
    1: 0.90,   # Enero - inicio de año, liquidaciones
    2: 1.20,   # Febrero - San Valentín, demostró ser fuerte
    3: 1.05,   # Marzo - Día de la Mujer, oportunidad
    4: 1.10,   # Abril - Semana Santa
    5: 1.25,   # Mayo - Día de la Madre, muy fuerte
    6: 0.95,   # Junio - cayó en 2024, reforzar
    7: 1.00,   # Julio - vacaciones
    8: 1.15,   # Agosto - regreso a clases
    9: 1.05,   # Septiembre - fiestas
    10: 1.20,  # Octubre - Halloween, demostró ser fuerte
    11: 1.25,  # Noviembre - Black Friday, oportunidad
    12: 1.35,  # Diciembre - Navidad, el más fuerte
}

# ================================
# PROMEDIO MENSUAL HISTÓRICO
# ================================
promedio_mensual = df.groupby(['Año', 'Mes'])['TotalVenta'].sum().reset_index()
promedio_mensual = promedio_mensual.groupby('Mes')['TotalVenta'].mean().round(2)

# ================================
# PROYECCIÓN 2025
# ================================
# Aplicamos crecimiento del 10% sobre el promedio histórico
# más los factores estacionales
crecimiento_base = 1.10

proyeccion_2025 = {}
for mes, promedio in promedio_mensual.items():
    proyeccion_2025[mes] = round(promedio * crecimiento_base * factores_estacionales[mes], 2)

df_proyeccion = pd.DataFrame({
    'Mes': list(proyeccion_2025.keys()),
    'Proyeccion_2025': list(proyeccion_2025.values()),
    'Promedio_Historico': promedio_mensual.values
})

df_proyeccion['Crecimiento_%'] = ((df_proyeccion['Proyeccion_2025'] - df_proyeccion['Promedio_Historico']) / df_proyeccion['Promedio_Historico'] * 100).round(1)

meses_nombres = ['Ene','Feb','Mar','Abr','May','Jun',
                 'Jul','Ago','Sep','Oct','Nov','Dic']
df_proyeccion['Mes_Nombre'] = meses_nombres

print("=== PROYECCIÓN DE VENTAS 2025 ===")
print(df_proyeccion[['Mes_Nombre', 'Promedio_Historico', 'Proyeccion_2025', 'Crecimiento_%']].to_string(index=False))
print(f"\nTotal proyectado 2025: ${df_proyeccion['Proyeccion_2025'].sum():,.2f}")
print(f"Total promedio histórico: ${df_proyeccion['Promedio_Historico'].sum():,.2f}")
print(f"Crecimiento proyectado: {((df_proyeccion['Proyeccion_2025'].sum() / df_proyeccion['Promedio_Historico'].sum()) - 1) * 100:.1f}%")

# ================================
# VISUALIZACIÓN
# ================================
fig, axes = plt.subplots(2, 1, figsize=(14, 12))
fig.suptitle('Proyección de Ventas 2025', fontsize=16, fontweight='bold')

# GRÁFICA 1 - Barras proyección + línea 2024
ventas_2024 = df[df['Año'] == 2024].groupby('Mes')['TotalVenta'].sum().round(2)

x = list(range(1, 13))
ax1 = axes[0]
ax2 = ax1.twinx()

# Barras
ax1.bar([i - 0.2 for i in x], df_proyeccion['Promedio_Historico'],
        width=0.4, label='Promedio Histórico', color='steelblue', alpha=0.7)
ax1.bar([i + 0.2 for i in x], df_proyeccion['Proyeccion_2025'],
        width=0.4, label='Proyección 2025', color='orange', alpha=0.7)

# Línea 2024
ax2.plot(x, ventas_2024.values,
         marker='D', linewidth=2.5, color='red',
         label='Real 2024', zorder=5)
ax2.set_ylabel('Ventas 2024 ($)', color='red')
ax2.tick_params(axis='y', labelcolor='red')

ax1.set_title('Histórico vs Proyección 2025 vs Real 2024')
ax1.set_xlabel('Mes')
ax1.set_ylabel('Ventas ($)')
ax1.set_xticks(x)
ax1.set_xticklabels(meses_nombres)
ax1.grid(True, alpha=0.3)

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

# GRÁFICA 2 - Línea de proyección con tendencia
axes[1].plot(meses_nombres, df_proyeccion['Promedio_Historico'],
             marker='o', linewidth=2, color='steelblue', label='Promedio Histórico')
axes[1].plot(meses_nombres, df_proyeccion['Proyeccion_2025'],
             marker='s', linewidth=2, color='orange', label='Proyección 2025')
axes[1].fill_between(meses_nombres, df_proyeccion['Promedio_Historico'],
                     df_proyeccion['Proyeccion_2025'],
                     alpha=0.2, color='green')
axes[1].set_title('Tendencia Proyectada 2025')
axes[1].set_xlabel('Mes')
axes[1].set_ylabel('Ventas ($)')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

engine.dispose()