from datetime import datetime, timezone
import uuid
from sqlalchemy.dialects.postgresql import UUID
from .extensions import db

class Categoria(db.Model):
    __tablename__ = 'categoria'
    __table_args__ = {'schema': 'content'}

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    eliminado = db.Column(db.SmallInteger, default=0, nullable=False)

    productos = db.relationship('Producto', backref='categoria', lazy=True)

    def __repr__(self):
        return f'<Categoria {self.nombre}>'

    def format(self):
        return {
            'id': str(self.id),
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'eliminado': self.eliminado
        }


class Usuario(db.Model):
    __tablename__ = 'usuario'
    __table_args__ = {'schema': 'content'}

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = db.Column(db.String(100), nullable=False)
    apellido_paterno = db.Column(db.String(100), nullable=False)
    apellido_materno = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    contrasena = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(50), default='cliente', nullable=False)
    numero_telefono = db.Column(db.String(20))
    nit = db.Column(db.String(20), unique=True)
    eliminado = db.Column(db.SmallInteger, default=0, nullable=False)

    ordenes = db.relationship('Orden', backref='usuario', lazy=True)

    def __repr__(self):
        return f'<Usuario {self.email}>'

    def format(self):
        return {
            'id': str(self.id),
            'nombre': self.nombre,
            'apellido_paterno': self.apellido_paterno,
            'apellido_materno': self.apellido_materno,
            'email': self.email,
            'rol': self.rol,
            'numero_telefono': self.numero_telefono,
            'nit': self.nit,
            'eliminado': self.eliminado
        }


class Producto(db.Model):
    __tablename__ = 'producto'
    __table_args__ = {'schema': 'content'}

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Integer, nullable=False)
    categoria_id = db.Column(UUID(as_uuid=True), db.ForeignKey('content.categoria.id'))
    estado = db.Column(db.String(50), default='activo', nullable=False)
    eliminado = db.Column(db.SmallInteger, default=0, nullable=False)

    detalles_orden = db.relationship('DetallesOrden', backref='producto', lazy=True)

    def __repr__(self):
        return f'<Producto {self.nombre}>'

    def format(self):
        return {
            'id': str(self.id),
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'precio': self.precio,
            'estado': self.estado,
            'categoria_id': str(self.categoria_id) if self.categoria_id else None,
            'eliminado': self.eliminado
        }


class Orden(db.Model):
    __tablename__ = 'orden'
    __table_args__ = {'schema': 'content'}

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = db.Column(UUID(as_uuid=True), db.ForeignKey('content.usuario.id'), nullable=False)
    tipo_solicitud = db.Column(db.String(50))
    fecha_solicitud = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    eliminado = db.Column(db.SmallInteger, default=0, nullable=False)

    detalles = db.relationship('DetallesOrden', backref='orden', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Orden {self.id}>'

    def format(self):
        return {
            'id': str(self.id),
            'usuario_id': str(self.usuario_id),
            'tipo_solicitud': self.tipo_solicitud,
            'fecha_solicitud': self.fecha_solicitud.isoformat() if self.fecha_solicitud else None,
            'eliminado': self.eliminado
        }


class DetallesOrden(db.Model):
    __tablename__ = 'detalles_orden'
    __table_args__ = {'schema': 'content'}

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    orden_id = db.Column(UUID(as_uuid=True), db.ForeignKey('content.orden.id'), nullable=False)
    producto_id = db.Column(UUID(as_uuid=True), db.ForeignKey('content.producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<DetallesOrden Orden:{self.orden_id} Producto:{self.producto_id}>'

    def format(self):
        return {
            'id': str(self.id),
            'orden_id': str(self.orden_id),
            'producto_id': str(self.producto_id),
            'cantidad': self.cantidad
        }