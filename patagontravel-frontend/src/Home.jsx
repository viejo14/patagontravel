import React from "react";
import { useNavigate } from "react-router-dom";

export default function Home({ user, onLogout }) {
  const navigate = useNavigate();

  if (!user) {
    return <p>Cargando...</p>;
  }

  const handleLogout = () => {
    onLogout();      // borra token y resetea usuario
    navigate("/");   // redirige a login
  };

  return (
    <div style={{ padding: "2rem", textAlign: "center" }}>
      <h1>Hola, {user.username} ✈️ Bienvenido a PatagonTravel</h1>
      <p>Rol: {user.role}</p>

      <button 
        onClick={handleLogout} 
        style={{ marginTop: "1rem", padding: "0.5rem 1rem", cursor: "pointer" }}
      >
        Cerrar sesión
      </button>
    </div>
  );
}