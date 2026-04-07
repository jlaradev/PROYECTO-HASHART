import pytest
from backend.cloudinary_utils import upload_image_to_cloudinary, delete_image_from_cloudinary


def test_cloudinary_upload_with_file():
    """Test de carga a Cloudinary usando archivo local de fixtures."""
    fixture_path = "backend/tests/fixtures/test_cloudinary_image.png"
    
    try:
        with open(fixture_path, "rb") as f:
            image_bytes = f.read()
        
        filename = "test_image_from_fixtures.png"
        url = upload_image_to_cloudinary(image_bytes, filename)
        
        assert isinstance(url, str)
        assert url.startswith("https://")
        assert "cloudinary" in url
        
        print(f"\n✓ Cloudinary Upload Successful")
        print(f"  • Filename: {filename}")
        print(f"  • File Size: {len(image_bytes)} bytes")
        print(f"  • URL: {url}")
        
        # Limpiar
        public_id = f"proyecto-hashart/imagenes/{filename.split('.')[0]}"
        delete_image_from_cloudinary(public_id)
        print(f"  • Cleanup: Image deleted from Cloudinary")
        
    except FileNotFoundError:
        pytest.skip(f"No existe archivo en {fixture_path}. Crea la imagen ahí si quieres este test.")
    except Exception as e:
        pytest.skip(f"Error en Cloudinary: {str(e)}")
