import React, { useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { API_ENDPOINTS } from "./config";

export default function UploadForm() {
  const [filePDF, setFilePDF] = useState(null);
  const [loading, setLoading] = useState(false);
  const [downloadSuccess, setDownloadSuccess] = useState(false);
  const [validationError, setValidationError] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!filePDF) {
      setValidationError("Seleccione un PDF para continuar");
      setTimeout(() => setValidationError(null), 4000);
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("pdf", filePDF);

    try {
      const response = await fetch(API_ENDPOINTS.REGISTRAR_PDF, {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `documento_${filePDF.name.split(".")[0]}.zip`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        setDownloadSuccess(true);
        setTimeout(() => setDownloadSuccess(false), 8000);
        setFilePDF(null);
      } else {
        const err = await response.json();
        setValidationError(err.error || "Error al procesar el archivo");
        setTimeout(() => setValidationError(null), 4000);
      }
    } catch (error) {
      setValidationError("Error de conexión con el servidor");
      setTimeout(() => setValidationError(null), 4000);
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-b from-black to-orange-900">
      {/* Mensaje de validación */}
      {validationError && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0 }}
          className="bg-red-600 text-white p-4 text-center text-sm font-semibold"
        >
          ⚠ {validationError}
        </motion.div>
      )}

      {/* Mensaje de éxito */}
      {downloadSuccess && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0 }}
          className="bg-green-600 text-white p-4 text-center text-sm font-semibold"
        >
          ✓ ZIP descargado correctamente. Contiene: PDF con QR + Imagen Salt (IMPORTANTE para verificación)
        </motion.div>
      )}

      {/* Contenido principal */}
      <div className="flex-1 flex flex-col justify-center items-center px-4">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="bg-white/95 shadow-2xl rounded-2xl p-8 w-full max-w-md"
        >
          {/* Título principal */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-orange-600 mb-6 leading-tight">
              Proyecto Hashart
            </h1>
            <h2 className="text-xl font-semibold text-gray-800">
              Certificar Documento
            </h2>
            <p className="text-gray-600 text-sm mt-1">
              Suba un PDF para obtener un certificado de autenticidad.
            </p>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block mb-2 font-semibold text-gray-700">
                Seleccione un PDF
              </label>
              <input
                type="file"
                accept="application/pdf"
                onChange={(e) => setFilePDF(e.target.files[0])}
                className="border border-gray-300 rounded-lg w-full p-2 focus:outline-none focus:ring-2 focus:ring-orange-500"
              />
              {filePDF && (
                <p className="text-xs text-green-600 mt-1">
                  ✓ {filePDF.name}
                </p>
              )}
            </div>

            {/* Texto institucional */}
            <div className="text-center text-sm text-gray-600 italic leading-snug">
              Proyecto de tesis — Universidad de San Buenaventura 2025-2
              <br />
              Realizado por <span className="font-semibold">Juan Campo</span> y{" "}
              <span className="font-semibold">Juan Lara</span>
            </div>

            <button
              type="submit"
              disabled={loading}
              className={`w-full py-3 rounded-lg font-medium transition-all ${
                loading
                  ? "bg-gray-300 cursor-not-allowed text-gray-700"
                  : "bg-orange-600 text-white hover:bg-orange-700 active:scale-[0.98]"
              }`}
            >
              {loading ? "Procesando..." : "Certificar PDF"}
            </button>
          </form>
        </motion.div>
      </div>

      {/* Banda inferior con botón de verificación */}
      <div className="bg-white text-black text-center py-3 shadow-inner font-semibold text-lg">
        <button
          onClick={() => navigate("/verify")}
          className="hover:underline text-orange-600 hover:text-orange-700"
        >
          Ir a Verificar Documento
        </button>
      </div>
    </div>
  );
}
