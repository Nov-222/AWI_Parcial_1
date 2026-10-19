-- =============================================================================
-- SCRIPT DML: POBLAMIENTO MASIVO DE DATOS DE PRUEBA (10,000 REGISTROS POR TABLA)
-- =============================================================================

begin;

-- 1. insertar 10,000 categorías (categoria_1, categoria_2, ...)
insert into content.categoria (nombre, descripcion, eliminado)
select 
    'categoria_' || g,
    'descripción para categoria_' || g,
    0
from generate_series(1, 10000) as g;

-- 2. insertar 10,000 usuarios (usuario_1, usuario_2, ...)
insert into content.usuario (nombre, apellido_paterno, apellido_materno, email, contrasena, rol, numero_telefono, nit, eliminado)
select 
    'usuario_' || g,
    'paterno_' || g,
    'materno_' || g,
    'usuario_' || g || '@restaurante.com',
    'pass_hash_' || g,
    'cliente',
    '7' || lpad(g::text, 7, '0'),
    (1000000 + g)::text,
    0
from generate_series(1, 10000) as g;

-- 3. insertar 10,000 productos asignados a sus respectivas categorías
insert into content.producto (nombre, descripcion, precio, categoria_id, estado, eliminado)
select 
    'producto_' || g,
    'descripción del producto_' || g,
    floor(random() * (100 - 5 + 1) + 5)::int, -- precio entre 5 y 100
    cat.id,
    'activo',
    0
from generate_series(1, 10000) as g
cross join lateral (
    select id from content.categoria where nombre = 'categoria_' || g
) cat;

-- 4. insertar 10,000 órdenes asociadas a cada usuario
insert into content.orden (usuario_id, tipo_solicitud, fecha_solicitud, eliminado)
select 
    u.id,
    (array['para_llevar', 'comer_aqui'])[floor(random() * 2 + 1)],
    current_timestamp - (random() * 730 || ' days')::interval, -- distribuidas en los últimos 2 años
    0
from generate_series(1, 10000) as g
cross join lateral (
    select id from content.usuario where email = 'usuario_' || g || '@restaurante.com'
) u;

-- 5. insertar 10,000 detalles de orden asociando cada orden con su producto correspondiente
insert into content.detalles_orden (orden_id, producto_id, cantidad)
select 
    o.id,
    p.id,
    floor(random() * 5 + 1)::int -- cantidad aleatoria entre 1 y 5
from generate_series(1, 10000) as g
cross join lateral (
    select id from content.orden offset (g - 1) limit 1
) o
cross join lateral (
    select id from content.producto offset (g - 1) limit 1
) p;

commit;