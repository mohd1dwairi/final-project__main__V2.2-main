// src/components/layout/Topbar.jsx
import React from "react"
export default function Topbar() {
  return (
    <header className="topbar">
      <div className="topbar-left">
        <span className="badge">BETA</span>
        <span className="topbar-text">
          Crypto price prediction & sentiment analysis
        </span>
      </div>

      <div className="topbar-right">
        <input
          className="search-input"
          placeholder="Search for a coin, e.g. BTC, ETH..."
        />
        <div className="user-pill">
          <div className="user-avatar">R</div>
          <span className="user-name">Raed</span>
        </div>
      </div>
    </header>
  );
}
