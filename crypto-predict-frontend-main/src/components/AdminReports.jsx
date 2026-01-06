import React, { useState, useEffect } from 'react';
import api from '../services/api';

export default function AdminReports() {
  const [stats, setStats] = useState({});
  const [accuracyData, setAccuracyData] = useState([]);

  // جلب إحصائيات النظام عند التحميل
  useEffect(() => {
    api.get('/admin/stats').then(res => setStats(res.data));
    api.get('/admin/accuracy-report/btc').then(res => setAccuracyData(res.data));
  }, []);

  // دالة الطباعة (تصدير التقرير)
  const handlePrint = () => {
    window.print(); // تفتح نافذة الطباعة/الحفظ كـ PDF للمتصفح
  };

  return (
    <div className="admin-reports-container" style={{ color: 'white', padding: '20px' }}>
      <h2>📊 System Administration & Reports</h2>
      
      {/* 1. بطاقات الإحصائيات (System Stats) */}
      <div style={{ display: 'flex', gap: '20px', marginBottom: '30px' }}>
        <div style={cardStyle}>
          <h4>Total Users</h4>
          <p style={{ fontSize: '24px' }}>{stats.users_count}</p>
        </div>
        <div style={cardStyle}>
          <h4>Data Records (OHLCV)</h4>
          <p style={{ fontSize: '24px' }}>{stats.data_records}</p>
        </div>
        <div style={cardStyle}>
          <h4>Total Predictions</h4>
          <p style={{ fontSize: '24px' }}>{stats.predictions_made}</p>
        </div>
      </div>

      {/* 2. جدول دقة التوقع (Accuracy Report) */}
      <div id="printable-area" style={{ background: '#111', padding: '20px', borderRadius: '10px' }}>
        <h3>🎯 AI Model Accuracy Report (Backtesting)</h3>
        <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #333', textAlign: 'left' }}>
              <th>Timestamp</th>
              <th>Predicted ($)</th>
              <th>Actual ($)</th>
              <th>Accuracy (%)</th>
            </tr>
          </thead>
          <tbody>
            {accuracyData.map((row, i) => (
              <tr key={i} style={{ borderBottom: '1px solid #222' }}>
                <td>{new Date(row.time).toLocaleString()}</td>
                <td>{row.predicted}</td>
                <td>{row.actual}</td>
                <td style={{ color: row.accuracy > 90 ? '#22c55e' : '#eab308' }}>
                  {row.accuracy}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* زر تصدير التقرير */}
      <button onClick={handlePrint} style={btnStyle}>
        Export Report (PDF/Print) 🖨️
      </button>
    </div>
  );
}

const cardStyle = { background: '#1a1a1a', padding: '20px', borderRadius: '10px', flex: 1, textAlign: 'center', border: '1px solid #333' };
const btnStyle = { marginTop: '20px', padding: '10px 20px', backgroundColor: '#3b82f6', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' };