import axios from "axios";

// --- 1. الإعدادات الأساسية (الأسهل) ---
// قمنا بتثبيت الرابط ليتوافق مع إعدادات CORS في الباك إيند
const api = axios.create({
  baseURL: 'http://localhost:8000/api', 
  timeout: 15000, // مهلة الانتظار 15 ثانية
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

// --- 2. معترض الطلبات (Request Interceptor) - متوسط الصعوبة ---
// هذه الوظيفة تقوم بحقن توكن JWT في رأس كل طلب يخرج من المتصفح تلقائياً
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("user_token");
    if (token) {
      // إرسال التوكن بصيغة Bearer كما يتوقع FastAPI
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// --- 3. معترض الاستجابة (Response Interceptor) - الأكثر تعقيداً ---
// مراقبة الردود القادمة من السيرفر ومعالجة حالات فشل الصلاحيات (401)
api.interceptors.response.use(
  (response) => {
    // إذا كانت الاستجابة ناجحة، يتم تمريرها كما هي
    return response;
  },
  (error) => {
    // التحقق مما إذا كان الخطأ هو "غير مصرح به" (401 Unauthorized)
    if (error.response?.status === 401) {
      console.warn("Session expired or invalid token. Logging out...");
      
      // تنظيف كل البيانات المتعلقة بالمستخدم عند انتهاء الجلسة
      localStorage.removeItem("user_token");
      localStorage.removeItem("user_role");
      localStorage.removeItem("username");

      // توجيه المستخدم لصفحة تسجيل الدخول فوراً
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }

    // تمرير الخطأ لبقية الكود للتعامل معه (مثل عرض رسالة خطأ للمستخدم)
    return Promise.reject(error);
  }
);

export default api;