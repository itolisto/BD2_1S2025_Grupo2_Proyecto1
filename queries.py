from cassandra.cluster import Cluster
from cassandra import ConsistencyLevel
from cassandra.query import SimpleStatement
import uuid
from datetime import date, datetime, timedelta
from collections import defaultdict

# auth = PlainTextAuthProvider(username='cassandra', password='cassandra')
# cluster = Cluster(contact_points=["127.0.0.1"], port=9042, auth_provider=auth)
cluster = Cluster(contact_points=["127.0.0.1"], port=9042)
session = cluster.connect("reservas_ks")

# a) Consultar espacios disponibles por fecha
def espacios_disponibles(fecha):
    filas = session.execute(
        "SELECT id_espacio FROM reservas_por_fecha WHERE fecha=%s",
        (fecha)
    )
    espacios_ocupados = {row.id_espacio for row in filas}
    # Todos los espacios menos los ocupados
    espacios_libres = [esp for esp in filas if esp not in espacios_ocupados]
    print(f"Espacios disponibles el {fecha}: {espacios_libres}")
    return espacios_libres

# b) Historial de reservas de un espacio en rango de fechas
def historial_reservas_usuario(dpi, fecha_inicio=None, fecha_fin=None):
    if fecha_inicio and fecha_fin:
        query = session.prepare("""
            SELECT fecha, hora_inicio, hora_fin, id_espacio, estado, nombre_espacio 
            FROM reservas_por_usuario 
            WHERE dpi=? AND fecha >= ? AND fecha <= ?
        """)
        params = (dpi, fecha_inicio, fecha_fin)
    else:
        query = session.prepare("""
            SELECT fecha, hora_inicio, hora_fin, id_espacio, estado, nombre_espacio 
            FROM reservas_por_usuario 
            WHERE dpi=?
        """)
        params = (dpi,)

    rows = session.execute(query, params)
    print(f"\nHistorial de reservas del usuario {dpi}:")
    for row in rows:
        print(f" - {row.fecha} | {row.hora_inicio}-{row.hora_fin} | {row.nombre_espacio} ({row.id_espacio}) | Estado: {row.estado}")

# c) Historial de reservas de un espacio en rango de fechas
def get_espacios():
    """
    Devuelve la lista de IDs de todos los espacios registrados.
    """
    rows = session.execute("SELECT id_espacio FROM espacio")
    return [row.id_espacio for row in rows]

def ocupacion_espacios(fecha_inicio, fecha_fin):
    espacios = get_espacios()
    ocupacion = defaultdict(list)
    for espacio in espacios:
        query = session.prepare("""
            SELECT fecha, hora_inicio, hora_fin, dpi, estado 
            FROM reservas_por_espacio 
            WHERE id_espacio=? AND fecha >= ? AND fecha <= ?
        """)
        rows = session.execute(query, (espacio, fecha_inicio, fecha_fin))
        for row in rows:
            ocupacion[espacio].append({
                'fecha': row.fecha,
                'hora_inicio': row.hora_inicio,
                'hora_fin': row.hora_fin,
                'dpi': row.dpi,
                'estado': row.estado
            })

    print(f"\nOcupación de espacios del {fecha_inicio} al {fecha_fin}:")
    for espacio_id, reservas in ocupacion.items():
        print(f"Espacio {espacio_id} - {len(reservas)} reservas:")
        for r in reservas:
            print(f"   - {r['fecha']} | {r['hora_inicio']}-{r['hora_fin']} | Usuario: {r['dpi']} | Estado: {r['estado']}")

# --- Ejemplos de uso de las funciones anteriores --- #
espacios_disponibles(date(2025, 5, 10))

historial_reservas_usuario("DPI0001", date(2025, 4, 1), date(2025, 4, 30))

ocupacion_espacios(date(2025, 4, 1), date(2025, 4, 3))
