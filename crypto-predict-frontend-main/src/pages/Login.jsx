import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { login } from "../services/authService";

export default function Login() {
  const navigate = useNavigate();

  // --- 1. الحالة (States) وإدارة الحقول (الأسهل) ---
  const [form, setForm] = useState({
    email: "",
    password: "",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  // دالة لتحديث قيم المدخلات عند الكتابة
  function handleChange(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  // --- 2. واجهة المستخدم (Render) - متوسط الصعوبة ---
  return (
    <div className="login-page">
      <div className="login-content">
        <div className="login-card login-fade-up">
          <h2 className="login-card-title">Sign in to your account</h2>

          {/* عرض رسالة الخطأ في حال فشل تسجيل الدخول */}
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

  // --- 3. معالجة إرسال البيانات والربط مع الباك إيند (الأصعب) ---
  async function handleSubmit(e) {
    e.preventDefault();
    setIsSubmitting(true);
    setErrorMessage("");

    try {
      // إرسال البيانات للباك إيند
      const data = await login({
        email: form.email,
        password: form.password,
      });

      // --- الخطوة الأهم لمشروعك ---
      // تخزين التوكن وبيانات المستخدم في المتصفح لاستخدامها لاحقاً
      localStorage.setItem("user_token", data.access_token); 
      localStorage.setItem("user_role", data.user.role);   // تخزين "أدمن" أو "يوزر"
      localStorage.setItem("username", data.user.name);    // تخزين اسم المستخدم للعرض

      // الانتقال للداشبورد بعد النجاح
      navigate("/dashboard");

    } catch (error) {
      // التعامل مع أخطاء الرد من السيرفر (مثل 401 Unauthorized)
      setErrorMessage(
        error.response?.data?.detail ||
        "Login failed. Please check your credentials."
      );
      console.error("Login Error:", error);
    } finally {
      setIsSubmitting(false);
    }
  }
}