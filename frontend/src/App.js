import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Home from "./Home";
import UploadForm from "./UploadForm";
import VerifyPage from "./VerifyPage";

function App() {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <Routes>
        {/* Ruta raíz - Home con healthcheck */}
        <Route path="/" element={<Home />} />
        
        {/* Página de certificación/subida */}
        <Route path="/upload" element={<UploadForm />} />
        
        {/* Página de verificación */}
        <Route path="/verify" element={<VerifyPage />} />
        
        {/* Ruta no encontrada */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
