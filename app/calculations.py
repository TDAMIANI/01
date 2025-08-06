from datetime import date
from sqlalchemy import func
from . import db
from .models import Balance, Cuenta, Movimiento, IPC, Ajuste


def obtener_coeficiente(fecha_desde: date, fecha_hasta: date) -> float:
    """Calcula el coeficiente IPC entre dos fechas (mes/año)."""
    inicio = db.session.query(IPC).filter_by(anio=fecha_desde.year, mes=fecha_desde.month).first()
    fin = db.session.query(IPC).filter_by(anio=fecha_hasta.year, mes=fecha_hasta.month).first()
    if not inicio or not fin:
        raise ValueError('IPC faltante para el período solicitado')
    return fin.indice / inicio.indice


def calcular_ajuste_estatico(balance: Balance) -> float:
    activos = db.session.query(func.sum(Cuenta.monto_historico)).filter_by(balance_id=balance.id, categoria='activo', es_computable=True).scalar() or 0
    pasivos = db.session.query(func.sum(Cuenta.monto_historico)).filter_by(balance_id=balance.id, categoria='pasivo', es_computable=True).scalar() or 0
    coef = obtener_coeficiente(date(balance.ejercicio, 1, 1), date(balance.ejercicio, 12, 1))
    return (activos - pasivos) * (coef - 1)


def calcular_ajuste_dinamico(balance: Balance) -> float:
    total = 0.0
    cierre = date(balance.ejercicio, 12, 1)
    movimientos = Movimiento.query.filter_by(balance_id=balance.id).all()
    for mov in movimientos:
        coef = obtener_coeficiente(mov.fecha, cierre)
        total += mov.importe_historico * (coef - 1)
    return total


def calcular_ajuste_final(balance_id: int) -> Ajuste:
    balance = Balance.query.get(balance_id)
    if not balance:
        raise ValueError('Balance inexistente')
    estatico = calcular_ajuste_estatico(balance)
    dinamico = calcular_ajuste_dinamico(balance)
    ajuste = Ajuste.query.filter_by(balance_id=balance.id).first()
    if not ajuste:
        ajuste = Ajuste(balance_id=balance.id)
        db.session.add(ajuste)
    ajuste.ajuste_estatico = estatico
    ajuste.ajuste_dinamico = dinamico
    ajuste.resultado_final = estatico + dinamico
    db.session.commit()
    return ajuste
