import { useState, useEffect } from "react";
import axios from "axios";

export default function App() {
  const [user, setUser] = useState(null);
  const [error, setError] = useState("");

  const API_URL = import.meta.env.VITE_API_URL;

  const saveToken = (token) => {
    localStorage.setItem("access_token", token);
  };

  const fetchMe = async (token) => {
    const me = await axios.get(`${API_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    setUser(me.data);
  };

  const login = async () => {
    try {
      const res = await axios.post(
        `${API_URL}/auth/login`,
        new URLSearchParams({
          username: "francisco",
          password: "123456"
        })
      );
      saveToken(res.data.access_token);
      await fetchMe(res.data.access_token);
      setError("");
    } catch {
      setError("Error al iniciar sesión");
    }
  };

  const guestLogin = async () => {
    try {
      const res = await axios.post(`${API_URL}/auth/guest`);
      saveToken(res.data.access_token);
      await fetchMe(res.data.access_token);
      setError("");
    } catch {
      setError("Error en login invitado");
    }
  };

  useEffect(() => {
    const init = async () => {
      const token = localStorage.getItem("access_token");
      if (token) {
        try {
          await fetchMe(token);
        } catch {
          // Si el token no es válido (caso muy raro con 1 año de duración), volvemos a invitado
          await guestLogin();
        }
      } else {
        await guestLogin();
      }
    };
    init();
  }, []);

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>PatagonTravel</h1>
      {user ? (
        <p>Hola {user.username}, rol: {user.role}</p>
      ) : (
        <>
          <button onClick={login}>Iniciar sesión</button>
          <button onClick={guestLogin} style={{ marginLeft: "1rem" }}>
            Entrar como invitado
          </button>
          {error && <p style={{ color: "red" }}>{error}</p>}
        </>
      )}
    </div>
  );
}