import os
import re
from PIL import Image
from werkzeug.utils import secure_filename


class ImageProcessor:
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
    MAX_SIZE = 5 * 1024 * 1024  # 5 MB

    @staticmethod
    def sanitizar_nombre(nombre: str) -> str:
        nombre_sin_ext = os.path.splitext(nombre)[0]
        nombre_limpio = nombre_sin_ext.lower().strip()
        nombre_limpio = re.sub(r'\s+', '-', nombre_limpio)
        nombre_limpio = re.sub(r'[^a-z0-9\-_]', '', nombre_limpio)
        nombre_limpio = re.sub(r'-+', '-', nombre_limpio)
        nombre_limpio = nombre_limpio.strip('-')
        return nombre_limpio if nombre_limpio else 'imagen'

    @staticmethod
    def validar_extension(filename: str) -> bool:
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ImageProcessor.ALLOWED_EXTENSIONS

    @staticmethod
    def obtener_extension(filename: str) -> str:
        ext = filename.rsplit('.', 1)[1].lower()
        return 'jpg' if ext == 'jpeg' else ext

    @staticmethod
    def optimizar_imagen(ruta_archivo: str, calidad: int = 85) -> None:
        try:
            with Image.open(ruta_archivo) as img:
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                img.save(ruta_archivo, optimize=True, quality=calidad)
        except Exception:
            raise ValueError('Error al procesar el archivo de imagen')

    @staticmethod
    def generar_nombre_unico(nombre_base: str, extension: str, upload_folder: str) -> str:
        nombre_archivo = f"{nombre_base}.{extension}"
        ruta_completa = os.path.join(upload_folder, nombre_archivo)

        if not os.path.exists(ruta_completa):
            return nombre_archivo

        contador = 1
        while True:
            nombre_archivo = f"{nombre_base}-{contador}.{extension}"
            ruta_completa = os.path.join(upload_folder, nombre_archivo)
            if not os.path.exists(ruta_completa):
                return nombre_archivo
            contador += 1
