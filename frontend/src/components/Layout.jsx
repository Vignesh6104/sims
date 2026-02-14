import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { cn } from '@/lib/utils';
import {
    LayoutDashboard,
    Users,
    UserCog,
    GraduationCap,
    School,
    BookOpen,
    ClipboardList,
    CalendarDays,
    Library,
    BarChart3,
    Bell,
    Menu,
    LogOut,
    User,
    ChevronRight,
    Search,
    MessageSquare,
    MessageCircle,
    ClipboardCheck,
    Banknote,
    Package,
    History
} from 'lucide-react';
import {
    Avatar,
    AvatarFallback,
    AvatarImage,
} from "@/components/ui/avatar";
import {
    Button,
} from "@/components/ui/button";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from "@/components/ui/tooltip";
import { Separator } from "@/components/ui/separator";

const drawerWidth = 240;

const Layout = () => {
    const { user, role, logout } = useAuth();
    const [mobileOpen, setMobileOpen] = useState(false);
    const navigate = useNavigate();
    const location = useLocation();

    // Close mobile drawer on navigation
    useEffect(() => {
        setMobileOpen(false);
    }, [location]);

    const handleLogout = () => {
        logout();
    };

    const menuItems = {
        admin: [
            { text: 'Dashboard', icon: <LayoutDashboard size={20} />, path: '/admin' },
            { text: 'Admins', icon: <UserCog size={20} />, path: '/admin/admins' },
            { text: 'Teachers', icon: <Users size={20} />, path: '/admin/teachers' },
            { text: 'Students', icon: <GraduationCap size={20} />, path: '/admin/students' },
            { text: 'Classes', icon: <School size={20} />, path: '/admin/classes' },
            { text: 'Subjects', icon: <BookOpen size={20} />, path: '/admin/subjects' },
            { text: 'Exams', icon: <ClipboardList size={20} />, path: '/admin/exams' },
            { text: 'Timetable', icon: <CalendarDays size={20} />, path: '/admin/timetable' },
            { text: 'Calendar', icon: <CalendarDays size={20} />, path: '/admin/calendar' },
            { text: 'Library', icon: <Library size={20} />, path: '/admin/library' },
            { text: 'Fees', icon: <BarChart3 size={20} />, path: '/admin/fees' },
            { text: 'Leaves', icon: <History size={20} />, path: '/admin/leaves' },
            { text: 'Feedbacks', icon: <MessageSquare size={20} />, path: '/admin/feedbacks' },
            { text: 'Salaries', icon: <Banknote size={20} />, path: '/admin/salaries' },
            { text: 'Assets', icon: <Package size={20} />, path: '/admin/assets' },
            { text: 'Messages', icon: <MessageCircle size={20} />, path: '/admin/messages' },
            { text: 'Notifications', icon: <Bell size={20} />, path: '/admin/notifications' },
            { text: 'Profile', icon: <User size={20} />, path: '/admin/profile' },
        ],
        teacher: [
            { text: 'Dashboard', icon: <LayoutDashboard size={20} />, path: '/teacher' },
            { text: 'Attendance', icon: <ClipboardList size={20} />, path: '/teacher/attendance' },
            { text: 'Marks', icon: <BarChart3 size={20} />, path: '/teacher/marks' },
            { text: 'Assignments', icon: <ClipboardList size={20} />, path: '/teacher/assignments' },
            { text: 'Quizzes', icon: <ClipboardCheck size={20} />, path: '/teacher/quizzes' },
            { text: 'Leaves', icon: <History size={20} />, path: '/teacher/leaves' },
            { text: 'Feedbacks', icon: <MessageSquare size={20} />, path: '/teacher/feedbacks' },
            { text: 'Assets', icon: <Package size={20} />, path: '/teacher/assets' },
            { text: 'Messages', icon: <MessageCircle size={20} />, path: '/teacher/messages' },
            { text: 'Calendar', icon: <CalendarDays size={20} />, path: '/teacher/calendar' },
            { text: 'Library', icon: <Library size={20} />, path: '/teacher/library' },
            { text: 'Notifications', icon: <Bell size={20} />, path: '/teacher/notifications' },
            { text: 'Profile', icon: <User size={20} />, path: '/teacher/profile' },
        ],
        student: [
            { text: 'Dashboard', icon: <LayoutDashboard size={20} />, path: '/student' },
            { text: 'Attendance', icon: <ClipboardList size={20} />, path: '/student/attendance' },
            { text: 'Marks', icon: <BarChart3 size={20} />, path: '/student/marks' },
            { text: 'Assignments', icon: <ClipboardList size={20} />, path: '/student/assignments' },
            { text: 'Quizzes', icon: <ClipboardCheck size={20} />, path: '/student/quizzes' },
            { text: 'Leaves', icon: <History size={20} />, path: '/student/leaves' },
            { text: 'Feedbacks', icon: <MessageSquare size={20} />, path: '/student/feedbacks' },
            { text: 'Messages', icon: <MessageCircle size={20} />, path: '/student/messages' },
            { text: 'Calendar', icon: <CalendarDays size={20} />, path: '/student/calendar' },
            { text: 'Library', icon: <Library size={20} />, path: '/student/library' },
            { text: 'Notifications', icon: <Bell size={20} />, path: '/student/notifications' },
            { text: 'Profile', icon: <User size={20} />, path: '/student/profile' },
        ],
        parent: [
            { text: 'Dashboard', icon: <LayoutDashboard size={20} />, path: '/parent' },
            { text: 'Feedbacks', icon: <MessageSquare size={20} />, path: '/parent/feedbacks' },
            { text: 'Messages', icon: <MessageCircle size={20} />, path: '/parent/messages' },
            { text: 'Calendar', icon: <CalendarDays size={20} />, path: '/parent/calendar' },
            { text: 'Notifications', icon: <Bell size={20} />, path: '/parent/notifications' },
            { text: 'Profile', icon: <User size={20} />, path: '/parent/profile' },
        ],
    };

    const sidebarContent = (
        <div className="flex flex-col h-full bg-white border-r">
            <div className="p-6 text-center bg-gradient-to-br from-blue-600 to-blue-800 text-white m-2 rounded-2xl shadow-md">
                <Avatar className="w-20 h-20 mx-auto mb-4 border-2 border-white/30 bg-white/20">
                    <AvatarImage src={user?.profile_image} />
                    <AvatarFallback className="text-2xl font-bold bg-transparent text-white">
                        {user?.full_name?.charAt(0).toUpperCase() || 'U'}
                    </AvatarFallback>
                </Avatar>
                <h2 className="text-lg font-bold truncate">{user?.full_name}</h2>
                <p className="text-xs uppercase tracking-widest opacity-80 mt-1">{role}</p>
            </div>
            
            <nav className="flex-1 px-4 py-4 overflow-y-auto">
                <ul className="space-y-1">
                    {(menuItems[role] || []).map((item) => (
                        <li key={item.text}>
                            <button
                                onClick={() => navigate(item.path)}
                                className={cn(
                                    "flex items-center w-full px-4 py-2.5 rounded-xl transition-all duration-200 group",
                                    location.pathname === item.path
                                        ? "bg-blue-50 text-blue-600"
                                        : "text-gray-600 hover:bg-gray-100"
                                )}
                            >
                                <span className={cn(
                                    "mr-3 transition-colors",
                                    location.pathname === item.path ? "text-blue-600" : "text-gray-400 group-hover:text-gray-600"
                                )}>
                                    {item.icon}
                                </span>
                                <span className="font-medium text-sm">{item.text}</span>
                                {location.pathname === item.path && (
                                    <ChevronRight size={16} className="ml-auto" />
                                )}
                            </button>
                        </li>
                    ))}
                </ul>
            </nav>
        </div>
    );

    return (
        <div className="flex min-h-screen bg-gray-50/50">
            {/* Desktop Sidebar */}
            <aside className="hidden sm:block w-[240px] fixed h-screen z-20">
                {sidebarContent}
            </aside>

            {/* Mobile Drawer Overlay */}
            {mobileOpen && (
                <div 
                    className="fixed inset-0 bg-black/50 z-30 sm:hidden"
                    onClick={() => setMobileOpen(false)}
                />
            )}

            {/* Mobile Sidebar */}
            <aside className={cn(
                "fixed top-0 left-0 h-screen w-[240px] z-40 bg-white transition-transform duration-300 sm:hidden",
                mobileOpen ? "translate-x-0" : "-translate-x-full"
            )}>
                {sidebarContent}
            </aside>

            <div className="flex-1 flex flex-col sm:pl-[240px]">
                <header className="sticky top-0 z-10 bg-white/70 backdrop-blur-md border-b border-gray-200 px-4 sm:px-6 py-3 flex items-center justify-between">
                    <Button
                        variant="ghost"
                        size="icon"
                        className="sm:hidden"
                        onClick={() => setMobileOpen(true)}
                    >
                        <Menu size={24} />
                    </Button>

                    <div className="flex-1" />

                    <div className="flex items-center space-x-2">
                        <TooltipProvider>
                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        onClick={() => navigate(`/${role}/notifications`)}
                                        className="text-gray-600"
                                    >
                                        <Bell size={20} />
                                    </Button>
                                </TooltipTrigger>
                                <TooltipContent>
                                    <p>Notifications</p>
                                </TooltipContent>
                            </Tooltip>
                        </TooltipProvider>

                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <Button variant="ghost" className="relative h-10 w-10 rounded-full p-0">
                                    <Avatar className="h-9 w-9 border">
                                        <AvatarImage src={user?.profile_image} />
                                        <AvatarFallback className="bg-secondary text-secondary-foreground">
                                            {user?.full_name?.charAt(0).toUpperCase() || 'U'}
                                        </AvatarFallback>
                                    </Avatar>
                                </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent className="w-56" align="right" forceMount>
                                <DropdownMenuLabel className="font-normal">
                                    <div className="flex flex-col space-y-1">
                                        <p className="text-sm font-medium leading-none">{user?.full_name}</p>
                                        <p className="text-xs leading-none text-muted-foreground">{user?.email}</p>
                                    </div>
                                </DropdownMenuLabel>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem onClick={() => navigate(`/${role}/profile`)}>
                                    <User className="mr-2 h-4 w-4" />
                                    <span>Profile</span>
                                </DropdownMenuItem>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem onClick={handleLogout} className="text-red-600 focus:text-red-600">
                                    <LogOut className="mr-2 h-4 w-4" />
                                    <span>Log out</span>
                                </DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>
                    </div>
                </header>

                <main className="flex-1 p-4 sm:p-6 md:p-8">
                    <Outlet />
                </main>
            </div>
        </div>
    );
};

export default Layout;
