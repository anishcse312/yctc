import React from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import AdminLoginPage from "./pages/AdminLoginPage";
import AdminRegisterPage from "./pages/AdminRegisterPage";
import ForgotPage from "./pages/ForgotPage";
import HomePage from "./pages/HomePage";
import NotFoundPage from "./pages/NotFoundPage";
import OtpPage from "./pages/OtpPage";
import SetNewPasswordPage from "./pages/SetNewPasswordPage";
import AdminLayout from "./layouts/AdminLayout";
import DashboardPage from "./pages/admin/DashboardPage";
import SearchAllStudentsPage from "./pages/admin/SearchAllStudentsPage";
import StudentLateralAdmissionPage from "./pages/admin/StudentLateralAdmissionPage";
import SettingsPage from "./pages/admin/SettingsPage";

const App = () => (
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/admin-login" element={<AdminLoginPage />} />
      <Route path="/admin-register" element={<AdminRegisterPage />} />
      <Route path="/forgot" element={<ForgotPage />} />
      <Route path="/otp" element={<OtpPage />} />
      <Route path="/set-new-password" element={<SetNewPasswordPage />} />
      <Route path="/admin" element={<AdminLayout />}>
        <Route index element={<Navigate to="/admin/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="students">
          <Route path="search" element={<SearchAllStudentsPage />} />
          <Route path="lateralAdmissions" element={<StudentLateralAdmissionPage />} />
        </Route>
        <Route path="settings" element={<SettingsPage />} />
      </Route>
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  </BrowserRouter>
);

export default App;
