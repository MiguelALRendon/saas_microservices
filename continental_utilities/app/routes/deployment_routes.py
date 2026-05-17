import os
import stat
import subprocess
from flask import Blueprint, jsonify

deployment_bp = Blueprint('deployment', __name__, url_prefix='/deployment')

SCRIPT_PATH = '/var/www/reload_continental_page.sh'
BASH_PATH = '/bin/bash'


@deployment_bp.route('/reload-continental-page', methods=['POST'])
def reload_continental_page():
    """Ejecuta el script de deployment de ContinentalPage."""
    try:
        if not os.path.exists(BASH_PATH):
            return jsonify({
                'errors': ['Bash no encontrado en el sistema'],
                'error_step': 'BASH_NOT_FOUND',
            }), 500

        if not os.path.exists(SCRIPT_PATH):
            return jsonify({
                'errors': ['Script de deployment no encontrado'],
                'error_step': 'FILE_NOT_FOUND',
            }), 500

        file_stat = os.stat(SCRIPT_PATH)
        if not os.access(SCRIPT_PATH, os.R_OK):
            return jsonify({
                'errors': ['Sin permisos para leer el script'],
                'error_step': 'PERMISSION_DENIED',
            }), 500

        env = os.environ.copy()
        env['PATH'] = '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
        env['HOME'] = '/root'
        env['GIT_TERMINAL_PROMPT'] = '0'
        env['GIT_SSH_COMMAND'] = 'ssh -o StrictHostKeyChecking=no'

        result = subprocess.run(
            [BASH_PATH, SCRIPT_PATH],
            capture_output=True,
            text=True,
            timeout=600,
            cwd='/var/www',
            env=env,
        )

        output = result.stdout
        error_output = result.stderr

        if result.returncode == 0 and 'SUCCESS: DEPLOY COMPLETADO' in output:
            steps_completed = [
                line.replace('SUCCESS: ', '').strip()
                for line in output.split('\n')
                if line.startswith('SUCCESS:')
            ]
            return jsonify({
                'message': 'Deployment completado exitosamente',
                'success': True,
                'output': output,
                'steps_completed': steps_completed,
            }), 200
        else:
            return jsonify({
                'errors': ['El script no completó correctamente'],
                'success': False,
                'output': output,
                'error_output': error_output,
                'return_code': result.returncode,
            }), 500

    except subprocess.TimeoutExpired:
        return jsonify({'errors': ['El script excedió el tiempo límite (10 min)']}), 504
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500
