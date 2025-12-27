import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

export default function Register() {
  const navigate = useNavigate();
  // تعديل اسم الحالة لتطابق المسمى في التقرير: User_Name
  const [User_Name, setUser_Name] = useState(""); 
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [apiError, setApiError] = useState("");

  const validate = () => {
    const newErrors = {};
    // التحقق من الاسم بناءً على "Main Course - Step 4" في التقرير
    if (!User_Name.trim()) {
      newErrors.User_Name = "Full Name is required";
    } else if (User_Name.trim().length < 3) {
      newErrors.User_Name = "Name must be at least 3 characters";
    }

    if (!email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/^\S+@\S+\.\S+$/.test(email)) {
      newErrors.email = "Please enter a valid email";
    }

    // التحقق من قوة كلمة المرور (أكثر من 8 خانات كما في التقرير)
    if (!password) {
      newErrors.password = "Password is required";
    } else if (password.length < 8) {
      newErrors.password = "Password must be at least 8 characters";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setIsSubmitting(true);
    setApiError("");

    try {
      // تعديل الرابط ليتوافق مع المسار في FastAPI
      const response = await fetch("http://localhost:8000/api/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          User_Name: User_Name, // إرسال المسمى الصحيح للباك إيند
          email: email,
          password: password,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // حالة النجاح (Postconditions صفحة 4)
        alert("Account created successfully! Please sign in.");
        navigate("/login"); // التوجيه لصفحة تسجيل الدخول كما في التقرير
      } else {
        // عرض الأخطاء الموثقة مثل "Email already registered"
        setApiError(data.detail || "Registration failed. Try again.");
      }
    } catch (error) {
      // خطأ في الاتصال (Exception EX1 صفحة 4)
      setApiError("System error, please try again later.");
      console.error("Register Error:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-main">
          <div className="auth-header">
            <h1>Create Account</h1>
            <p>Enter your details to sign up</p>
          </div>

          {apiError && <p style={{ color: "#ff4d4d", marginBottom: "15px" }}>{apiError}</p>}

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="field">
              <label className="field-label">Full Name</label>
              <input
                type="text"
                className={`field-input ${errors.User_Name ? "field-input-error" : ""}`}
                placeholder="Enter your full name"
                value={User_Name}
                onChange={(e) => setUser_Name(e.target.value)}
              />
              {errors.User_Name && <span className="error-text">{errors.User_Name}</span>}
            </div>

            <div className="field">
              <label className="field-label">Email Address</label>
              <input
                type="email"
                className={`field-input ${errors.email ? "field-input-error" : ""}`}
                placeholder="example@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
              {errors.email && <span className="error-text">{errors.email}</span>}
            </div>

            <div className="field">
              <label className="field-label">Password</label>
              <input
                type="password"
                className={`field-input ${errors.password ? "field-input-error" : ""}`}
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              {errors.password && <span className="error-text">{errors.password}</span>}
            </div>

            <button type="submit" className="primary-btn" disabled={isSubmitting}>
              {isSubmitting ? "Creating Account..." : "Register"}
            </button>
          </form>

          <p className="auth-footer-text">
            Already have an account?{" "}
            <Link to="/login" className="link">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}