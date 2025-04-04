# <div align="center">  Proyecto #1 - Grupo 2 </div>

## <div align="center">  Laboratorio Sistemas de Bases de Datos 2 - Sección A </div>
## <div align="center">  Primer Semestre 2025 </div> 
___

## Miembros

| Nombre | Carnet |
|:------:|:------:|
| Julio Alejandro Zaldaña Ríos | 202110206 |
| Edgar Mauricio Gómez Flores | 2011-14340 |
| Edgar Rolando Alvarez Rodriguez  | 202001144 |

______

## <div align="center">  Fases de Desarrollo </div> 

### Modelo Conceptual (Entidad-Relación)

3 entidades principales:

1. Usuario
2. Reserva
3. Espacio

Se realizan las relaciones entre tablas, como un modelo relacional.

<img src="./img/conceptual.png" width=95%>


### Modelo Lógico

Se aplica desnormalización en el modelo anterior, para evitar:

* Evitar JOINS
* Normalización excesiva

<img src="./img/logico.png" width=95%>

1. **Usuario:**

DPI (pk)
nombre
email
telefono
NIT


2. **Reservas:**

id_reserva
DPI
id_espacio
nombre_espacio
nombre_usuario
fecha
hora_inicio
hora_fin
estado
tipo_espacio
capacidad_espacio
ubicacion_espacio



3. **Espacio:**

id_espacio (pk)
nombre
tipo
capacidad_max
ubicacion


### Modelo Físico

#### Clúster de Cassandra en Docker (3 nodos, SimpleStrategy)

Se configura un clúster local de Cassandra con 3 nodos usando Docker y Docker Compose. Para simplificar, usaremos la estrategia de replicación SimpleStrategy (adecuada para un solo centro de datos) con factor de replicación = 2 para nuestro keyspace​. Esto significa que cada dato se copiará en dos nodos distintos del clúster, aumentando la tolerancia a fallos (si un nodo cae, el dato aún reside en otro).

Docker Compose nos permite definir los 3 contenedores Cassandra y sus parámetros. Uno de los nodos actúa como seed (nodo semilla) para que los demás puedan unirse al anillo. Cada contenedor expone el puerto 9042 (protocolo CQL nativo) en el host con un puerto distinto para poder conectarnos desde la máquina anfitriona. También habilitamos JMX en cada nodo (puerto 7199) para monitoreo.

#### Monitoreo con Prometheus del clúster Cassandra

Para monitorear el desempeño y estado del clúster Cassandra, integraremos Prometheus en nuestro entorno Docker. Prometheus recopilará métricas de los nodos Cassandra, tales como uso de CPU, operaciones por segundo, latencia de lecturas/escrituras, tamaño de datos, estado de los nodos, etc., que son expuestas vía JMX.

Cassandra expone sus métricas internas a través de JMX (Java Management Extensions) en el puerto 7199. Prometheus no puede leer JMX directamente, por lo que utilizamos un exporter que traduzca de JMX a un endpoint HTTP de métricas en formato Prometheus. En este proyecto usaremos la imagen criteord/cassandra_exporter (un exportador de Cassandra listo para usar). Desplegaremos un contenedor exportador por cada nodo Cassandra.

Esta configuración define un único job llamado "cassandra" con tres targets estáticos: los tres exportadores en sus puertos internos 8080 (Prometheus, al estar en la misma red Docker, usará directamente los nombres de contenedor cassandra*-exporter). Cada 15 segundos Prometheus consultará cada exportador para obtener las métricas actuales. Acceso a Prometheus: Una vez que todos los servicios estén en marcha, podemos acceder a la interfaz web de Prometheus en http://localhost:9090. En esta interfaz, bajo Status -> Targets, deberíamos ver los tres objetivos (exporters) con estado "UP" si todo funciona correctamente. También podemos explorar las métricas en Graph o Metrics – por ejemplo, buscar org_apache_cassandra_metrics para ver métricas específicas de Cassandra.

#### Modelado desnormalizado en Cassandra

Crearemos un keyspace específico para la aplicación (`reservas_ks`) con replicación SimpleStrategy y factor 2. Dentro de este keyspace definiremos cinco tablas principales:

1. usuario – datos de usuarios.
2. espacio – datos de espacios.
3. reservas_por_usuario – historial de reservas por usuario.
4. reservas_por_espacio – historial de reservas por espacio (ordenadas por fecha).
5. reservas_por_fecha – índice de reservas por fecha/horario (para ayudar a consultar disponibilidad).

Las sentencias de creación están en [ddl](./ddl.cql).

#### Script de carga de datos en Python (usuarios, espacios, reservas)

Crearemos un script Python [load](./load.py) que genere estos datos aleatoriamente y los inserte en Cassandra. El script usará el controlador Python de Cassandra (Datastax cassandra-driver) para conectarse al clúster y ejecutar las inserciones. Para eficiencia, aprovecharemos Batch Writes, es decir, agruparemos las escrituras de una misma operación lógica en un solo batch CQL para reducir viajes de red y asegurar atomicidad.

Antes de ejecutar el script, asegúrese de tener instaladas las dependencias en su entorno Python local, principalmente:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install cassandra-driver 
```

Y finalmente ejecutar el script con:

```bash
python3 load.py
```

____

### Requerimientos Técnicos del Proyecto

