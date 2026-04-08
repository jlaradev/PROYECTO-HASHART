import React from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Upload, CheckCircle2 } from "lucide-react";

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-black via-gray-900 to-blue-900 px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center max-w-2xl"
      >
        <h1 className="text-5xl font-bold text-white mb-4">
          Proyecto <span className="text-blue-400">Hashart</span>
        </h1>
        
        <p className="text-gray-300 text-lg mb-12">
          Sistema de autenticidad y verificación de documentos
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Botón Certificar */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => navigate("/upload")}
            className="bg-gradient-to-br from-blue-600 to-blue-800 hover:from-blue-500 hover:to-blue-700 text-white rounded-2xl p-8 shadow-xl transition-all"
          >
            <div className="flex flex-col items-center space-y-4">
              <Upload className="w-12 h-12" />
              <div>
                <h2 className="text-2xl font-bold">Certificar</h2>
                <p className="text-blue-200 text-sm mt-1">
                  Obtenga un certificado de autenticidad para el documento
                </p>
              </div>
            </div>
          </motion.button>

          {/* Botón Verificar */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => navigate("/verify")}
            className="bg-gradient-to-br from-green-600 to-green-800 hover:from-green-500 hover:to-green-700 text-white rounded-2xl p-8 shadow-xl transition-all"
          >
            <div className="flex flex-col items-center space-y-4">
              <CheckCircle2 className="w-12 h-12" />
              <div>
                <h2 className="text-2xl font-bold">Verificar</h2>
                <p className="text-green-200 text-sm mt-1">
                  Verifique la autenticidad de un documento
                </p>
              </div>
            </div>
          </motion.button>
        </div>

        <p className="text-gray-500 text-sm mt-12">
          Universidad de San Buenaventura 2025-2<br />
          <span className="text-gray-600">Realizado por Juan Campo y Juan Lara</span>
        </p>
      </motion.div>
    </div>
  );
}
