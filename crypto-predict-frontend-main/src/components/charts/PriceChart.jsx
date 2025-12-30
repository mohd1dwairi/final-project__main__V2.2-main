import React from "react";
import Chart from "react-apexcharts";

export default function PriceChart({ historyData, predictionData, showPrediction }) {
  
  // تجهيز سلسلة البيانات (Series)
  const series = [
    {
      name: "Price History (OHLCV)",
      type: "candlestick",
      data: historyData // بيانات الشمعات من الباك إيند
    }
  ];

  // إضافة خط التوقع المتقطع إذا ضغط المستخدم الزر
  if (showPrediction && predictionData.length > 0) {
    series.push({
      name: "AI Prediction",
      type: "line",
      data: predictionData.map(p => ({
        x: new Date(p.timestamp).getTime(),
        y: p.predicted_value
      }))
    });
  }

  const options = {
    chart: { id: "crypto-chart", background: "transparent" },
    theme: { mode: "dark" },
    xaxis: { type: "datetime" },
    stroke: { 
        width: [1, 3], // سمك خط الشمعة ثم خط التوقع
        dashArray: [0, 5] // الخط الثاني (التوقع) سيكون متقطعاً
    },
    plotOptions: {
      candlestick: {
        colors: { upward: "#22c55e", downward: "#ef4444" }
      }
    },
    tooltip: { shared: true, theme: "dark" }
  };

  return (
    <div style={{ background: "#111", padding: "10px", borderRadius: "10px" }}>
      <Chart options={options} series={series} type="candlestick" height={350} />
    </div>
  );
}