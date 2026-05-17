from app import create_app, db
from config import Config

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Crear tablas si no existen
        db.create_all()
    
    # Usar variables de entorno para configuración del servidor
    app.run(
        debug=Config.DEBUG,
        host=Config.HOST,
        port=Config.PORT
    )
