import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';
import Login from './pages/Login';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import AboutUs from './pages/AboutUs';
import PublicLayout from './components/PublicLayout';
import AdminDashboard from './pages/AdminDashboard';
import Teachers from './pages/admin/Teachers';
import Students from './pages/admin/Students';
import Admins from './pages/admin/Admins';
import Classes from './pages/admin/Classes';
import Subjects from './pages/admin/Subjects';
import Exams from './pages/admin/Exams';
import AdminFees from './pages/admin/Fees';
import AdminTimetable from './pages/admin/Timetable';
import Notifications from './pages/Notifications';
import TeacherDashboard from './pages/TeacherDashboard';
import TeacherAttendance from './pages/teacher/Attendance';
import TeacherMarks from './pages/teacher/Marks';
import TeacherAssignments from './pages/teacher/Assignments';
import StudentDashboard from './pages/StudentDashboard';
import StudentAttendance from './pages/student/Attendance';
import StudentMarks from './pages/student/Marks';
import StudentAssignments from './pages/student/Assignments';
import NotFound from './pages/NotFound';
import Calendar from './pages/Calendar';
import Library from './pages/admin/Library';
import LibraryCatalog from './pages/LibraryCatalog';
import ParentDashboard from './pages/ParentDashboard';

// Placeholders for now, will implement later
const Placeholder = ({ title }) => <h2>{title} Page (Coming Soon)</h2>;

function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/about" replace />} />

      {/* Public Routes with Header and Footer */}
      <Route element={<PublicLayout />}>
        <Route path="/login" element={<Login />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/about" element={<AboutUs />} />
      </Route>

      {/* Admin Routes */}
      <Route element={<ProtectedRoute allowedRoles={['admin']} />}>
        <Route path="/admin" element={<Layout />}>
          <Route index element={<AdminDashboard />} />
          <Route path="admins" element={<Admins />} />
          <Route path="teachers" element={<Teachers />} />
          <Route path="students" element={<Students />} />
          <Route path="classes" element={<Classes />} />
          <Route path="subjects" element={<Subjects />} />
          <Route path="exams" element={<Exams />} />
          <Route path="fees" element={<AdminFees />} />
          <Route path="timetable" element={<AdminTimetable />} />
          <Route path="notifications" element={<Notifications />} />
          <Route path="calendar" element={<Calendar />} />
          <Route path="library" element={<Library />} />
        </Route>
      </Route>

      {/* Teacher Routes */}
      <Route element={<ProtectedRoute allowedRoles={['teacher']} />}>
        <Route path="/teacher" element={<Layout />}>
          <Route index element={<TeacherDashboard />} />
          <Route path="attendance" element={<TeacherAttendance />} />
          <Route path="marks" element={<TeacherMarks />} />
          <Route path="assignments" element={<TeacherAssignments />} />
          <Route path="notifications" element={<Notifications />} />
          <Route path="calendar" element={<Calendar />} />
          <Route path="library" element={<LibraryCatalog />} />
        </Route>
      </Route>

      {/* Student Routes */}
      <Route element={<ProtectedRoute allowedRoles={['student']} />}>
        <Route path="/student" element={<Layout />}>
          <Route index element={<StudentDashboard />} />
          <Route path="attendance" element={<StudentAttendance />} />
          <Route path="marks" element={<StudentMarks />} />
          <Route path="assignments" element={<StudentAssignments />} />
          <Route path="notifications" element={<Notifications />} />
          <Route path="calendar" element={<Calendar />} />
          <Route path="library" element={<LibraryCatalog />} />
        </Route>
      </Route>

      {/* Parent Routes */}
      <Route element={<ProtectedRoute allowedRoles={['parent']} />}>
        <Route path="/parent" element={<Layout />}>
          <Route index element={<ParentDashboard />} />
          <Route path="notifications" element={<Notifications />} />
          <Route path="calendar" element={<Calendar />} />
        </Route>
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}

export default App;
