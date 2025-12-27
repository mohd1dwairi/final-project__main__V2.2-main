import React from "react"

export default function Topbar() {
  const userName = "mohd"; 
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
      </div>
    </header>
  );
}