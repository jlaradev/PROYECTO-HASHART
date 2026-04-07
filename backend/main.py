
from dotenv import load_dotenv
import os
import random
import requests
from io import BytesIO

from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import qrcode
from PIL import Image

from backend.utils import generate_pdf_hash
from backend.database import get_db, engine, Base
from backend import models, crud, schemas
from backend.routes import files as files_router
from backend.routes.files import get_pdf_sha256_hash, get_deterministic_salt, generate_sha256_hash, validate_pdf_file, validate_image_file
import tempfile
import pytz
import zipfile

# Cargar variables de entorno desde .env
load_dotenv()

# Crear aplicación FastAPI
app = FastAPI()

# Dominios permitidos para CORS desde variables de entorno
cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000")
origins = [origin.strip() for origin in cors_origins_str.split(",")]

# AGREGAR CORS MIDDLEWARE PRIMERO (antes de cualquier endpoint)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "PUT"],
    allow_headers=["*"],
)

# Función auxiliar para convertir timestamps a zona horaria de Bogotá
def to_bogota_time(dt):
    """Convierte datetime UTC a zona horaria de Bogotá (America/Bogota, UTC-5)"""
    if dt is None:
        return None
    bogota_tz = pytz.timezone("America/Bogota")
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    return dt.astimezone(bogota_tz)

# Función auxiliar para limpiar archivos temporales
def cleanup_temp_files(*paths):
    """Elimina archivos temporales de forma segura"""
    for path in paths:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass

# Endpoint raíz para health check
@app.get("/")
def health_check(db: Session = Depends(get_db)):
    try:
        # Intentar obtener la fecha del servidor de la BD para validar conexión
        from sqlalchemy import func, text
        db_time = db.execute(text("SELECT NOW()")).scalar()
        db_status = "connected"
        db_date = str(to_bogota_time(db_time)) if db_time else None
    except Exception as e:
        db_status = "error"
        db_date = None
        print(f"Health check - DB error: {e}")
    
    return {
        "status": "ok",
        "database": {
            "status": db_status,
            "timestamp": db_date  # Ahora en zona horaria de Bogotá
        }
    }

# Montar carpeta estática si existe
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Servir favicon
@app.get("/favicon.ico")
def favicon():
    path = os.path.join(static_dir, "favicon.ico")
    if os.path.exists(path):
        return FileResponse(path, media_type="image/x-icon")
    return Response(status_code=204)

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

# Incluir rutas adicionales
app.include_router(files_router.router)


@app.post("/registrar_pdf/")
async def registrar_pdf(pdf: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        # Leer PDF y validar
        pdf_bytes = await pdf.read()
        is_valid, error_msg = validate_pdf_file(pdf.content_type or "", len(pdf_bytes))
        if not is_valid:
            return JSONResponse(content={"error": error_msg}, status_code=400)
        
        pdf_path = None
        image_path = None
        
        try:
            # Escribir PDF en temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as pdf_tmp:
                pdf_tmp.write(pdf_bytes)
                pdf_path = pdf_tmp.name

            # Calcular hash del PDF
            pdf_hash = get_pdf_sha256_hash(pdf_path)

            # Obtener imagen aleatoria de la BD
            imagenes = crud.listar_imagenes(db)
            if not imagenes:
                return JSONResponse(content={"error": "No hay imágenes en la base de datos"}, status_code=500)
            imagen = random.choice(imagenes)
            imagen_asociada_nombre = imagen.nombre
            imagen_asociada_url = imagen.url
            
            # Validar que URL sea HTTPS y no apunte a redes internas (prevenir SSRF)
            if not imagen_asociada_url.startswith("https://"):
                print(f"Advertencia: URL de imagen no es HTTPS: {imagen_asociada_url}")
                return JSONResponse(content={"error": "URL de imagen debe ser HTTPS"}, status_code=500)
            
            # Rechazar direcciones locales/privadas
            suspicious_hosts = ["localhost", "127.0.0.1", "0.0.0.0", "169.254", "10.", "172.16", "192.168"]
            if any(host in imagen_asociada_url for host in suspicious_hosts):
                print(f"Advertencia: URL de imagen sospechosa: {imagen_asociada_url}")
                return JSONResponse(content={"error": "URL de imagen no válida"}, status_code=500)
            
            # Descargar imagen desde Cloudinary
            try:
                imagen_response = requests.get(imagen_asociada_url, timeout=10)
                imagen_response.raise_for_status()
                imagen_asociada_bytes = imagen_response.content
            except Exception as e:
                print(f"Advertencia: No se pudo descargar imagen de {imagen_asociada_url}: {e}")
                return JSONResponse(content={"error": f"No se pudo descargar imagen: {str(e)}"}, status_code=500)

            # Guardar imagen en temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as img_tmp:
                img_tmp.write(imagen_asociada_bytes)
                image_path = img_tmp.name

            # Extraer salt de la imagen
            salt = get_deterministic_salt(image_path)
            
            # Calcular hash final
            combined_data = pdf_hash + salt
            hash_final = generate_sha256_hash(combined_data)
            
            # Guardar en BD con todos los datos
            documento_create = schemas.DocumentoCreate(
                nombre=pdf.filename,
                hash_pdf=pdf_hash,
                imagen_id=imagen.id,
                hash_final=hash_final
            )
            crud.crear_documento(db, documento_create)

            # Generar PDF con QR (igual que el original /registrar_pdf)
            verification_url = f"https://proyectohashart-front-production.up.railway.app/upload?hash={pdf_hash}"
            qr = qrcode.QRCode(box_size=6, border=2)
            qr.add_data(verification_url)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")

            # Crear PDF que contiene solo la página con el QR y la imagen
            output_pdf = BytesIO()
            width, height = letter
            c = canvas.Canvas(output_pdf, pagesize=letter)

            top_margin = height - inch
            c.setFont("Helvetica-Bold", 22)
            c.drawCentredString(width / 2, top_margin, "PROYECTO HASHART")

            c.setFont("Helvetica", 14)
            c.drawCentredString(width / 2, top_margin - 30, "Escanea este código QR para verificar tu documento")

            # QR centrado
            qr_size = 200
            qr_x = width / 2 - qr_size / 2
            qr_y = height / 2 - qr_size / 2 + 100
            qr_buffer = BytesIO()
            qr_img.save(qr_buffer, format="PNG")
            qr_buffer.seek(0)
            c.drawInlineImage(Image.open(qr_buffer), qr_x, qr_y, width=qr_size, height=qr_size)

            # Imagen asociada debajo del QR (si se descargó correctamente)
            if imagen_asociada_bytes:
                try:
                    pil_imagen = Image.open(BytesIO(imagen_asociada_bytes))
                    pil_imagen.thumbnail((200, 200))
                    img_x = width / 2 - pil_imagen.width / 2
                    img_y = qr_y - pil_imagen.height - 40
                    c.drawInlineImage(pil_imagen, img_x, img_y, width=pil_imagen.width, height=pil_imagen.height)
                except Exception as e:
                    print(f"Advertencia: No se pudo dibujar imagen: {e}")

            # Pie de página
            c.setFont("Helvetica-Oblique", 10)
            c.drawCentredString(width / 2, 40, "Proyecto de tesis de la Universidad de San Buenaventura")
            c.drawCentredString(width / 2, 25, "Creado por Juan Campo & Juan Lara")

            c.showPage()
            c.save()

            output_pdf.seek(0)

            # Crear ZIP con PDF + Imagen
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Agregar PDF al ZIP
                pdf_filename = f"QR_{pdf.filename}"
                zip_file.writestr(pdf_filename, output_pdf.getvalue())
                
                # Agregar imagen al ZIP (asegurar extensión .png)
                nombre_sin_ext = imagen.nombre.rsplit('.', 1)[0] if '.' in imagen.nombre else imagen.nombre
                imagen_filename = f"salt_source_{nombre_sin_ext}.png"
                zip_file.writestr(imagen_filename, imagen_asociada_bytes)
            
            zip_buffer.seek(0)

            return StreamingResponse(
                zip_buffer,
                media_type="application/zip",
                headers={"Content-Disposition": f"attachment; filename=documento_{pdf.filename.split('.')[0]}.zip"}
            )

        except Exception as e:
            # Limpiar archivos temporales en caso de error
            cleanup_temp_files(pdf_path, image_path)
            print(f"Error en registrar_pdf: {e}")
            return JSONResponse(content={"error": str(e)}, status_code=500)

    except Exception as e:
        print(f"Error en registrar_pdf: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/verificar_pdf/")
async def verificar_pdf(pdf: UploadFile = File(...), imagen: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        # Leer y validar PDF
        pdf_bytes = await pdf.read()
        is_valid, error_msg = validate_pdf_file(pdf.content_type or "", len(pdf_bytes))
        if not is_valid:
            return JSONResponse(content={"error": error_msg}, status_code=400)
        
        # Leer y validar imagen
        imagen_bytes = await imagen.read()
        is_valid, error_msg = validate_image_file(imagen.filename or "image", imagen.content_type or "", len(imagen_bytes))
        if not is_valid:
            return JSONResponse(content={"error": error_msg}, status_code=400)
        
        pdf_path = None
        imagen_path = None
        try:
            # Escribir PDF en temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as pdf_tmp:
                pdf_tmp.write(pdf_bytes)
                pdf_path = pdf_tmp.name

            # Escribir imagen en temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as img_tmp:
                img_tmp.write(imagen_bytes)
                imagen_path = img_tmp.name

            # Calcular hash del PDF subido
            pdf_hash = get_pdf_sha256_hash(pdf_path)

            # Extraer salt de la imagen subida
            salt_subido = get_deterministic_salt(imagen_path)

            # Buscar documento por hash_pdf
            documento = crud.obtener_documento_por_hash(db, pdf_hash)

            if not documento:
                resultado = False
                hash_final_guardado = None
            else:
                # Recalcular hash_final usando salt extraído de imagen subida
                hash_final_guardado = documento.hash_final
                combined_data = pdf_hash + salt_subido
                hash_final_calculado = generate_sha256_hash(combined_data)
                resultado = (hash_final_calculado == hash_final_guardado)

            # Guardar verificación si documento existe
            if documento:
                verificacion_create = schemas.VerificacionCreate(
                    documento_id=documento.id,
                    resultado=resultado
                )
                crud.crear_verificacion(db, verificacion_create)

            return JSONResponse(content={
                "hash": pdf_hash,
                "valido": resultado
            })

        except Exception as e:
            # Limpiar archivos temporales en caso de error
            cleanup_temp_files(pdf_path, imagen_path)
            print(f"Error en verificar_pdf: {e}")
            return JSONResponse(content={"error": str(e)}, status_code=500)

    except Exception as e:
        print(f"Error en verificar_pdf: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)
    