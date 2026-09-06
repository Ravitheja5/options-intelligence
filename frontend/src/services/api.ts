import axios from "axios";

const API_BASE_URL = "https://options-intelligence-backend.onrender.com";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export default api;