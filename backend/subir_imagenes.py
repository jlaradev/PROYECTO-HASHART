import os
from sqlalchemy.orm import Session
from backend import crud, schemas
from backend.database import SessionLocal

# Carpeta donde están las imágenes
IMAGES_DIR = r"C:\\Users\\fireb\\Downloads\\Outputs"

# Conexión a la base de datos
db: Session = SessionLocal()

# Iterar sobre los archivos de la carpeta

for filename in os.listdir(IMAGES_DIR):
	if filename.lower().endswith((".png", ".jpg", ".jpeg")):
		# En vez de subir la imagen, guardamos una URL de ejemplo
		url = f"https://ejemplo.com/imagenes/{filename}"
		imagen_db = schemas.ImagenCreate(
			nombre=filename,
			url=url
		)
		crud.crear_imagen(db, imagen_db)
		print(f"Imagen subida (como URL): {filename} -> {url}")

db.close()
print("¡Todas las imágenes se subieron correctamente!")
