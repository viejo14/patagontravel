import React, { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";

export default function Login({ login, guestLogin, user }) {
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");

  useEffect(() => {
    if (user) navigate("/home");
  }, [user, navigate]);

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleLogin = async () => {
    setError("");
    try {
      await login(form.username, form.password);
      navigate("/home");
    } catch {
      setError("Credenciales inválidas");
    }
  };

  const handleGuest = async () => {
    setError("");
    try {
      await guestLogin();
      navigate("/home");
    } catch {
      setError("No se pudo entrar como invitado");
    }
  };

  return (
    <div style={{ padding: "2rem", maxWidth: 420, margin: "0 auto" }}>
      <h2>Iniciar sesión</h2>

      <div style={{ marginBottom: 12 }}>
        <label>Usuario</label>
        <input
          name="username"
          value={form.username}
          onChange={handleChange}
          style={{ width: "100%" }}
        />
      </div>

      <div style={{ marginBottom: 12 }}>
        <label>Contraseña</label>
        <input
          type="password"
          name="password"
          value={form.password}
          onChange={handleChange}
          style={{ width: "100%" }}
        />
      </div>

      <div>
        <button onClick={handleLogin}>Entrar</button>
        <button onClick={handleGuest} style={{ marginLeft: 8 }}>
          Entrar como invitado
        </button>
      </div>

      {error && <p style={{ color: "red", marginTop: 10 }}>{error}</p>}

      <p style={{ marginTop: 16 }}>
        ¿No tienes cuenta?
        <Link to="/register" style={{ marginLeft: 4 }}>
          Crear cuenta
        </Link>
      </p>
    </div>
  );
}