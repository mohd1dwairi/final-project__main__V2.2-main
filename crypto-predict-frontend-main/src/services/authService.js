import api from "./api";

// تسجيل الدخول (UC-02 صفحة 5)
export const login = async ({ email, password }) => {
  // التعديل: إرسال كائن JSON مباشر بدلاً من URLSearchParams
  // ليتوافق مع LoginRequest (email, password) في الباك إيند
  const loginData = {
    email: email, 
    password: password,
  };

  const response = await api.post("/auth/login", loginData, {
    headers: {
      // التعديل: النوع يجب أن يكون application/json
      "Content-Type": "application/json",
    },
  });

  return response.data; // يعيد الـ access_token
};

// تسجيل الخروج (UC-03 Post-conditions)
export const logout = () => {
  // إزالة التوكن لإنهاء الجلسة
  localStorage.removeItem("user_token");
};
