from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from ..database import get_db
from .. import crud, schemas
from ..cloudinary_utils import upload_image_to_cloudinary
import hashlib, tempfile, qrcode, cv2, os, uuid
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

router = APIRouter()

# Tipos MIME y límites permitidos
ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/gif", "image/webp"}
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_PDF_SIZE = 50 * 1024 * 1024    # 50MB

def validate_image_file(filename: str, content_type: str, file_size: int) -> tuple[bool, str]:
    """
    Valida que el archivo sea una imagen permitida.
    Retorna (es_válido, mensaje_error)
    """
    # Validar tamaño
    if file_size > MAX_IMAGE_SIZE:
        return False, f"Archivo muy grande. Máximo permitido: 10MB. Recibido: {file_size / 1024 / 1024:.2f}MB"
    
    # Validar extensión
    file_ext = os.path.splitext(filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return False, f"Formato no permitido: {file_ext}. Permitidos: {', '.join(ALLOWED_EXTENSIONS)}"
    
    # Validar MIME type
    if content_type not in ALLOWED_IMAGE_TYPES:
        return False, f"Tipo MIME no válido: {content_type}. Permitidos: {', '.join(ALLOWED_IMAGE_TYPES)}"
    
    return True, ""

def validate_pdf_file(content_type: str, file_size: int) -> tuple[bool, str]:
    """Valida que sea un PDF válido y no demasiado grande."""
    if content_type not in ("application/pdf", "application/x-pdf"):
        return False, f"Tipo MIME no es PDF: {content_type}"
    if file_size > MAX_PDF_SIZE:
        return False, f"PDF muy grande. Máximo: 50MB. Recibido: {file_size / 1024 / 1024:.2f}MB"
    return True, ""

def get_pdf_sha256_hash(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def get_deterministic_salt(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("No se pudo cargar la imagen.")
    height, width, _ = img.shape
    salt = ""
    step = max(width // 10, 1)
    for y in range(0, height, step):
        for x in range(0, width, step):
            pixel = img[y, x]
            salt += f"{pixel[0]:02x}{pixel[1]:02x}{pixel[2]:02x}"
    return salt

def generate_sha256_hash(data):
    sha256 = hashlib.sha256()
    sha256.update(data.encode())
    return sha256.hexdigest()


@router.get("/records")
def list_records(db: Session = Depends(get_db)):
    return crud.get_all_records(db)


@router.post("/upload-image")
async def upload_image(image: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Endpoint para subir una imagen a Cloudinary y guardarla en la BD.
    Solo acepta: PNG, JPG, JPEG, GIF, WEBP (máx 10MB)
    
    Args:
        image: Archivo de imagen
        db: Sesión de base de datos
        
    Returns:
        JSON con los datos de la imagen guardada en BD y su URL en Cloudinary
    """
    try:
        # Leer archivo de imagen
        image_bytes = await image.read()
        
        # Validar archivo
        is_valid, error_msg = validate_image_file(
            image.filename or "unknown",
            image.content_type or "application/octet-stream",
            len(image_bytes)
        )
        
        if not is_valid:
            return JSONResponse(
                content={"error": error_msg},
                status_code=400
            )
        
        # Subir a Cloudinary
        image_url = upload_image_to_cloudinary(image_bytes, image.filename)
        
        # Crear registro en BD
        imagen_create = schemas.ImagenCreate(
            nombre=image.filename,
            url=image_url
        )
        imagen_guardada = crud.crear_imagen(db, imagen_create)
        
        return {
            "id": imagen_guardada.id,
            "nombre": imagen_guardada.nombre,
            "url": imagen_guardada.url,
            "mensaje": "Imagen subida exitosamente a Cloudinary y guardada en BD"
        }
        
    except Exception as e:
        return JSONResponse(
            content={"error": f"Error al subir imagen: {str(e)}"}, 
            status_code=500
        )
