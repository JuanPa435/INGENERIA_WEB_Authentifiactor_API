const API_URL = "http://127.0.0.1:5000"; // ajusta si cambias puerto

// Login
document.getElementById("login-btn").addEventListener("click", async () => {
  const username = document.getElementById("login-username").value;
  const password = document.getElementById("login-password").value;

  const res = await fetch(`${API_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

  const data = await res.json();
  if (res.ok) {
    alert("✅ Login exitoso");
    localStorage.setItem("token", data.access_token);
  } else {
    alert("❌ Error: " + (data.msg || "No autorizado"));
  }
});

// Registro
document.getElementById("register-btn").addEventListener("click", async () => {
  const username = document.getElementById("register-username").value;
  const password = document.getElementById("register-password").value;

  const res = await fetch(`${API_URL}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

  const data = await res.json();
  if (res.ok) {
    alert("🎉 Usuario registrado correctamente");
  } else {
    alert("❌ Error: " + (data.msg || "Fallo en el registro"));
  }
});

// Ver productos
document.getElementById("get-products-btn").addEventListener("click", async () => {
  const token = localStorage.getItem("token");
  if (!token) return alert("Primero inicia sesión.");

  const res = await fetch(`${API_URL}/productos`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  const data = await res.json();
  const list = document.getElementById("products-list");
  list.innerHTML = "";

  if (Array.isArray(data)) {
    data.forEach((p) => {
      const li = document.createElement("li");
      li.textContent = `${p.nombre} - $${p.precio}`;
      list.appendChild(li);
    });
  } else {
    alert("Error al cargar productos");
  }
});
