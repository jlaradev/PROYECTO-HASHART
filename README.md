# PROYECTO-HASHART

Software developed as part of a thesis on document verification systems. The implementation uses AI-generated images to strengthen file integrity verification against hash-based attacks. Provides secure PDF registration with SHA256 hashing, image-based salt extraction, and complete verification workflow — designed for certificate and document authentication use cases.

For full thesis details, see [Biblioteca Digital USB](https://bibliotecadigital.usb.edu.co/entities/publication/01afe63d-2cfc-45f7-8cd4-f83a4a1a00ef).

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Cloudinary](https://img.shields.io/badge/Cloudinary-CDN-4A90E2?style=flat-square&logo=cloudinary&logoColor=white)](https://cloudinary.com/)

---

## Overview

PROYECTO-HASHART is a full-stack application for secure document registration and verification. Users upload a PDF document for certification. The system generates a reference image from the PDF and extracts unique characteristics for verification. Later, users verify document authenticity by uploading the same PDF and reference image — the system recalculates the verification hash to confirm the document integrity.

| | |
|---|---|
| **Frontend** | https://proyecto-hashart.vercel.app/ |
| **Backend** | https://proyecto-hashart.onrender.com/ |

---

## Tech Stack

| Technology | Role | Why |
|---|---|---|
| **FastAPI** | Backend framework | Modern async Python framework with automatic API documentation, built-in validation via Pydantic, and excellent performance for I/O-bound operations like file processing. |
| **React 18** | Frontend framework | Component-based UI with hooks, streamlined state management, and excellent support for file upload workflows and image preview. |
| **PostgreSQL** | Database | ACID-compliant relational database to store document metadata, verification records, and maintain referential integrity between documents and their images. |
| **SQLAlchemy** | ORM | Declarative database layer avoiding raw SQL while maintaining query control; natural mapping of Python models to database tables. |
| **Cloudinary** | Image storage | Offloads binary file storage to a CDN, provides image optimization, and eliminates the need to store large files in the database. |
| **OpenCV** | Image processing | Extracts deterministic salt from image pixels using spatial sampling — the cryptographic foundation of document verification security. |
| **QRCode + PyZBar** | QR processing (optional) | Generates and decodes QR codes as a convenience navigation method to reach the verification page; not required for security. |
| **ReportLab** | PDF generation | Generates PDFs and certificate overlays with precise control over layout. |
| **Pydantic** | Data validation | Automatic request/response validation and serialization; clear error messages for invalid inputs. |

---

## Features

**Document Registration**
- Upload PDF file for secure certification
- System generates a reference image from the PDF
- Extract and store unique characteristics for verification

**Verification Workflow**
- Upload PDF and system-generated reference image
- System performs cryptographic comparison against original certificate
- Returns verification result indicating document integrity
- Complete audit trail of all verification attempts

> **Note:** The implementation requires users to provide both the PDF and the associated reference image for verification. This approach strengthens security compared to the original design specification.

---

## Project Structure

```
PROYECTO-HASHART/
├── backend/
│   ├── main.py              FastAPI application and endpoints
│   ├── models.py            SQLAlchemy ORM models
│   ├── schemas.py           Pydantic request/response schemas
│   ├── database.py          Database connection and session management
│   ├── crud.py              Create, Read, Update operations
│   ├── utils.py             Utility functions (hashing, timezone)
│   ├── cloudinary_utils.py  Cloudinary integration helpers
│   ├── routes/
│   │   └── files.py         File upload and verification endpoints
│   ├── tests/               Pytest test suite
│   │   ├── test_health.py
│   │   ├── test_upload_image.py
│   │   ├── test_registrar_pdf.py
│   │   ├── test_verificar_pdf.py
│   │   ├── test_cloudinary.py
│   │   └── fixtures/
│   ├── requirements.txt     Python dependencies
│   └── Procfile             Deployment configuration
│
└── frontend/
    ├── package.json         Node.js dependencies
    ├── tailwind.config.js   Tailwind CSS configuration
    ├── postcss.config.js    PostCSS configuration
    ├── public/              Static assets
    └── src/
        ├── App.js           Main application routing
        ├── Home.js          Landing page with health status
        ├── UploadForm.js    PDF registration form
        ├── VerifyPage.js    Document verification interface
        ├── config.js        API configuration
        ├── index.js         React entry point
        └── *.css            Tailwind-based styling
```

---

## Domain Model

| Entity | Description |
|---|---|
| `Documento` | Registered PDF with name and cryptographic verification data |
| `Verificacion` | Audit record of verification attempt: result (match/no-match), timestamp, document reference |
| `Imagen` | Reference image stored in Cloudinary, used for document verification |

---

## Frontend Routes

| Path | Component | Description |
|---|---|---|
| `/` | `Home` | Landing page |
| `/upload` | `UploadForm` | PDF registration |
| `/verify` | `VerifyPage` | Document verification |

---

## API Reference

**Base URL:** Configured via environment variable `VITE_API_URL`

### Document Endpoints

<details>
<summary><strong>PDF Registration</strong></summary>

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/registrar_pdf` | Upload PDF for certification. Returns ZIP file containing QR PDF and reference image |

</details>

<details>
<summary><strong>Document Verification</strong></summary>

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/verificar_pdf` | Verify certificate authenticity by uploading PDF and reference image |

</details>



---

## Setup

**Requirements:** Python 3.10+ · Node.js 18+ · PostgreSQL 15+

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm install
npm start
```

---

## Testing

```bash
cd backend
pytest
```

---

## Authors

This project is the software implementation of a thesis developed by Juan Pablo Lara ([jlaradev](https://github.com/jlaradev)) and Juan Pablo Campo ([EzicTerrariuM](https://github.com/EzicTerrariuM)). 

**Original repositories:**
- Backend: https://github.com/EzicTerrariuM/PROYECTOHASHART
- Frontend: https://github.com/EzicTerrariuM/PROYECTOHASHART-FRONT

The current repository represents a refactored monorepo structure with implementation improvements, redeployed to maintain active access to the project.

---

## License

This project is not open-source. All rights reserved.