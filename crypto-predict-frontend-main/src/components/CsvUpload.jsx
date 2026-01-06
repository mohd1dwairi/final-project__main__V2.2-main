import React, { useState } from "react";
import api from "../services/api";

export default function CsvUpload() {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);

  // دالة لمعالجة اختيار الملف
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  // دالة إرسال الملف إلى الباك إيند
  const handleUpload = async () => {
    if (!file) {
      alert("Please select a CSV file first!");
      return;
    }

    const formData = new FormData();
    formData.append("file", file); // إرفاق الملف بصيغة Multipart

    setIsUploading(true);
    try {
      const response = await api.post("/prices/upload-csv", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      alert(response.data.message);
      setFile(null); // تفريغ الحقل بعد النجاح
    } catch (error) {
      console.error("Upload failed:", error);
      alert("Failed to upload CSV. Check file format.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div style={styles.uploadCard}>
      <h3 style={styles.title}>Bulk Data Upload (CSV)</h3>
      <p style={styles.subtitle}>Upload historical price data in bulk to power the AI engine.</p>
      
      <div style={styles.inputGroup}>
        <input 
          type="file" 
          accept=".csv" 
          onChange={handleFileChange} 
          style={styles.fileInput}
        />
        <button 
          onClick={handleUpload} 
          disabled={isUploading} 
          style={styles.uploadBtn}
        >
          {isUploading ? "Uploading..." : "Upload CSV 📤"}
        </button>
      </div>
    </div>
  );
}

// تنسيقات المكون
const styles = {
  uploadCard: { background: "#161b22", padding: "20px", borderRadius: "12px", border: "1px solid #30363d", marginTop: "20px" },
  title: { margin: "0 0 10px 0", fontSize: "18px", color: "#fff" },
  subtitle: { color: "#8b949e", fontSize: "14px", marginBottom: "20px" },
  inputGroup: { display: "flex", alignItems: "center", gap: "10px" },
  fileInput: { background: "#0d1117", color: "#c9d1d9", padding: "10px", borderRadius: "6px", border: "1px solid #30363d", flex: 1 },
  uploadBtn: { background: "#238636", color: "#fff", border: "none", padding: "12px 20px", borderRadius: "6px", cursor: "pointer", fontWeight: "bold" }
};