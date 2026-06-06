import requests
from flask import request, jsonify, Response
from config import Config


def _internal_headers() -> dict:
    """Cabeceras de autenticación inter-servicio requeridas por TrustedServiceMiddleware."""
    return {'X-Internal-Service-Secret': Config.INTERNAL_SERVICE_SECRET}


def _proxy(base_url: str, path: str, json_data=None):
    """Reenvía la petición actual al microservicio dueño con la cabecera interna."""
    url = f'{base_url}{path}'
    kwargs = {
        'headers': _internal_headers(),
        'params': request.args.to_dict(),
        'timeout': 30,
    }
    if json_data is not None:
        kwargs['json'] = json_data

    try:
        resp = requests.request(request.method, url, **kwargs)
        return Response(
            resp.content,
            status=resp.status_code,
            content_type=resp.headers.get('Content-Type', 'application/json'),
        )
    except requests.exceptions.ConnectionError:
        return jsonify({'errors': ['Microservicio no disponible']}), 503
    except requests.exceptions.Timeout:
        return jsonify({'errors': ['El microservicio tardó demasiado en responder']}), 504
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


def proxy_to_auth(path: str, json_data=None):
    return _proxy(Config.AUTH_SERVICE_URL, path, json_data=json_data)


def proxy_to_catalogues(path: str, json_data=None):
    return _proxy(Config.CATALOGUES_SERVICE_URL, path, json_data=json_data)


def proxy_to_branch(path: str, json_data=None):
    return _proxy(Config.BRANCH_SERVICE_URL, path, json_data=json_data)
