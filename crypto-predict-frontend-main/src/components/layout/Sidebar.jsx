import React from "react"
import { NavLink } from "react-router-dom";

const navItems = [
  { label: "Overview", path: "/dashboard" },
  { label: "Markets", path: "/dashboard/markets" },
  { label: "Predictions", path: "/dashboard/predictions" }, // قمنا بتفعيلها
  { label: "Sentiment", path: "/dashboard/sentiment" },    // قمنا بتفعيلها
  { label: "Settings", path: "/dashboard/settings" },      
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="sidebar-logo">₿</div>
        <div>
          <p className="sidebar-title">Crypto Predict</p>
          <p className="sidebar-subtitle">AI Insights</p>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.label}
            to={item.path}
            className={({ isActive }) =>
              `nav-item ${isActive ? "nav-item-active" : ""}`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}