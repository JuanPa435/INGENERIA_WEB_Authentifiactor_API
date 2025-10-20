// Obtener la URL base dinámica
const API_BASE = window.location.origin + "/api/auth";

// --- LOGIN ---
const loginForm = document.getElementById("login-form");
const togglePasswordBtn = document.getElementById('toggle-password');
if (togglePasswordBtn) {
  let pwd = document.getElementById('password');
  let visible = false;
  togglePasswordBtn.setAttribute('aria-pressed', 'false');
  togglePasswordBtn.addEventListener('click', (e) => {
    e.preventDefault();
    if (!visible) {
      pwd.type = 'text';
      visible = true;
      togglePasswordBtn.setAttribute('aria-pressed', 'true');
    } else {
      pwd.type = 'password';
      visible = false;
      togglePasswordBtn.setAttribute('aria-pressed', 'false');
    }
  });
  // soporte teclado: Enter/Space activan click nativamente en button
}
if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    const message = document.getElementById("login-message");

    try {
      const response = await fetch(`${API_BASE}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();

          if (response.ok) {
            message.style.color = "green";
            message.textContent = "✅ Inicio de sesión exitoso";
            localStorage.setItem("token", data.access_token);
            // guardar username localmente para mostrar en header
            if (data.user && data.user.username) localStorage.setItem('username', data.user.username);
            // si hay campo anon-name en el login, guardarlo
            const anonInput = document.getElementById('anon-name-input');
            if (anonInput && anonInput.value.trim()) localStorage.setItem('anon_name', anonInput.value.trim());
            setTimeout(() => (window.location.href = "dashboard.html"), 700);
          } else {
            message.style.color = "red";
            message.textContent = data.msg || "Credenciales inválidas";
          }
    } catch (err) {
      message.style.color = "red";
      message.textContent = "⚠️ Error de conexión con el servidor.";
    }
  });
}

// --- REGISTRO ---
const registerForm = document.getElementById("register-form");
const toggleRegPasswordBtn = document.getElementById('toggle-reg-password');
if (toggleRegPasswordBtn) {
  let pwdR = document.getElementById('reg-password');
  let visibleR = false;
  toggleRegPasswordBtn.setAttribute('aria-pressed', 'false');
  toggleRegPasswordBtn.addEventListener('click', (e) => {
    e.preventDefault();
    if (!visibleR) {
      pwdR.type = 'text';
      visibleR = true;
      toggleRegPasswordBtn.setAttribute('aria-pressed', 'true');
    } else {
      pwdR.type = 'password';
      visibleR = false;
      toggleRegPasswordBtn.setAttribute('aria-pressed', 'false');
    }
  });
}
if (registerForm) {
  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("reg-email").value.trim();
    const password = document.getElementById("reg-password").value.trim();
    const role = document.getElementById("reg-role").value;
    const message = document.getElementById("register-message");

    try {
      const response = await fetch(`${API_BASE}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, role })
      });

      const data = await response.json();

      if (response.ok) {
        message.style.color = "green";
        message.textContent = "✅ Usuario registrado correctamente.";
        // si el formulario tiene campo anon-name, guardarlo
        const anonInputR = document.getElementById('anon-name-input');
        if (anonInputR && anonInputR.value.trim()) localStorage.setItem('anon_name', anonInputR.value.trim());
        setTimeout(() => (window.location.href = "login.html"), 900);
      } else {
        message.style.color = "red";
        message.textContent = data.msg || "Error al registrar usuario.";
      }
    } catch (err) {
      message.style.color = "red";
      message.textContent = "⚠️ Error de conexión con el servidor.";
    }
  });
}
