import React from "react";

export default function SentimentCard({ sentiment }) {
  // تحديد اللون والأيقونة بناءً على الحالة (صفحة 8 في التقرير)
  const getStatusConfig = (label) => {
    switch (label) {
      case "Positive":
        return { color: "#22c55e", icon: "😊", bg: "rgba(34, 197, 94, 0.1)" };
      case "Negative":
        return { color: "#ef4444", icon: "😨", bg: "rgba(239, 68, 68, 0.1)" };
      default:
        return { color: "#80796bff", icon: "😐", bg: "rgba(107, 114, 128, 0.1)" };
    }
  };

  const config = getStatusConfig(sentiment.label);

  return (
    <div className="sentiment-top-card" style={{ backgroundColor: config.bg, border: `1px solid ${config.color}` }}>
      <div className="sentiment-info">
        <span className="sentiment-icon" style={{ fontSize: "2rem" }}>{config.icon}</span>
        <div>
          <h4 style={{ margin: 0, color: "#9ca3af" }}>Market Sentiment</h4>
          <h2 style={{ margin: 0, color: config.color }}>{sentiment.label}</h2>
        </div>
      </div>
      <div className="sentiment-score">
        <p>Score: <strong>{sentiment.value}</strong></p>
        <small>(Analyzed by BERT Model)</small>
      </div>
    </div>
  );
}