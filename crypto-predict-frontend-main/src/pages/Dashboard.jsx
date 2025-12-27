import React, { useState, useEffect } from "react";
import PriceChart from "../components/charts/PriceChart.jsx";
import api from "../services/api";

const COINS = [
  { id: "BTC", label: "Bitcoin (BTC)" },
  { id: "ETH", label: "Ethereum (ETH)" },
  { id: "SOL", label: "Solana (SOL)" },
];

export default function Dashboard() {
  const [selectedCoin, setSelectedCoin] = useState("BTC");
  const [stats, setStats] = useState([]);
  const [sentiment, setSentiment] = useState({ score: 0, label: "Neutral" });
  const [loading, setLoading] = useState(true);

  // 1. جلب بيانات السوق والمشاعر معاً (UC-03 & UC-09)
  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      try {
        // جلب أسعار العملات (Top Assets)
        const statsRes = await api.get("/prices/top-assets");
        setStats(statsRes.data);

        // جلب تحليل المشاعر من نموذج BERT (UC-10)
        const sentimentRes = await api.get(`/sentiment/${selectedCoin}`);
        const labels = { "1": "Positive", "0": "Neutral", "-1": "Negative" };
        setSentiment({ 
          score: sentimentRes.data.score, 
          label: labels[sentimentRes.data.score] || "Neutral" 
        });

      } catch (err) {
        console.error("Dashboard data error:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboardData();
  }, [selectedCoin]);

  if (loading) return <div className="loading">Updating Market Insights...</div>;

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Market Overview</h1>
        <p>Real-time analytics and AI-driven sentiment analysis.</p>
      </header>

      {/* --- قسم البطاقات العلوية (تم نقل المشاعر هنا) --- */}
      <section className="dashboard-section">
        <div className="stats-grid">
          {/* بطاقة المشاعر (BERT Model Result) - صفحة 8 في التقرير */}
          <article className={`stat-card sentiment-highlight ${sentiment.label.toLowerCase()}`}>
            <h3 className="stat-name">Market Mood (BERT)</h3>
            <p className="sentiment-label">{sentiment.label}</p>
            <div className="sentiment-bar">
               <span className="score-text">Score: {sentiment.score}</span>
            </div>
          </article>

          {/* بطاقات العملات الحقيقية */}
          {stats.map((item) => (
            <article key={item.id} className="stat-card">
              <h3 className="stat-name">{item.name}</h3>
              <p className="stat-price">${item.price.toLocaleString()}</p>
              <p className={item.change >= 0 ? "stat-change-up" : "stat-change-down"}>
                {item.change >= 0 ? "▲" : "▼"} {item.change}%
              </p>
            </article>
          ))}
        </div>
      </section>

      {/* قسم الرسم البياني - UC-05 */}
      <section className="dashboard-section">
        <div className="chart-header">
          <h2 className="section-title">Price Prediction (LSTM + XGBoost)</h2>
          <div className="chart-controls">
            <select value={selectedCoin} onChange={(e) => setSelectedCoin(e.target.value)}>
              {COINS.map(c => <option key={c.id} value={c.id}>{c.label}</option>)}
            </select>
          </div>
        </div>
        <PriceChart coin={selectedCoin} range="1h" />
      </section>
    </div>
  );
}