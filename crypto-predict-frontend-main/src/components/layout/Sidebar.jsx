// src/components/layout/Sidebar.jsx
import React from "react"
import { NavLink } from "react-router-dom";

const navItems = [
  { label: "Overview", path: "/dashboard" },
  { label: "Markets", path: "/dashboard/markets", disabled: true },
  { label: "Predictions", path: "/dashboard/predictions", disabled: true },
  { label: "Sentiment", path: "/dashboard/sentiment", disabled: true },
  { label: "Settings", path: "/dashboard/settings", disabled: true },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="sidebar-logo">₿</div>
        <div>
          <p className="sidebar-title">Crypto Predict</p>
          <p className="sidebar-subtitle">AI insights</p>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => {
          if (item.disabled) {
            return (
              <div key={item.label} className="nav-item nav-item-disabled">
                {item.label}
                <span className="nav-tag">soon</span>
              </div>
            );
          }

          return (
            <NavLink
              key={item.label}
              to={item.path}
              className={({ isActive }) =>
                `nav-item ${isActive ? "nav-item-active" : ""}`
              }
            >
              {item.label}
            </NavLink>
          );
        })}
      </nav>
    </aside>
  );
}
