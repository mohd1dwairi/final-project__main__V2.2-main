// src/components/layout/AppLayout.jsx
import React from "react"; // أضفنا هذا السطر لحل مشكلة "React is not defined"
import Sidebar from "./Sidebar.jsx";
import Topbar from "./Topbar.jsx";

export default function AppLayout({ children }) {
  return (
    <div className="app-shell">
      <Sidebar />

      <div className="app-main-area">
        <Topbar />
        <main className="app-main-content">{children}</main>
      </div>
    </div>
  );
}