import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Configurar Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)


def upload_image_to_cloudinary(file_bytes: bytes, filename: str) -> str:
    """
    Sube una imagen a Cloudinary y retorna la URL pública.
    
    Args:
        file_bytes: Contenido del archivo en bytes
        filename: Nombre del archivo original
        
    Returns:
        URL pública de la imagen en Cloudinary
        
    Raises:
        Exception: Si falla la carga a Cloudinary
    """
    try:
        # Crear un archivo temporal en memoria
        from io import BytesIO
        file_stream = BytesIO(file_bytes)
        
        # Subir a Cloudinary
        result = cloudinary.uploader.upload(
            file_stream,
            public_id=filename.split('.')[0],  # Nombre sin extensión
            folder="proyecto-hashart/imagenes",  # Carpeta en Cloudinary
            overwrite=True  # Sobreescribir si existe
        )
        
        # Retornar la URL segura
        return result.get("secure_url")
        
    except Exception as e:
        raise Exception(f"Error al subir imagen a Cloudinary: {str(e)}")


def get_cloudinary_url_by_public_id(public_id: str) -> str:
    """
    Construye la URL de Cloudinary a partir del public_id.
    
    Args:
        public_id: ID público del recurso en Cloudinary
        
    Returns:
        URL segura de Cloudinary
    """
    return cloudinary.CloudinaryResource(
        public_id=public_id,
        type="upload",
        resource_type="image"
    ).build_url(secure=True)


def delete_image_from_cloudinary(public_id: str) -> bool:
    """
    Elimina una imagen de Cloudinary.
    
    Args:
        public_id: ID público del recurso en Cloudinary
        
    Returns:
        True si se eliminó correctamente, False en caso contrario
    """
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result.get("result") == "ok"
    except Exception as e:
        print(f"Error al eliminar imagen de Cloudinary: {str(e)}")
        return False
