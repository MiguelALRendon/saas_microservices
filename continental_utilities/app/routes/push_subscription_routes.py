from datetime import datetime
from flask import Blueprint, request, jsonify
from app import db
from app.models.push_subscription import PushSubscription
from app.schemas.push_subscription_schema import PushSubscriptionSchema

push_subscription_bp = Blueprint('push_subscription', __name__, url_prefix='/push-subscription')


@push_subscription_bp.route('/<string:oid>', methods=['GET'])
def get_subscription(oid):
    try:
        sub = PushSubscription.query.filter(PushSubscription.id == oid).first()
        if not sub:
            return jsonify({'errors': ['Suscripción no encontrada']}), 404
        return jsonify(PushSubscriptionSchema.serialize(sub)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@push_subscription_bp.route('/', methods=['GET'])
def get_subscriptions():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        pagination = PushSubscription.query.paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            'data': PushSubscriptionSchema.serialize_list(pagination.items),
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages,
        }), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@push_subscription_bp.route('/', methods=['POST'])
def create_subscription():
    """Upsert por endpoint — no requiere auth (se llama desde el navegador del cliente)."""
    try:
        data = request.get_json()
        errors = PushSubscriptionSchema.validate_create(data)
        if errors:
            return jsonify({'errors': errors}), 400

        existing = PushSubscription.query.filter_by(endpoint=data['endpoint']).first()
        if existing:
            existing.p256dh = data['p256dh']
            existing.auth = data['auth']
            existing.user_agent = data.get('user_agent')
            existing.updated_at = datetime.now()
            db.session.commit()
            return jsonify(PushSubscriptionSchema.serialize(existing)), 200

        sub = PushSubscription(
            endpoint=data['endpoint'],
            p256dh=data['p256dh'],
            auth=data['auth'],
            user_agent=data.get('user_agent'),
        )
        db.session.add(sub)
        db.session.commit()
        return jsonify(PushSubscriptionSchema.serialize(sub)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@push_subscription_bp.route('/many', methods=['POST'])
def create_many_subscriptions():
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de suscripciones']}), 400

        created, errors = [], []
        for idx, item in enumerate(data):
            validation_errors = PushSubscriptionSchema.validate_create(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue
            existing = PushSubscription.query.filter_by(endpoint=item['endpoint']).first()
            if existing:
                existing.p256dh = item['p256dh']
                existing.auth = item['auth']
                existing.updated_at = datetime.now()
                created.append(existing)
                continue
            sub = PushSubscription(
                endpoint=item['endpoint'],
                p256dh=item['p256dh'],
                auth=item['auth'],
                user_agent=item.get('user_agent'),
            )
            db.session.add(sub)
            created.append(sub)

        db.session.commit()
        response = {'created': len(created), 'data': PushSubscriptionSchema.serialize_list(created)}
        if errors:
            response['errors'] = errors
        return jsonify(response), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@push_subscription_bp.route('/<string:oid>', methods=['PUT'])
def update_subscription(oid):
    try:
        sub = PushSubscription.query.filter(PushSubscription.id == oid).first()
        if not sub:
            return jsonify({'errors': ['Suscripción no encontrada']}), 404

        data = request.get_json()
        for field in ['endpoint', 'p256dh', 'auth', 'user_agent']:
            if field in data:
                setattr(sub, field, data[field])
        sub.updated_at = datetime.now()
        db.session.commit()
        return jsonify(PushSubscriptionSchema.serialize(sub)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@push_subscription_bp.route('/many', methods=['PUT'])
def update_many_subscriptions():
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de suscripciones']}), 400

        updated, errors = [], []
        for idx, item in enumerate(data):
            if 'id' not in item:
                errors.append({'index': idx, 'errors': ['id es requerido']})
                continue
            sub = PushSubscription.query.filter(PushSubscription.id == item['id']).first()
            if not sub:
                errors.append({'index': idx, 'errors': ['Suscripción no encontrada']})
                continue
            for field in ['endpoint', 'p256dh', 'auth', 'user_agent']:
                if field in item:
                    setattr(sub, field, item[field])
            sub.updated_at = datetime.now()
            updated.append(sub)

        if updated:
            db.session.commit()
        response = {'updated': len(updated), 'data': PushSubscriptionSchema.serialize_list(updated)}
        if errors:
            response['errors'] = errors
        return jsonify(response), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@push_subscription_bp.route('/<string:oid>', methods=['DELETE'])
def delete_subscription(oid):
    """Hard delete — PushSubscription usa ConceptBase."""
    try:
        sub = PushSubscription.query.filter(PushSubscription.id == oid).first()
        if not sub:
            return jsonify({'errors': ['Suscripción no encontrada']}), 404
        db.session.delete(sub)
        db.session.commit()
        return jsonify({'message': 'Suscripción eliminada exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@push_subscription_bp.route('/list', methods=['POST'])
def get_subscription_list():
    try:
        data = request.get_json()
        if not data or 'oid_list' not in data:
            return jsonify({'errors': ['oid_list es requerido']}), 400
        oid_list = data.get('oid_list', [])
        if not isinstance(oid_list, list):
            return jsonify({'errors': ['oid_list debe ser un arreglo']}), 400
        subs = PushSubscription.query.filter(PushSubscription.id.in_(oid_list)).all()
        return jsonify(PushSubscriptionSchema.serialize_list(subs)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500
