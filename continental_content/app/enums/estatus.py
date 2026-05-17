class EstatusEnum:
    """Constantes de estatus compatibles con el esquema existente de ContinentalApi.

    Nota: La DB usa Integer (1=ACTIVO, -1=INACTIVO), no un Enum str.
    Esta es una desviación justificada del DEVELOPMENT_STANDARDS estándar
    para mantener compatibilidad con el esquema de DB existente.
    """
    ACTIVO = 1
    INACTIVO = -1
