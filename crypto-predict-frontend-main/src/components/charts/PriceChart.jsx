import React, { useState, useEffect } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import api from "../../services/api";

export default function PriceChart({ coin, range }) {
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        // 1. استدعاء مسار الأسعار الفعلية (UC-06)
        const priceRes = await api.get(`/prices/${coin}?timeframe=${range}`);
        
        // 2. استدعاء مسار التوقعات (UC-07)
        // ملاحظة: هذا المسار يجب أن يكون مجهزاً في الباك إيند
        const predictRes = await api.get(`/predict/${coin}?timeframe=${range}`);

        // 3. دمج البيانات بناءً على محور الوقت (UC-07 Step 3)
        // نفترض أن الباك إيند يرسل بيانات مرتبة زمنياً
        const combined = priceRes.data.map((item, index) => {
          return {
            time: new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            actual: parseFloat(item.close),
            // ربط نقاط التوقع بنقاط الوقت المقابلة لها للمقارنة البصرية
            predicted: predictRes.data[index] ? parseFloat(predictRes.data[index].predicted_value) : null
          };
        }).reverse();

        setChartData(combined);
      } catch (err) {
        console.error("Data fetch error:", err);
        setError("Unable to load chart or prediction data."); // EX1 صفحة 7
      } finally {
        setLoading(false);
      }
    };

    if (coin) fetchData();
  }, [coin, range]);

  if (loading) return <div>Loading real-time insights...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;

  return (
    <div className="chart-wrapper">
      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.1)" />
          <XAxis dataKey="time" tick={{ fill: "#9CA3AF", fontSize: 11 }} />
          <YAxis 
            domain={['auto', 'auto']} 
            tick={{ fill: "#9CA3AF", fontSize: 11 }}
            tickFormatter={(value) => `$${value.toLocaleString()}`}
          />
          <Tooltip 
            contentStyle={{ backgroundColor: "#1f2937", border: "none", color: "#f3f4f6" }}
            formatter={(value) => [`$${value}`, ""]}
          />
          <Legend verticalAlign="top" height={36} />

          {/* خط السعر الفعلي - متصل */}
          <Line
            type="monotone"
            dataKey="actual"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={false}
            name="Actual Price"
          />

          {/* خط التوقعات - متقطع (UC-07 Step 4) */}
          <Line
            type="monotone"
            dataKey="predicted"
            stroke="#22c55e"
            strokeWidth={2}
            strokeDasharray="5 5" // تمثيل التوقع بخط متقطع كما في التقرير
            dot={false}
            name="AI Prediction"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}