import axios from "axios";

// Retrieve the base URL from the environment or default to our local API Gateway
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Global Axios instance communicating with the API Gateway.
 */
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Axios Interceptor to automatically attach the JWT token to every outgoing request.
api.interceptors.request.use(
  (config) => {
    // We store the Zustand state in localStorage under the key 'auth-storage'
    try {
      const authStorage = localStorage.getItem("auth-storage");
      if (authStorage) {
        const { state } = JSON.parse(authStorage);
        if (state && state.token) {
          config.headers.Authorization = `Bearer ${state.token}`;
        }
      }
    } catch (error) {
      console.error("Failed to parse auth storage in axios interceptor", error);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);
