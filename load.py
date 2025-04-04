from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
from datetime import datetime, timedelta
import uuid, random

# Conectar al clúster Cassandra (nodo seed en localhost:9042)
cluster = Cluster(contact_points=["127.0.0.1"], port=9042)
session = cluster.connect("reservas_ks")  # keyspace previamente creado

# 1. Insertar usuarios de ejemplo
usuarios = []
for i in range(1, 21):
    dpi = f"DPI{i:04d}"
    nombre = f"Usuario{i}"
    email = f"usuario{i}@example.com"
    telefono = f"{random.randint(10000000, 99999999)}"
    nit = f"NIT-{random.randint(100000,999999)}"
    usuarios.append(dpi)
    session.execute(
        "INSERT INTO usuario (dpi, nombre, email, telefono, nit) VALUES (%s, %s, %s, %s, %s)",
        (dpi, nombre, email, telefono, nit)
    )

# 2. Insertar espacios de ejemplo
espacios = []
tipos = ["Sala", "Laboratorio", "Auditorio", "Cancha", "Sala"]  # tipos arbitrarios
for j in range(1, 6):
    id_esp = f"ESP{j:02d}"
    nombre = f"Espacio {j}"
    tipo = tipos[j-1]
    capacidad = random.choice([10, 20, 50, 100])
    ubicacion = f"Nivel {random.randint(1,5)}"
    espacios.append(id_esp)
    session.execute(
        "INSERT INTO espacio (id_espacio, nombre, tipo, capacidad_max, ubicacion) VALUES (%s, %s, %s, %s, %s)",
        (id_esp, nombre, tipo, capacidad, ubicacion)
    )

# 3. Crear e insertar 100,000 reservas
# Rango de fechas: por ejemplo, desde 2025-01-01 hasta 2025-12-31
fecha_inicio = datetime(2025, 1, 1)
dias_rango = 365  # un año de rango de fechas
for n in range(100000):
    # Seleccionar usuario y espacio aleatoriamente
    dpi = random.choice(usuarios)
    id_esp = random.choice(espacios)
    # Generar fecha y hora aleatoria
    delta_dias = random.randint(0, dias_rango - 1)
    fecha_reserva = fecha_inicio + timedelta(days=delta_dias)
    # Escoger hora de inicio aleatoria (entre 0 y 23h)
    hora = random.randint(0, 23)
    minuto = random.choice([0, 30])  # slots de comienzo a cada hora o media hora
    inicio = fecha_reserva.replace(hour=hora, minute=minuto, second=0, microsecond=0)
    # Duración aleatoria de 1 a 3 horas (para hora_fin)
    duracion_horas = random.randint(1, 3)
    fin = inicio + timedelta(hours=duracion_horas)
    # Generar UUID para la reserva
    id_reserva = uuid.uuid4()
    estado = "activa"

    # Obtener detalles del usuario y espacio (podríamos haberlos guardado en diccionarios arriba)
    nombre_usuario = f"Usuario{dpi[-4:]}"  # Dado nuestro formato DPI0001 -> Usuario1
    # (En un caso real, obtendríamos nombre de un dict usando DPI como clave)
    # Para simplificar, asumimos nombre_usuario coincide con identificador en este contexto.
    # Igual con detalles de espacio:
    nombre_espacio = f"Espacio {int(id_esp[-2:])}"
    tipo_espacio = tipos[int(id_esp[-2:]) - 1]
    # capacidad y ubicacion podrían buscarse si los hubiéramos almacenado; aquí usamos la lista creada:
    capacidad_espacio = None  # (omitido por simplicidad en este ejemplo)
    ubicacion_espacio = None  # (omitido por simplicidad)

    # Preparar sentencia de Batch para insertar en las 3 tablas de reservas
    cql_batch = f"""
    BEGIN BATCH
      INSERT INTO reservas_por_usuario (dpi, fecha, hora_inicio, id_reserva, id_espacio, nombre_espacio, tipo_espacio, ubicacion_espacio, hora_fin, estado, nombre_usuario, capacidad_espacio)
      VALUES ('{dpi}', '{inicio.date()}', '{inicio.time()}', {id_reserva}, '{id_esp}', '{nombre_espacio}', '{tipo_espacio}', '{ubicacion_espacio}', '{fin.time()}', '{estado}', '{nombre_usuario}', {capacidad_espacio});
      INSERT INTO reservas_por_espacio (id_espacio, fecha, hora_inicio, id_reserva, dpi, nombre_usuario, hora_fin, estado, tipo_espacio, capacidad_espacio, ubicacion_espacio)
      VALUES ('{id_esp}', '{inicio.date()}', '{inicio.time()}', {id_reserva}, '{dpi}', '{nombre_usuario}', '{fin.time()}', '{estado}', '{tipo_espacio}', {capacidad_espacio}, '{ubicacion_espacio}');
      INSERT INTO reservas_por_fecha (fecha, hora_inicio, id_espacio, id_reserva)
      VALUES ('{inicio.date()}', '{inicio.time()}', '{id_esp}', {id_reserva});
    APPLY BATCH;
    """
    session.execute(SimpleStatement(cql_batch))
