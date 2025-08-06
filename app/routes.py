from flask import Blueprint, request, jsonify
from datetime import date
from . import db
from .models import Empresa, Balance, Cuenta, Movimiento, IPC
from .calculations import calcular_ajuste_final

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/empresas', methods=['POST'])
def crear_empresa():
    data = request.get_json()
    empresa = Empresa(nombre=data['nombre'], cuit=data.get('cuit'))
    db.session.add(empresa)
    db.session.commit()
    return jsonify({'id': empresa.id, 'nombre': empresa.nombre}), 201


@api_bp.route('/empresas', methods=['GET'])
def listar_empresas():
    empresas = Empresa.query.all()
    return jsonify([{'id': e.id, 'nombre': e.nombre} for e in empresas])


@api_bp.route('/ipc', methods=['POST'])
def cargar_ipc():
    data = request.get_json()
    registro = IPC(anio=data['anio'], mes=data['mes'], indice=data['indice'])
    db.session.add(registro)
    db.session.commit()
    return jsonify({'id': registro.id}), 201


@api_bp.route('/balances', methods=['POST'])
def crear_balance():
    data = request.get_json()
    balance = Balance(empresa_id=data['empresa_id'], ejercicio=data['ejercicio'])
    db.session.add(balance)
    db.session.commit()
    return jsonify({'id': balance.id}), 201


@api_bp.route('/cuentas', methods=['POST'])
def crear_cuenta():
    data = request.get_json()
    cuenta = Cuenta(
        balance_id=data['balance_id'],
        nombre=data['nombre'],
        categoria=data['categoria'],
        es_monetaria=data.get('es_monetaria', True),
        es_computable=data.get('es_computable', True),
        monto_historico=data.get('monto_historico', 0.0)
    )
    db.session.add(cuenta)
    db.session.commit()
    return jsonify({'id': cuenta.id}), 201


@api_bp.route('/movimientos', methods=['POST'])
def crear_movimiento():
    data = request.get_json()
    movimiento = Movimiento(
        balance_id=data['balance_id'],
        tipo=data['tipo'],
        fecha=date.fromisoformat(data['fecha']),
        importe_historico=data['importe_historico']
    )
    db.session.add(movimiento)
    db.session.commit()
    return jsonify({'id': movimiento.id}), 201


@api_bp.route('/ajustes/<int:balance_id>', methods=['GET'])
def obtener_ajuste(balance_id):
    ajuste = calcular_ajuste_final(balance_id)
    return jsonify({
        'balance_id': balance_id,
        'ajuste_estatico': ajuste.ajuste_estatico,
        'ajuste_dinamico': ajuste.ajuste_dinamico,
        'resultado_final': ajuste.resultado_final
    })
