import React, { useState, useEffect } from "react";
import PriceChart from "../components/charts/PriceChart.jsx";
import AddDataForm from "../components/AddDataForm.jsx";
import api from "../services/api";

export default function Dashboard() {
  // --- 1. تعريف الحالة (States) - الأسهل ---
  const [selectedCoin, setSelectedCoin] = useState("BTC");
  const [history, setHistory] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [stats, setStats] = useState([]);
  const [showPrediction, setShowPrediction] = useState(false);

  // استخراج دور المستخدم من التخزين المحلي (admin أو user)
  const userRole = localStorage.getItem("user_role"); 
  const username = localStorage.getItem("username");

  // --- 2. جلب البيانات من السيرفر (متوسط الصعوبة) ---
  
  // جلب إحصائيات العملات العلوية عند تحميل الصفحة لأول مرة
  useEffect(() => {
    api.get("/prices/top-assets").then(res => setStats(res.data));
  }, []);

  // جلب سجل الأسعار التاريخي عند تغيير العملة المختارة
  useEffect(() => {
    api.get(`/prices/${selectedCoin}`).then(res => setHistory(res.data));
    setShowPrediction(false); // إخفاء التوقعات القديمة عند تغيير العملة
  }, [selectedCoin]);

  // --- 3. المنطق البرمجي للتحكم والتوقع (الأصعب) ---

  // دالة طلب التوقع من محرك الذكاء الاصطناعي
  const handlePredictClick = async () => {
    try {
      const res = await api.get(`/prices/predict/${selectedCoin}`);
      setPredictions(res.data);
      setShowPrediction(true);
    } catch (error) {
      alert("Error fetching prediction: " + (error.response?.data?.detail || "Insufficient data"));
    }
  };

  return (
    <div style={styles.container}>
      {/* قسم الترويسة - يعرض اسم المستخدم والترحيب */}
      <header style={styles.header}>
        <h2>Smart Trading Dashboard <span style={{color: '#3b82f6'}}>(CIS Project)</span></h2>
        <p style={{color: '#888'}}>Welcome back, {username} ({userRole})</p>
      </header>
      
      {/* القسم 1: بطاقات الإحصائيات السريعة */}
      <div style={styles.statsGrid}>
        {stats.map(s => (
          <div key={s.id} style={styles.statCard}>
            <span style={styles.statLabel}>{s.name}</span>
            <div style={styles.statPrice}>${s.price ? s.price.toLocaleString() : "0.00"}</div>
          </div>
        ))}
      </div>

      {/* القسم 2: أدوات التحكم والرسم البياني الأساسي */}
      <div style={styles.mainSection}>
        <div style={styles.controls}>
          <select 
            value={selectedCoin} 
            onChange={(e) => setSelectedCoin(e.target.value)} 
            style={styles.select}
          >
            <option value="BTC">Bitcoin (BTC)</option>
            <option value="ETH">Ethereum (ETH)</option>
            <option value="BNB">Binance (BNB)</option>
            <option value="SOL">Solana (SOL)</option>
            <option value="DOGE">Dogecoin (DOGE)</option>
          </select>

          <button onClick={handlePredictClick} style={styles.predictBtn}>
            Start AI Prediction 🚀
          </button>
        </div>

        <PriceChart historyData={history} predictionData={predictions} showPrediction={showPrediction} />
      </div>

      {/* --- الربط مع نظام الأدمن (Admin Role) --- */}
      {/* القسم 3: نموذج إدخال البيانات - يظهر فقط إذا كان المستخدم أدمن */}
      {userRole === "admin" && (
        <div style={styles.formSection}>
          <div style={{ borderLeft: '4px solid #22c55e', paddingLeft: '15px', marginBottom: '15px' }}>
            <h3 style={{ margin: 0 }}>Admin Control Panel</h3>
            <small style={{ color: '#888' }}>You have access to inject manual market signals.</small>
          </div>
          <AddDataForm />
        </div>
      )}

      {/* القسم 4: جدول تفاصيل التوقعات (يظهر عند طلب التوقع) */}
      {showPrediction && (
        <div style={styles.tableSection}>
          <h3>📋 Detailed Prediction Results for {selectedCoin}</h3>
          <table style={styles.table}>
            <thead>
              <tr style={styles.tableHeader}>
                <th>Predicted Time</th>
                <th>Predicted Price</th>
                <th>Trend Status</th>
                <th>AI Confidence</th>
              </tr>
            </thead>
            <tbody>
              {predictions.map((p, i) => (
                <tr key={i} style={styles.tableRow}>
                  <td>{new Date(p.timestamp).toLocaleTimeString('en-US')}</td>
                  <td style={{ color: '#22c55e', fontWeight: 'bold' }}>${p.predicted_value}</td>
                  <td>
                    {p.trend === 'Up' ? (
                      <span style={styles.badgeUp}>🟢 Bullish</span>
                    ) : (
                      <span style={styles.badgeStable}>🟡 Stable/Bearish</span>
                    )}
                  </td>
                  <td>{p.confidence}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// التنسيقات الداخلية المنظمة
const styles = {
  container: { padding: '20px', color: 'white', background: '#0a0a0a', minHeight: '100vh', fontFamily: 'Arial, sans-serif' },
  header: { marginBottom: '20px', borderBottom: '1px solid #222', paddingBottom: '10px' },
  statsGrid: { display: 'flex', gap: '15px', marginBottom: '30px' },
  statCard: { background: '#1a1a1a', padding: '15px', borderRadius: '8px', flex: 1, borderLeft: '4px solid #3b82f6' },
  statLabel: { fontSize: '12px', color: '#888' },
  statPrice: { fontSize: '18px', fontWeight: 'bold' },
  mainSection: { background: '#111', padding: '20px', borderRadius: '12px', marginBottom: '30px' },
  controls: { marginBottom: '20px', display: 'flex', gap: '15px' },
  select: { padding: '10px', background: '#222', color: 'white', border: '1px solid #444', borderRadius: '5px' },
  predictBtn: { padding: '10px 20px', background: '#22c55e', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer', fontWeight: 'bold' },
  formSection: { background: '#161b22', padding: '20px', borderRadius: '12px', border: '1px solid #30363d', marginBottom: '30px' },
  tableSection: { background: '#111', padding: '20px', borderRadius: '10px' },
  table: { width: '100%', borderCollapse: 'collapse', marginTop: '10px' },
  tableHeader: { color: '#888', textAlign: 'left', borderBottom: '1px solid #333' },
  tableRow: { borderBottom: '1px solid #222' },
  badgeUp: { background: 'rgba(34, 197, 94, 0.1)', color: '#22c55e', padding: '4px 8px', borderRadius: '4px' },
  badgeStable: { background: 'rgba(234, 179, 8, 0.1)', color: '#eab308', padding: '4px 8px', borderRadius: '4px' },
};