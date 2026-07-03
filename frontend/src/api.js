const API = "http://localhost:8000";

function getToken() {
  return localStorage.getItem("token");
}

function getHeaders(isJson = true) {
  const headers = {};

  if (isJson) {
    headers["Content-Type"] = "application/json";
  }

  const token = getToken();

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  return headers;
}

/* ---------------------- AUTH ---------------------- */

export async function register(email, password) {
  const response = await fetch(`${API}/v1/auth/register`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({
      email,
      password,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Registration failed");
  }

  return data;
}

export async function login(email, password) {
  const body = new URLSearchParams();

  body.append("username", email);
  body.append("password", password);

  const response = await fetch(`${API}/v1/auth/token`, {
    method: "POST",
    body,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Login failed");
  }

  return data;
}

/* ---------------------- CHAT ---------------------- */

export async function sendMessage(message) {
  const response = await fetch(`${API}/v1/chat`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({
      message,
    }),
  });

  if (!response.ok) {
    throw new Error("Failed to send message.");
  }

  return response;
}

/* ---------------------- IMAGE ---------------------- */

export async function uploadImage(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API}/v1/image`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${getToken()}`,
    },
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Image upload failed.");
  }

  return response.json();
}

/* ---------------------- AUDIO ---------------------- */

export async function uploadAudio(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API}/v1/audio`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${getToken()}`,
    },
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Audio upload failed.");
  }

  return response.json();
}

/* ---------------------- MULTI-CHAT ---------------------- */

export async function getChats() {
  const response = await fetch(`${API}/v1/chats`, {
    headers: getHeaders(),
  });

  if (!response.ok) {
    throw new Error("Failed to load chats.");
  }

  return response.json();
}

export async function getChatMessages(chatId) {
  const response = await fetch(`${API}/v1/chats/${chatId}/messages`, {
    headers: getHeaders(),
  });

  if (!response.ok) {
    throw new Error("Failed to load chat messages.");
  }

  return response.json();
}



