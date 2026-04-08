import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, XCircle, Loader2 } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { API_ENDPOINTS } from "./config";

export default function VerifyPage() {
  const [filePDF, setFilePDF] = useState(null);
  const [fileImage, setFileImage] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [validationError, setValidationError] = useState(null);
  const navigate = useNavigate();

  const handleVerify = async (e) => {
    e.preventDefault();
    
    // Validar que ambos archivos estén seleccionados
    if (!filePDF) {
      setValidationError("Seleccione un PDF para continuar");
      setTimeout(() => setValidationError(null), 4000);
      return;
    }
    
    if (!fileImage) {
      setValidationError("Seleccione la imagen salt para continuar");
      setTimeout(() => setValidationError(null), 4000);
      return;
    }

    setLoading(true);
    setResult(null);

    const formData = new FormData();
    formData.append("pdf", filePDF);
    formData.append("imagen", fileImage);

    try {
      const response = await fetch(API_ENDPOINTS.VERIFICAR_PDF, {
        method: "POST",
        body: formData,
      });
      
      const data = await response.json();

      if (data.error) {
        setResult({ 
          verificado: null, 
          mensaje: data.error, 
          hash: "" 
        });
      } else {
        setResult({
          verificado: data.valido,
          mensaje: data.valido
            ? "✓ Documento verificado correctamente"
            : "✗ Documento NO encontrado o inválido",
          hash: data.hash,
        });
      }
    } catch (error) {
      setResult({
        verificado: null,
        mensaje: "Error de conexión con el servidor",
        hash: "",
      });
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-black via-gray-900 to-blue-900">
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

      {/* Contenido principal */}
      <div className="flex-1 flex items-center justify-center p-6">
        <motion.div
          initial={{ opacity: 0, y: 25 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="bg-gray-950 text-gray-100 shadow-2xl rounded-3xl p-10 w-full max-w-lg border border-gray-800"
        >
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-blue-400 mb-1">
              Proyecto Hashart
            </h1>
            <h2 className="text-xl font-semibold text-gray-300">
              Verificación de Autenticidad
            </h2>
            <p className="text-gray-400 text-sm mt-1">
              Suba el PDF y la imagen salt para verificar.
            </p>
          </div>

          <form onSubmit={handleVerify} className="space-y-5">
            {/* Input para PDF */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                PDF Original (el que fue certificado)
              </label>
              <p className="text-xs text-gray-500 mb-2">
                PDF original, no el PDF con QR
              </p>
              <input
                type="file"
                accept="application/pdf"
                onChange={(e) => setFilePDF(e.target.files[0])}
                className="border border-gray-700 bg-gray-900 rounded-xl w-full p-3 text-gray-100 focus:border-blue-500 focus:ring-2 focus:ring-blue-700 transition"
              />
              {filePDF && (
                <p className="text-xs text-gray-400 mt-1">
                  ✓ {filePDF.name}
                </p>
              )}
            </div>

            {/* Input para Imagen */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Imagen Salt
              </label>
              <p className="text-xs text-gray-500 mb-2">
                Imagen del ZIP descargado
              </p>
              <input
                type="file"
                accept="image/png,image/jpeg,image/jpg,image/gif,image/webp"
                onChange={(e) => setFileImage(e.target.files[0])}
                className="border border-gray-700 bg-gray-900 rounded-xl w-full p-3 text-gray-100 focus:border-blue-500 focus:ring-2 focus:ring-blue-700 transition"
              />
              {fileImage && (
                <p className="text-xs text-gray-400 mt-1">
                  ✓ {fileImage.name}
                </p>
              )}
            </div>

            <div className="text-center text-sm text-gray-400 italic leading-snug">
              Proyecto de tesis — Universidad de San Buenaventura 2025-2
              <br />
              Realizado por <span className="font-semibold">Juan Campo</span> y{" "}
              <span className="font-semibold">Juan Lara</span>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="flex items-center justify-center gap-2 bg-gradient-to-r from-blue-600 to-blue-800 text-white px-4 py-3 rounded-xl w-full hover:from-blue-500 hover:to-blue-700 active:scale-[0.98] transition-all font-medium disabled:opacity-60"
            >
              {loading ? (
                <>
                  <Loader2 className="animate-spin w-5 h-5" /> Verificando...
                </>
              ) : (
                "Verificar Autenticidad"
              )}
            </button>
          </form>

          <AnimatePresence>
            {result && (
              <motion.div
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.3 }}
                className="mt-8 text-center bg-gray-900/60 rounded-2xl p-4 border border-gray-700"
              >
                {result.verificado === true && (
                  <div className="text-green-400">
                    <CheckCircle2 className="w-10 h-10 mx-auto mb-2" />
                    <p className="font-semibold text-lg">{result.mensaje}</p>
                    <p className="text-xs text-gray-400 break-all mt-3 bg-gray-800 p-2 rounded">
                      Hash: {result.hash}
                    </p>
                  </div>
                )}
                {result.verificado === false && (
                  <div className="text-yellow-400">
                    <XCircle className="w-10 h-10 mx-auto mb-2" />
                    <p className="font-semibold text-lg">{result.mensaje}</p>
                    <p className="text-xs text-gray-400 break-all mt-3 bg-gray-800 p-2 rounded">
                      Hash: {result.hash}
                    </p>
                  </div>
                )}
                {result.verificado === null && (
                  <div className="text-red-500">
                    <XCircle className="w-10 h-10 mx-auto mb-2" />
                    <p className="font-semibold text-lg">{result.mensaje}</p>
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>

      {/* Banda inferior */}
      <div className="bg-white text-black text-center py-3 shadow-inner font-semibold text-lg">
        <button
          onClick={() => navigate("/upload")}
          className="hover:underline"
        >
          Ir a Certificar
        </button>
      </div>
    </div>
  );
}
