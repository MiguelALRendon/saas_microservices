from app.routes.obra_routes import obra_bp
from app.routes.arco_routes import arco_bp
from app.routes.capitulo_routes import capitulo_bp
from app.routes.noticia_routes import noticia_bp
from app.routes.personaje_ficticio_routes import personaje_ficticio_bp
from app.routes.nota_routes import nota_bp
from app.routes.fecha_routes import fecha_bp
from app.routes.variable_sistema_routes import variable_sistema_bp

__all__ = [
    'obra_bp', 'arco_bp', 'capitulo_bp', 'noticia_bp',
    'personaje_ficticio_bp', 'nota_bp', 'fecha_bp', 'variable_sistema_bp',
]
