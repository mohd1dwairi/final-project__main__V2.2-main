import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom"; // استيراد Navigate للتنقل

export default function Topbar() {
  const [userName, setUserName] = useState("Guest");
  const navigate = useNavigate(); // تعريف الـ navigate

  useEffect(() => {
    const storedName = localStorage.getItem("username");
    if (storedName) {
      setUserName(storedName);
    }
  }, []);

  // دالة تسجيل الخروج
  const handleLogout = () => {
    // 1. حذف التوكن والاسم من المتصفح
    localStorage.removeItem("user_token");
    localStorage.removeItem("username");
    
    // 2. توجيه المستخدم لصفحة تسجيل الدخول
    navigate("/login");
  };

  const userInitial = userName.charAt(0).toUpperCase();

  return (
    <header className="topbar">
      <div className="topbar-left">
        <span className="badge">BETA</span>
        <span className="topbar-text">
          Crypto Price Prediction & Sentiment Analysis
        </span>
      </div>

      <div className="topbar-right">
        <input
          className="search-input"
          placeholder="Search for a coin, e.g. BTC, ETH..."
        />
        
        <div className="user-pill">
          <div className="user-avatar">{userInitial}</div>
          <span className="user-name">{userName}</span>
        </div>

        {/* زر تسجيل الخروج الجديد */}
        <button onClick={handleLogout} className="logout-btn">
          Logout
        </button>
      </div>
    </header>
  );
}