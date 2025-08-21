import React from "react";
import { useNavigate } from "react-router-dom";

export default function Login({ login, guestLogin, user }) {
  const navigate = useNavigate();

  const handleGuest = async () => {
    await guestLogin();
    navigate("/home");
  };

  const handleLogin = async () => {
    await login("francisco", "123456");
    navigate("/home");
  };

  if (user) {
    navigate("/home");
    return null;
  }

  return (
    <div style={{ padding: "2rem", textAlign: "center" }}>
      <h1>PatagonTravel</h1>
      <button onClick={handleLogin}>Iniciar sesión</button>
      <button onClick={handleGuest} style={{ marginLeft: "1rem" }}>
        Entrar como invitado
      </button>
    </div>
  );
}