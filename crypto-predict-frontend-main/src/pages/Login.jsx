import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { login } from "../services/authService";

export default function Login() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    email: "",
    password: "",
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  // تحديث الحقول
  function handleChange(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  // تسجيل الدخول
  async function handleSubmit(e) {
    e.preventDefault();
    setIsSubmitting(true);
    setErrorMessage("");

    try {
      const data = await login({
        email: form.email,
        password: form.password,
      });

      // تخزين التوكن
      localStorage.setItem("user_token", data.access_token);

      // الانتقال للداشبورد
      navigate("/dashboard");

    } catch (error) {
      setErrorMessage(
        error.response?.data?.detail ||
        "Login failed. Please check your credentials."
      );
      console.error("Login Error:", error);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-content">

        {/* الجزء الأيسر (اختياري) */}
        <div className="login-info">
          {/* محتوى بصري أو معلومات */}
        </div>

        {/* كرت تسجيل الدخول */}
        <div className="login-card login-fade-up">
          <h2 className="login-card-title">Sign in to your account</h2>

          {/* رسالة الخطأ */}
          {errorMessage && (
            <p style={{ color: "#ff4d4d", textAlign: "center", marginBottom: "10px" }}>
              {errorMessage}
            </p>
          )}

          <form className="login-form" onSubmit={handleSubmit}>
            <div className="login-field">
              <label htmlFor="email" className="login-label">Email</label>
              <input
                id="email"
                name="email"
                type="email"
                required
                placeholder="you@example.com"
                value={form.email}
                onChange={handleChange}
                className="login-input"
              />
            </div>

            <div className="login-field">
              <label htmlFor="password" className="login-label">Password</label>
              <input
                id="password"
                name="password"
                type="password"
                required
                placeholder="••••••••"
                value={form.password}
                onChange={handleChange}
                className="login-input"
              />
            </div>

            <button
              type="submit"
              className="login-button"
              disabled={isSubmitting}
            >
              {isSubmitting ? "Signing in..." : "Sign in"}
            </button>
          </form>

          <p className="login-footer-text">
            Don&apos;t have an account?{" "}
            <Link to="/register" className="login-link">
              Create account
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
