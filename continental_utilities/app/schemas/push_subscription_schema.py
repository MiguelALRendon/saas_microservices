from .base_schema import BaseSchema


class PushSubscriptionSchema(BaseSchema):

    @staticmethod
    def serialize(sub):
        data = BaseSchema.serialize_concept_base(sub)
        data.update({
            'endpoint': sub.endpoint,
            'p256dh': sub.p256dh,
            'auth': sub.auth,
            'user_agent': sub.user_agent,
            'last_used': sub.last_used.isoformat() if sub.last_used else None,
        })
        return data

    @staticmethod
    def serialize_list(subs):
        return [PushSubscriptionSchema.serialize(s) for s in subs]

    @staticmethod
    def validate_create(data):
        errors = []
        for field in ['endpoint', 'p256dh', 'auth']:
            if not data.get(field):
                errors.append(f'{field} es requerido')
        return errors

    @staticmethod
    def validate_update(data):
        return []
