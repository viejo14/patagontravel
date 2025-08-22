// Importamos React y sus hooks para manejar estado y efectos secundarios
import React, { useState, useEffect } from "react";
// Importamos herramientas de navegación y enlace de React Router
import { useNavigate, Link } from "react-router-dom";

// Componente principal de Login, recibe por props funciones y estado del usuario
export default function Login({ login, guestLogin, user }) {
  // Hook para navegar entre rutas
  const navigate = useNavigate();

  // Estado para almacenar los valores del formulario de login
  const [form, setForm] = useState({ username: "", password: "" });
  // Estado para mostrar mensajes de error si algo falla
  const [error, setError] = useState("");

  // 🔄 useEffect: si el usuario ya está logueado, lo redirige automáticamente a /home
  useEffect(() => {
    if (user) navigate("/home");
  }, [user, navigate]);

  // 📥 Maneja cambios en los inputs actualizando el estado `form`
  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  // 🔑 Lógica para login normal
  const handleLogin = async () => {
    setError("");
    try {
      await login(form.username, form.password); // Llama a la función login pasada por props
      navigate("/home"); // Redirige al home si todo sale bien
    } catch {
      setError("Credenciales inválidas"); // Muestra error si falla
    }
  };

  // 🟢 Lógica para login como invitado
  const handleGuest = async () => {
    setError("");
    try {
      await guestLogin(); // Llama a la función guestLogin
      navigate("/home"); // Redirige al home
    } catch {
      setError("No se pudo entrar como invitado"); // Error si falla
    }
  };

  // 🖼 Renderizado de la interfaz
  return (
    <div style={{ padding: "2rem", maxWidth: 420, margin: "0 auto" }}>
      <h2>Iniciar sesión</h2>

      {/* Campo de usuario */}
      <div style={{ marginBottom: 12 }}>
        <label>Usuario</label>
        <input
          name="username"
          value={form.username}
          onChange={handleChange}
          style={{ width: "100%" }}
        />
      </div>

      {/* Campo de contraseña + botón para recuperar contraseña */}
      <div style={{ marginBottom: 12 }}>
        <label>Contraseña</label>
        <input
          type="password"
          name="password"
          value={form.password}
          onChange={handleChange}
          style={{ width: "100%" }}
        />
        {/* 🔗 Botón que redirige a la pantalla de recuperación de contraseña */}
        <div style={{ textAlign: "right", marginTop: 6 }}>
          <button
            type="button"
            onClick={() => navigate("/forgot-password")}
            style={{
              background: "none",
              border: "none",
              color: "#007bff",
              textDecoration: "underline",
              cursor: "pointer",
              padding: 0,
              fontSize: "0.9rem"
            }}
          >
            Recupera tu contraseña
          </button>
        </div>
      </div>

      {/* Botones de acción */}
      <div>
        <button onClick={handleLogin}>Entrar</button>
        <button onClick={handleGuest} style={{ marginLeft: 8 }}>
          Entrar como invitado
        </button>
      </div>

      {/* Mensaje de error si existe */}
      {error && <p style={{ color: "red", marginTop: 10 }}>{error}</p>}

      {/* Enlace para crear cuenta nueva */}
      <p style={{ marginTop: 16 }}>
        ¿No tienes cuenta?
        <Link to="/register" style={{ marginLeft: 4 }}>
          Crear cuenta
        </Link>
      </p>
    </div>
  );
}