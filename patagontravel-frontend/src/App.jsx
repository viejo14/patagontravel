// Importamos React y hooks para manejar estado y efectos
import React, { useState, useEffect } from "react";

// Axios para hacer peticiones HTTP al backend
import axios from "axios";

// Componentes de React Router para manejo de rutas
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

// Componentes que renderizamos según la ruta
import Login from "./Login";
import Home from "./Home";

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
    saveToken(res.data.access_token);        // Guardamos el token
    await fetchMe(res.data.access_token);    // Obtenemos datos del usuario
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

  // Efecto que se ejecuta al montar la app
  // Intenta recuperar sesión previa, si no hay, entra como invitado
  useEffect(() => {
    const init = async () => {
      const token = localStorage.getItem("access_token");
      if (token) {
        try {
          await fetchMe(token); // Token válido → obtenemos datos
        } catch {
          await guestLogin();   // Token inválido → login invitado
        }
      } else {
        await guestLogin();     // Sin token → login invitado
      }
    };
    init();
  }, []);

  // Router principal: define qué componente mostrar según la URL
  return (
    <Router>
      <Routes>
        {/* Ruta del login */}
        <Route
          path="/"
          element={
            <Login login={login} guestLogin={guestLogin} user={user} />
          }
        />

        {/* Ruta del home → ahora recibe onLogout para cerrar sesión */}
        <Route
          path="/home"
          element={<Home user={user} onLogout={logout} />}
        />
      </Routes>
    </Router>
  );
}