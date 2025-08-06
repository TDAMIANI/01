from datetime import date
from . import db


class Empresa(db.Model):
    __tablename__ = 'empresas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(128), nullable=False)
    cuit = db.Column(db.String(20), unique=True, nullable=True)

    balances = db.relationship('Balance', backref='empresa', lazy=True)


class Balance(db.Model):
    __tablename__ = 'balances'
    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    ejercicio = db.Column(db.Integer, nullable=False)

    cuentas = db.relationship('Cuenta', backref='balance', lazy=True)
    movimientos = db.relationship('Movimiento', backref='balance', lazy=True)
    ajuste = db.relationship('Ajuste', backref='balance', uselist=False)


class Cuenta(db.Model):
    __tablename__ = 'cuentas'
    id = db.Column(db.Integer, primary_key=True)
    balance_id = db.Column(db.Integer, db.ForeignKey('balances.id'), nullable=False)
    nombre = db.Column(db.String(128), nullable=False)
    categoria = db.Column(db.String(20), nullable=False)  # activo/pasivo
    es_monetaria = db.Column(db.Boolean, default=True)
    es_computable = db.Column(db.Boolean, default=True)
    monto_historico = db.Column(db.Float, default=0.0)


class Movimiento(db.Model):
    __tablename__ = 'movimientos'
    id = db.Column(db.Integer, primary_key=True)
    balance_id = db.Column(db.Integer, db.ForeignKey('balances.id'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.Date, default=date.today)
    importe_historico = db.Column(db.Float, nullable=False)


class IPC(db.Model):
    __tablename__ = 'ipc'
    id = db.Column(db.Integer, primary_key=True)
    anio = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False)
    indice = db.Column(db.Float, nullable=False)

    __table_args__ = (db.UniqueConstraint('anio', 'mes', name='_anio_mes_uc'),)


class Ajuste(db.Model):
    __tablename__ = 'ajustes'
    id = db.Column(db.Integer, primary_key=True)
    balance_id = db.Column(db.Integer, db.ForeignKey('balances.id'), nullable=False)
    ajuste_estatico = db.Column(db.Float, default=0.0)
    ajuste_dinamico = db.Column(db.Float, default=0.0)
    resultado_final = db.Column(db.Float, default=0.0)
