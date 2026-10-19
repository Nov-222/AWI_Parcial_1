from flask import Blueprint, jsonify, request, abort
from .extensions import db
from .models import Categoria, Usuario, Producto, Orden, DetallesOrden

api_bp = Blueprint('api', __name__)

# --- SALUD ---
@api_bp.get('/health')
def salud():
    return jsonify({
        'status': 'ok',
        'usuarios_registrados': Usuario.query.filter_by(eliminado=0).count(),
        'productos_registrados': Producto.query.filter_by(eliminado=0).count()
    }), 200

# --- CATEGORÍAS ---
@api_bp.get('/categorias')
def listar_categorias():
    consulta = Categoria.query.filter_by(eliminado=0)
    categorias = consulta.order_by(Categoria.nombre).all()
    return jsonify({
        'success': True,
        'total': len(categorias),
        'categorias': [c.format() for c in categorias]
    }), 200

@api_bp.get('/categorias/<uuid:categoria_id>')
def obtener_categoria(categoria_id):
    cat = Categoria.query.filter_by(id=categoria_id, eliminado=0).first_or_404()
    return jsonify({'success': True, 'categoria': cat.format()}), 200

# --- PRODUCTOS ---
@api_bp.get('/productos')
def listar_productos():
    consulta = Producto.query.filter_by(eliminado=0)
    nombre = request.args.get('nombre')
    if nombre:
        consulta = consulta.filter(Producto.nombre.ilike(f'%{nombre}%'))
    
    productos = consulta.order_by(Producto.nombre).all()
    return jsonify({
        'success': True,
        'total': len(productos),
        'productos': [p.format() for p in productos]
    }), 200

@api_bp.get('/productos/<uuid:producto_id>')
def obtener_producto(producto_id):
    prod = Producto.query.filter_by(id=producto_id, eliminado=0).first_or_404()
    return jsonify({'success': True, 'producto': prod.format()}), 200

@api_bp.post('/productos')
def crear_producto():
    cuerpo = request.get_json(silent=True) or request.form
    if not cuerpo:
        return jsonify({'success': False, 'mensaje': 'Sin datos de entrada'}), 400

    nombre = cuerpo.get('nombre')
    precio = cuerpo.get('precio')
    categoria_id = cuerpo.get('categoria_id')

    if not nombre or precio is None or not categoria_id:
        return jsonify({'success': False, 'mensaje': 'Campos obligatorios: nombre, precio, categoria_id'}), 422

    try:
        nuevo_producto = Producto(
            nombre=nombre,
            descripcion=cuerpo.get('descripcion'),
            precio=int(precio),
            categoria_id=categoria_id
        )
        db.session.add(nuevo_producto)
        db.session.commit()
        return jsonify({'success': True, 'producto': nuevo_producto.format()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@api_bp.put('/productos/<uuid:producto_id>')
def editar_producto(producto_id):
    prod = Producto.query.filter_by(id=producto_id, eliminado=0).first_or_404()
    cuerpo = request.get_json(silent=True) or request.form

    if 'nombre' in cuerpo: prod.nombre = cuerpo['nombre']
    if 'descripcion' in cuerpo: prod.descripcion = cuerpo['descripcion']
    if 'precio' in cuerpo: prod.precio = int(cuerpo['precio'])
    if 'estado' in cuerpo: prod.estado = cuerpo['estado']
    if 'categoria_id' in cuerpo: prod.categoria_id = cuerpo['categoria_id']

    try:
        db.session.commit()
        return jsonify({'success': True, 'producto': prod.format()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@api_bp.delete('/productos/<uuid:producto_id>')
def eliminar_producto(producto_id):
    prod = Producto.query.filter_by(id=producto_id, eliminado=0).first_or_404()
    try:
        prod.eliminado = 1  # Borrado lógico recomendado
        db.session.commit()
        return jsonify({'success': True, 'id_eliminado': str(producto_id)}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

# --- USUARIOS / PERSONAS ---
@api_bp.get('/usuarios')
def listar_usuarios():
    consulta = Usuario.query.filter_by(eliminado=0)
    nombre = request.args.get('nombre')
    if nombre:
        consulta = consulta.filter(Usuario.nombre.ilike(f'%{nombre}%'))
    usuarios = consulta.order_by(Usuario.nombre).all()
    return jsonify({
        'success': True,
        'total': len(usuarios),
        'usuarios': [u.format() for u in usuarios]
    }), 200

@api_bp.get('/usuarios/<uuid:usuario_id>')
def obtener_usuario(usuario_id):
    usr = Usuario.query.filter_by(id=usuario_id, eliminado=0).first_or_404()
    return jsonify({'success': True, 'usuario': usr.format()}), 200

@api_bp.post('/usuarios')
def crear_usuario():
    cuerpo = request.get_json(silent=True) or request.form
    if not cuerpo or not cuerpo.get('email') or not cuerpo.get('nombre'):
        return jsonify({'success': False, 'mensaje': 'Nombre y Email son requeridos'}), 422

    try:
        nuevo_usuario = Usuario(
            nombre=cuerpo.get('nombre'),
            apellido_paterno=cuerpo.get('apellido_paterno', ''),
            apellido_materno=cuerpo.get('apellido_materno', ''),
            email=cuerpo.get('email'),
            contrasena=cuerpo.get('contrasena', 'pass_hash_default'),
            numero_telefono=cuerpo.get('numero_telefono'),
            nit=cuerpo.get('nit')
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        return jsonify({'success': True, 'usuario': nuevo_usuario.format()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

# --- ÓRDENES DE RESTAURANTE ---
@api_bp.post('/ordenes')
def crear_orden():
    cuerpo = request.get_json(silent=True) or {}
    usuario_id = cuerpo.get('usuario_id')
    tipo_solicitud = cuerpo.get('tipo_solicitud', 'comer_aqui')
    detalles = cuerpo.get('detalles', [])  # Lista de dicts: [{"producto_id": "...", "cantidad": 2}]

    if not usuario_id or not detalles:
        return jsonify({'success': False, 'mensaje': 'Se requiere usuario_id y al menos un detalle de producto'}), 422

    try:
        nueva_orden = Orden(usuario_id=usuario_id, tipo_solicitud=tipo_solicitud)
        db.session.add(nueva_orden)
        db.session.flush()  # Genera el ID de la orden sin hacer commit aún

        for item in detalles:
            detalle = DetallesOrden(
                orden_id=nueva_orden.id,
                producto_id=item['producto_id'],
                cantidad=item['cantidad']
            )
            db.session.add(detalle)

        db.session.commit()
        return jsonify({'success': True, 'orden': nueva_orden.format()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400