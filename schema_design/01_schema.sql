-- habilitar extensión para uuids
create extension if not exists "uuid-ossp";

-- creación del esquema dedicado
create schema if not exists content;

-- 1. tabla categoria
create table content.categoria (
    id uuid primary key default uuid_generate_v4(),
    nombre varchar(100) not null,
    descripcion text,
    eliminado smallint default 0 not null check (eliminado in (0, 1))
);

-- 2. tabla usuario
create table content.usuario (
    id uuid primary key default uuid_generate_v4(),
    nombre varchar(100) not null,
    apellido_paterno varchar(100) not null,
    apellido_materno varchar(100) not null,
    email varchar(255) not null unique,
    contrasena varchar(255) not null,
    rol varchar(50) default 'cliente' not null,
    numero_telefono varchar(20),
    nit varchar(20) unique,
    eliminado smallint default 0 not null check (eliminado in (0, 1))
);

-- 3. tabla producto
create table content.producto (
    id uuid primary key default uuid_generate_v4(),
    nombre varchar(150) not null,
    descripcion text,
    precio int not null check (precio >= 0),
    categoria_id uuid,
    estado varchar(50) default 'activo' not null,
    eliminado smallint default 0 not null check (eliminado in (0, 1)),
    constraint fk_producto_categoria foreign key (categoria_id) 
        references content.categoria(id) on delete set null
);

-- 4. tabla orden
create table content.orden (
    id uuid primary key default uuid_generate_v4(),
    usuario_id uuid not null,
    tipo_solicitud varchar(50),
    fecha_solicitud timestamp with time zone default current_timestamp not null,
    eliminado smallint default 0 not null check (eliminado in (0, 1)),
    constraint fk_orden_usuario foreign key (usuario_id) 
        references content.usuario(id) on delete cascade
);

-- 5. tabla detalles_orden
create table content.detalles_orden (
    id uuid primary key default uuid_generate_v4(),
    orden_id uuid not null,
    producto_id uuid not null,
    cantidad int not null check (cantidad > 0),
    constraint fk_detalles_orden_orden foreign key (orden_id) 
        references content.orden(id) on delete cascade,
    constraint fk_detalles_orden_producto foreign key (producto_id) 
        references content.producto(id) on delete restrict
);

-- definición de índices para rendimiento
create index idx_producto_categoria_id on content.producto(categoria_id);
create index idx_orden_usuario_id on content.orden(usuario_id);
create index idx_orden_fecha_solicitud on content.orden(fecha_solicitud);
create index idx_detalles_orden_orden_id on content.detalles_orden(orden_id);
create index idx_detalles_orden_producto_id on content.detalles_orden(producto_id);