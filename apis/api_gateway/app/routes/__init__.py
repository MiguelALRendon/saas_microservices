def register_blueprints(app):
    from app.routes.auth_routes import auth_bp
    from app.routes.variable_sistema_routes import variable_sistema_bp
    from app.routes.obra_routes import obra_bp
    from app.routes.arco_routes import arco_bp
    from app.routes.capitulo_routes import capitulo_bp
    from app.routes.noticia_routes import noticia_bp
    from app.routes.nota_routes import nota_bp
    from app.routes.personaje_ficticio_routes import personaje_ficticio_bp
    from app.routes.fecha_routes import fecha_bp
    from app.routes.imagen_routes import imagen_bp
    from app.routes.push_subscription_routes import push_subscription_bp
    from app.routes.push_notification_routes import push_notification_bp
    from app.routes.deployment_routes import deployment_bp

    for bp in [
        auth_bp,
        variable_sistema_bp,
        obra_bp,
        arco_bp,
        capitulo_bp,
        noticia_bp,
        nota_bp,
        personaje_ficticio_bp,
        fecha_bp,
        imagen_bp,
        push_subscription_bp,
        push_notification_bp,
        deployment_bp,
    ]:
        app.register_blueprint(bp)
