import React, { useState, useEffect } from "react";
import PriceChart from "../components/charts/PriceChart.jsx";
import api from "../services/api";

export default function Dashboard() {
  const [selectedCoin, setSelectedCoin] = useState("BTC");
  const [history, setHistory] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [stats, setStats] = useState([]);
  const [showPrediction, setShowPrediction] = useState(false);

  // جلب إحصائيات البطاقات العلوية
  useEffect(() => {
    api.get("/prices/top-assets").then(res => setStats(res.data));
  }, []);

  // جلب التاريخ عند تغيير العملة
  useEffect(() => {
    api.get(`/prices/${selectedCoin}`).then(res => setHistory(res.data));
    setShowPrediction(false); // إخفاء التوقع القديم
  }, [selectedCoin]);

  const handlePredictClick = async () => {
    const res = await api.get(`/prices/predict/${selectedCoin}`);
    setPredictions(res.data);
    setShowPrediction(true);
  };

  return (
    <div style={{ padding: '20px', color: 'white', background: '#0a0a0a', minHeight: '100vh' }}>
      <h2>لوحة تحكم التداول الذكي (CIS Project)</h2>
      
      {/* البطاقات العلوية */}
      <div style={{ display: 'flex', gap: '15px', marginBottom: '30px' }}>
        {stats.map(s => (
          <div key={s.id} style={{ background: '#1a1a1a', padding: '15px', borderRadius: '8px', flex: 1, borderLeft: '4px solid #3b82f6' }}>
            <span style={{ fontSize: '12px', color: '#888' }}>{s.name}</span>
            <div style={{ fontSize: '18px', fontWeight: 'bold' }}>${s.price.toLocaleString()}</div>
          </div>
        ))}
      </div>

      {/* أدوات التحكم */}
      <div style={{ marginBottom: '20px', display: 'flex', gap: '15px' }}>
        <select value={selectedCoin} onChange={(e) => setSelectedCoin(e.target.value)} style={{ padding: '10px', background: '#222', color: 'white', border: '1px solid #444' }}>
          <option value="BTC">Bitcoin (BTC)</option>
          <option value="ETH">Ethereum (ETH)</option>
          <option value="BNB">Binance (BNB)</option>
          <option value="SOL">Solana (SOL)</option>
        </select>
        <button onClick={handlePredictClick} style={{ padding: '10px 20px', background: '#22c55e', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>
           بدء توقع الذكاء الاصطناعي 🚀
        </button>
      </div>

      {/* الرسم البياني (الشمعات) */}
      <PriceChart historyData={history} predictionData={predictions} showPrediction={showPrediction} />

      {/* جدول نتائج التوقع */}
      {showPrediction && (
        <div style={{ marginTop: '30px', background: '#111', padding: '20px', borderRadius: '10px' }}>
          <h3>📋 نتائج التوقع لعملة {selectedCoin}</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px' }}>
            <thead>
              <tr style={{ color: '#888', textAlign: 'left', borderBottom: '1px solid #333' }}>
                <th style={{ padding: '10px' }}>الوقت المتوقع</th>
                <th style={{ padding: '10px' }}>السعر المتوقع</th>
                <th style={{ padding: '10px' }}>الاتجاه</th>
                <th style={{ padding: '10px' }}>الثقة</th>
              </tr>
            </thead>
            <tbody>
              {predictions.map((p, i) => (
                <tr key={i} style={{ borderBottom: '1px solid #222' }}>
                  <td style={{ padding: '10px' }}>{new Date(p.timestamp).toLocaleTimeString()}</td>
                  <td style={{ padding: '10px', color: '#22c55e' }}>${p.predicted_value}</td>
                  <td style={{ padding: '10px' }}>{p.trend === 'Up' ? '🟢 صعود' : '🟡 مستقر'}</td>
                  <td style={{ padding: '10px' }}>{p.confidence}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}