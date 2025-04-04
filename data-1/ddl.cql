-- Keyspace para la aplicación de reservas
CREATE KEYSPACE reservas_ks 
  WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 2};

USE reservas_ks;

-- Tabla de Usuarios
CREATE TABLE usuario (
  dpi TEXT PRIMARY KEY,       -- Identificador único de usuario (DPI)
  nombre TEXT,
  email TEXT,
  telefono TEXT,
  nit TEXT
);

-- Tabla de Espacios
CREATE TABLE espacio (
  id_espacio TEXT PRIMARY KEY,  -- Identificador único del espacio
  nombre TEXT,
  tipo TEXT,
  capacidad_max INT,
  ubicacion TEXT
);

-- Historial de reservas por Usuario
CREATE TABLE reservas_por_usuario (
  dpi TEXT,                 -- Usuario (partición)
  fecha DATE,               -- Fecha de la reserva
  hora_inicio TIME,         -- Hora de inicio
  id_reserva UUID,          -- ID único de la reserva
  id_espacio TEXT,
  nombre_espacio TEXT,
  tipo_espacio TEXT,
  ubicacion_espacio TEXT,
  hora_fin TIME,
  estado TEXT,
  nombre_usuario TEXT,
  capacidad_espacio INT,
  PRIMARY KEY ((dpi), fecha, hora_inicio, id_reserva)
) WITH CLUSTERING ORDER BY (fecha DESC, hora_inicio ASC, id_reserva ASC);

-- Historial de reservas por Espacio (ordenadas por fecha/hora)
CREATE TABLE reservas_por_espacio (
  id_espacio TEXT,          -- Espacio (partición)
  fecha DATE,               -- Fecha de la reserva
  hora_inicio TIME,         -- Hora de inicio
  id_reserva UUID,          -- ID único de la reserva
  dpi TEXT,
  nombre_usuario TEXT,
  hora_fin TIME,
  estado TEXT,
  tipo_espacio TEXT,
  capacidad_espacio INT,
  ubicacion_espacio TEXT,
  PRIMARY KEY ((id_espacio), fecha, hora_inicio, id_reserva)
) WITH CLUSTERING ORDER BY (fecha DESC, hora_inicio ASC, id_reserva ASC);

-- Disponibilidad de espacios por fecha y hora
CREATE TABLE reservas_por_fecha (
  fecha DATE,               -- Fecha (parte de la partición)
  hora_inicio TIME,         -- Hora (parte de la partición)
  id_espacio TEXT,          -- Espacio reservado en esa fecha/hora (clave de clúster)
  id_reserva UUID,
  PRIMARY KEY ((fecha), hora_inicio, id_espacio, id_reserva)
);
