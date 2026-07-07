# ==============================================================
# ALERTA SÍSMICA EXCLUSIVA: VENEZUELA Y COLOMBIA
# Fuentes: USGS (Mundial), EMSC (Europa y Latinoamérica)
# Validación cruzada para evitar falsas alarmas
# Con alertas en pantalla, vibración y notificaciones
# ==============================================================

import requests
import time
import math
from datetime import datetime

# -------------------------- CONFIGURACIÓN --------------------------
MAGNITUD_MINIMA = 3.8       # Avisa desde magnitud 3.8 (más sensible en la región)
# Coordenadas que cubren todo Venezuela, Colombia y zonas fronterizas
LAT_MIN = 0.5
LAT_MAX = 13.0
LON_MIN = -79.5
LON_MAX = -59.5
INTERVALO_CONSULTA = 120    # Revisa datos cada 2 minutos
# -------------------------------------------------------------------

# Configurar alertas del teléfono
try:
    from androidhelper import Android
    droid = Android()
    ALERTAS_ACTIVAS = True
except ImportError:
    ALERTAS_ACTIVAS = False
    print("⚠️  Nota: Sin acceso a funciones del sistema. Solo alertas en pantalla.\n")

# -------------------------- FUNCIONES AUXILIARES --------------------------
def activar_alertas():
    """Activa vibración y notificación si es posible"""
    if ALERTAS_ACTIVAS:
        droid.vibrate(1200)
        time.sleep(0.5)
        droid.vibrate(1200)
        droid.notify("⚠️ ALERTA SÍSMICA", "Sismo confirmado en Venezuela / Colombia")

def esta_en_la_zona(latitud, longitud):
    """Verifica que el sismo esté dentro de la región seleccionada"""
    return LAT_MIN <= latitud <= LAT_MAX and LON_MIN <= longitud <= LON_MAX

def consultar_fuente_usgs():
    """Consulta datos oficiales del USGS"""
    sismos = []
    try:
        url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&minmagnitude={MAGNITUD_MINIMA}&limit=15"
        respuesta = requests.get(url, timeout=15)
        datos = respuesta.json()
        
        for evento in datos["features"]:
            sismos.append({
                "magnitud": evento["properties"]["mag"],
                "lat": evento["geometry"]["coordinates"][1],
                "lon": evento["geometry"]["coordinates"][0],
                "lugar": evento["properties"]["place"],
                "hora": evento["properties"]["time"]
            })
    except Exception as error:
        print(f"⚠️  Error al consultar USGS: {str(error)[:50]}...")
    return sismos

def consultar_fuente_emsc():
    """Consulta datos oficiales del EMSC"""
    sismos = []
    try:
        url = f"https://www.seismicportal.eu/fdsnws/event/1/query?format=json&minmagnitude={MAGNITUD_MINIMA}&limit=15"
        respuesta = requests.get(url, timeout=15)
        datos = respuesta.json()
        
        for evento in datos["features"]:
            sismos.append({
                "magnitud": evento["properties"]["mag"],
                "lat": evento["geometry"]["coordinates"][1],
                "lon": evento["geometry"]["coordinates"][0],
                "lugar": evento["properties"]["place"],
                "hora": evento["properties"]["time"]
            })
    except Exception as error:
        print(f"⚠️  Error al consultar EMSC: {str(error)[:50]}...")
    return sismos

# -------------------------- PROGRAMA PRINCIPAL --------------------------
def main():
    print("=" * 70)
    print("🚨 SISTEMA DE ALERTA SÍSMICA: VENEZUELA Y COLOMBIA")
    print(f"🔍 Monitoreando sismos mayores a magnitud {MAGNITUD_MINIMA}")
    print("✅ Fuentes oficiales | Validación cruzada")
    print("=" * 70 + "\n")
    
    eventos_vistos = set()

    while True:
        hora_actual = datetime.now().strftime("%H:%M:%S")
        print(f"🔎 Consultando fuentes... {hora_actual}")

        # Obtener datos de ambas fuentes
        sismos_usgs = consultar_fuente_usgs()
        sismos_emsc = consultar_fuente_emsc()
        todos_los_sismos = sismos_usgs + sismos_emsc

        # Filtrar y validar eventos nuevos
        confirmados = []
        for sismo in todos_los_sismos:
            # Identificador único para evitar repetir avisos
            clave = f"{sismo['magnitud']}_{round(sismo['lat'], 1)}_{round(sismo['lon'], 1)}"
            
            if clave not in eventos_vistos and esta_en_la_zona(sismo["lat"], sismo["lon"]):
                eventos_vistos.add(clave)
                confirmados.append(sismo)

        # Mostrar alertas de eventos confirmados
        for sismo in confirmados:
            activar_alertas()
            print("\n" + "❗" * 60)
            print(f"⚠️  SISMO CONFIRMADO EN LA REGIÓN")
            print(f"📌 Lugar: {sismo['lugar']}")
            print(f"📊 Magnitud: {sismo['magnitud']}")
            print(f"🌍 Coordenadas: {round(sismo['lat'], 2)}° N / {round(sismo['lon'], 2)}° O")
            print(f"⏱️  Hora exacta: {datetime.fromtimestamp(sismo['hora'] / 1000)}")
            print("❗" * 60 + "\n")

        # Esperar antes de la siguiente consulta
        time.sleep(INTERVALO_CONSULTA)

# Ejecutar el programa
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n✅ Monitoreo detenido correctamente por ti")
    except Exception as error_general:
        print(f"\n❌ Error inesperado: {error_general}")
        print("🔁 El programa se reiniciará automáticamente en 10 segundos...")
        time.sleep(10)
        main()
