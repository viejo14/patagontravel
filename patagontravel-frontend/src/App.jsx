// Importamos React y hooks para manejar estado y efectos
import React, { useState, useEffect } from "react";
import Register from "./Register";
import Login from "./Login";
import Home from "./Home";
import UserList from "./components/UserList"; // Listado de usuarios
import ForgotPassword from "./ForgotPassword";// 📌 NUEVO: Pantalla para solicitar recuperación

// Axios para hacer peticiones HTTP al backend
import axios from "axios";

// Componentes de React Router para manejo de rutas
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

// Leemos la URL de la API desde variables de entorno (Vite)
const API_URL = import.meta.env.VITE_API_URL;

export default function App() {
  // Estado global del usuario logueado (null si no hay sesión)
  const [user, setUser] = useState(null);

  // Guarda el token JWT en localStorage
  const saveToken = (token) => {
    localStorage.setItem("access_token", token);
  };

  // Llama al backend para obtener la info del usuario actual
  const fetchMe = async (token) => {
    const me = await axios.get(`${API_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    setUser(me.data); // Guardamos los datos en el estado
  };

  // Login normal con usuario y contraseña
  const login = async (username, password) => {
    const res = await axios.post(
      `${API_URL}/auth/login`,
      new URLSearchParams({ username, password })
    );
    saveToken(res.data.access_token);
    await fetchMe(res.data.access_token);
  };

  // Login como invitado (sin credenciales)
  const guestLogin = async () => {
    const res = await axios.post(`${API_URL}/auth/guest`);
    saveToken(res.data.access_token);
    await fetchMe(res.data.access_token);
  };

  // Cerrar sesión: elimina token y limpia el estado del usuario
  const logout = () => {
    localStorage.removeItem("access_token");
    setUser(null);
  };

  // 📌 Función para manejar el registro exitoso
  const onRegistered = async (token) => {
    saveToken(token);
    await fetchMe(token);
  };

  // Intenta recuperar sesión previa o hace login invitado
  useEffect(() => {
    const init = async () => {
      const token = localStorage.getItem("access_token");
      if (token) {
        try {
          await fetchMe(token);
        } catch {
          await guestLogin();
        }
      } else {
        await guestLogin();
      }
    };
    init();
  }, []);

  // Router principal
  return (
    <Router>
      <Routes>
        {/* Login */}
        <Route
          path="/"
          element={
            <Login
              login={login}
              guestLogin={guestLogin}
              user={user}
            />
          }
        />

        {/* Registro */}
        <Route
          path="/register"
          element={<Register onRegistered={onRegistered} />}
        />

        {/* 📌 NUEVA RUTA: Recuperar contraseña */}
        <Route
          path="/forgot-password"
          element={<ForgotPassword />}
        />

        {/* Home con botón de logout */}
        <Route
          path="/home"
          element={<Home user={user} onLogout={logout} />}
        />

        {/* Panel de usuarios */}
        <Route
          path="/users"
          element={
            <div>
              <h1>Panel de Usuarios</h1>
              <UserList /> {/* Listado en tabla */}
            </div>
          }
        />
      </Routes>
    </Router>
  );
}