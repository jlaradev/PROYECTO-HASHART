
from dotenv import load_dotenv
import os
import random
import requests
from io import BytesIO

from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
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

# Cargar variables de entorno desde .env
load_dotenv()

# Crear aplicación FastAPI
app = FastAPI()

# Endpoint raíz para health check
@app.get("/")
def health_check():
    return {"status": "ok"}

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

# Dominios permitidos para CORS
origins = [
    "http://localhost:3000",
    "https://proyectohashart-front-production.up.railway.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

# Incluir rutas adicionales
app.include_router(files_router.router)


@app.post("/registrar_pdf/")
async def registrar_pdf(pdf: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        # Leer PDF y validar
        pdf_bytes = await pdf.read()
        
        # Validar MIME type y tamaño
        if pdf.content_type not in ("application/pdf", "application/x-pdf"):
            return JSONResponse(content={"error": f"No es un PDF válido: {pdf.content_type}"}, status_code=400)
        if len(pdf_bytes) > 50 * 1024 * 1024:  # 50MB
            return JSONResponse(content={"error": "PDF muy grande (máx 50MB)"}, status_code=400)
        
        pdf_hash = generate_pdf_hash(pdf_bytes)

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
            imagen_asociada_bytes = None

        # Guardar en tabla documentos
        documento_create = schemas.DocumentoCreate(
            nombre=pdf.filename,
            hash_pdf=pdf_hash,
            imagen_asociada=imagen_asociada_nombre
        )
        crud.crear_documento(db, documento_create)

        # Generar QR con la URL hacia el frontend de Railway
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
                imagen = Image.open(BytesIO(imagen_asociada_bytes))
                imagen.thumbnail((200, 200))
                img_x = width / 2 - imagen.width / 2
                img_y = qr_y - imagen.height - 40
                c.drawInlineImage(imagen, img_x, img_y, width=imagen.width, height=imagen.height)
            except Exception as e:
                print(f"Advertencia: No se pudo dibujar imagen: {e}")

        # Pie de página
        c.setFont("Helvetica-Oblique", 10)
        c.drawCentredString(width / 2, 40, "Proyecto de tesis de la Universidad de San Buenaventura")
        c.drawCentredString(width / 2, 25, "Creado por Juan Campo & Juan Lara")

        c.showPage()
        c.save()

        output_pdf.seek(0)

        return StreamingResponse(
            output_pdf,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=QR_{pdf.filename}"}
        )

    except Exception as e:
        print("Error en registrar_pdf:", e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/verificar_pdf/")
async def verificar_pdf(pdf: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        # Leer PDF y generar hash
        pdf_bytes = await pdf.read()
        pdf_hash = generate_pdf_hash(pdf_bytes)

        # Buscar el documento en la tabla 'documentos'
        documento = crud.obtener_documento_por_hash(db, pdf_hash)

        if documento:
            documento_id = documento.id
            resultado = True
        else:
            documento_id = None
            resultado = False

        # Guardar la verificación si el documento existe
        if documento_id:
            verificacion_create = schemas.VerificacionCreate(
                documento_id=documento_id,
                resultado=resultado
            )
            crud.crear_verificacion(db, verificacion_create)

        return JSONResponse(content={"hash": pdf_hash, "valido": resultado})

    except Exception as e:
        print("Error en verificar_pdf:", e)
        return JSONResponse(content={"error": str(e)}, status_code=500)
    