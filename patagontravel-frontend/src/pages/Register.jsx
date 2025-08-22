import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL;

export default function Register({ onRegistered }) {
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const res = await axios.post(
        `${API_URL}/auth/register`,
        new URLSearchParams({
          username: form.username,
          password: form.password
        })
      );
      onRegistered(res.data.access_token); // guarda token y setUser
      navigate("/home");
    } catch (err) {
      if (err.response?.status === 400) {
        setError("El usuario ya existe");
      } else {
        setError("Error al registrarse");
      }
    }
  };

  return (
    <div style={{ padding: "2rem", maxWidth: 420, margin: "0 auto" }}>
      <h2>Crear cuenta</h2>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: 12 }}>
          <label>Usuario</label>
          <input
            name="username"
            value={form.username}
            onChange={handleChange}
            required
            minLength={3}
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
            required
            minLength={6}
            style={{ width: "100%" }}
          />
        </div>
        <button type="submit">Registrarme</button>
      </form>
      {error && <p style={{ color: "red", marginTop: 10 }}>{error}</p>}
      <p style={{ marginTop: 16 }}>
        ¿Ya tienes cuenta?{" "}
        <Link to="/">Inicia sesión</Link>
      </p>
    </div>
  );
}