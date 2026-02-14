import React, { useEffect, useState } from 'react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { 
    Users, 
    CalendarCheck, 
    CalendarX, 
    FileWarning, 
    CalendarDays,
    Clock,
    TrendingUp,
    AlertCircle,
    Loader2,
    ChevronRight,
    Search,
    BookOpen
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { cn } from '@/lib/utils';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from "@/components/ui/tooltip";

const StatCard = ({ title, value, icon, color, subtext }) => (
    <Card className="glass border-none shadow-sm relative overflow-hidden">
        <CardContent className="p-6">
            <div className="flex justify-between items-start">
                <div>
                    <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">
                        {title}
                    </p>
                    <h3 className={cn("text-2xl font-bold mb-1", color.text)}>
                        {value}
                    </h3>
                    {subtext && <p className="text-xs text-muted-foreground">{subtext}</p>}
                </div>
                <div className={cn("p-3 rounded-2xl shadow-sm", color.bg, color.icon)}>
                    {icon}
                </div>
            </div>
        </CardContent>
    </Card>
);

const TeacherDashboard = () => {
    const { user } = useAuth();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState(null);

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                const response = await api.get('/dashboard/teacher/stats');
                setData(response.data);
            } catch (error) {
                console.error("Failed to fetch dashboard data", error);
            } finally {
                setLoading(false);
            }
        };

        if (user?.sub) {
            fetchDashboardData(); 
            const intervalId = setInterval(fetchDashboardData, 30000); 
            return () => clearInterval(intervalId); 
        }
    }, [user]);

    if (loading) return (
        <div className="flex flex-col items-center justify-center h-[80vh] space-y-4">
            <Loader2 className="h-10 w-10 animate-spin text-blue-600" />
            <p className="text-muted-foreground font-medium">Preparing your classroom...</p>
        </div>
    );

    if (!data) return (
        <div className="flex flex-col items-center justify-center h-[80vh] text-center space-y-4">
            <AlertCircle className="h-12 w-12 text-red-500 opacity-50" />
            <h2 className="text-xl font-bold">Something went wrong</h2>
            <p className="text-muted-foreground">Failed to load dashboard data. Please refresh the page.</p>
            <Button onClick={() => window.location.reload()}>Try Again</Button>
        </div>
    );

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            <div className="flex flex-col space-y-2">
                <h2 className="text-3xl font-bold tracking-tight">Welcome, {user?.full_name || 'Teacher'}</h2>
                <p className="text-muted-foreground">Here's a summary of your classroom activity for today.</p>
            </div>

            {/* Overview Stats */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <StatCard 
                    title="Today's Date" 
                    value={data?.date} 
                    icon={<CalendarDays size={20} />} 
                    color={{ bg: 'bg-blue-50', text: 'text-blue-900', icon: 'text-blue-600' }} 
                />
                <StatCard 
                    title="Present Today" 
                    value={data?.overview?.present} 
                    icon={<CalendarCheck size={20} />} 
                    color={{ bg: 'bg-emerald-50', text: 'text-emerald-900', icon: 'text-emerald-600' }} 
                    subtext="Students in class"
                />
                <StatCard 
                    title="Absent Today" 
                    value={data?.overview?.absent} 
                    icon={<CalendarX size={20} />} 
                    color={{ bg: 'bg-red-50', text: 'text-red-900', icon: 'text-red-600' }} 
                    subtext="Students missing"
                />
                <StatCard 
                    title="Pending Marks" 
                    value={data?.overview?.pending_marks} 
                    icon={<FileWarning size={20} />} 
                    color={{ bg: 'bg-amber-50', text: 'text-amber-900', icon: 'text-amber-600' }} 
                    subtext="Classes pending entry"
                />
            </div>

            <div className="grid gap-6 md:grid-cols-12">
                {/* My Classes */}
                <Card className="md:col-span-7 glass border-none shadow-sm">
                    <CardHeader className="flex flex-row items-center justify-between">
                        <div>
                            <CardTitle>My Classes</CardTitle>
                            <CardDescription>Managed classroom list and actions.</CardDescription>
                        </div>
                        <BookOpen size={20} className="text-muted-foreground opacity-50" />
                    </CardHeader>
                    <CardContent>
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Class Name</TableHead>
                                    <TableHead className="text-right">Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {data?.classes?.map((cls) => (
                                    <TableRow key={cls.id}>
                                        <TableCell className="font-semibold">{cls.name}</TableCell>
                                        <TableCell className="text-right space-x-2">
                                            <Button 
                                                size="sm" 
                                                variant="outline"
                                                onClick={() => navigate('/teacher/attendance')}
                                            >
                                                Attendance
                                            </Button>
                                            <Button 
                                                size="sm" 
                                                variant="ghost"
                                                onClick={() => navigate('/teacher/attendance')}
                                            >
                                                Report
                                            </Button>
                                        </TableCell>
                                    </TableRow>
                                ))}
                                {(!data?.classes || data.classes.length === 0) && (
                                    <TableRow>
                                        <TableCell colSpan={2} className="h-24 text-center text-muted-foreground">
                                            No classes assigned.
                                        </TableCell>
                                    </TableRow>
                                )}
                            </TableBody>
                        </Table>
                    </CardContent>
                </Card>

                {/* Marks Status */}
                <Card className="md:col-span-5 glass border-none shadow-sm">
                    <CardHeader>
                        <CardTitle>Marks Entry Status</CardTitle>
                        <CardDescription>Progress for ongoing examination results.</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="space-y-4">
                            {data?.marks_status?.map((status, index) => (
                                <div key={index} className="flex items-center justify-between group">
                                    <div className="flex items-center space-x-4">
                                        <div className={cn(
                                            "p-2 rounded-full",
                                            status.status === 'Completed' ? "bg-emerald-100 text-emerald-600" : "bg-amber-100 text-amber-600"
                                        )}>
                                            {status.status === 'Completed' ? <CalendarCheck size={16} /> : <FileWarning size={16} />}
                                        </div>
                                        <div>
                                            <p className="text-sm font-bold leading-none mb-1">{status.exam_name}</p>
                                            <p className="text-xs text-muted-foreground">{status.class_name} • {status.progress} Entered</p>
                                        </div>
                                    </div>
                                    <Badge variant={status.status === 'Completed' ? 'default' : 'secondary'} className={cn(
                                        "h-6",
                                        status.status === 'Completed' ? "bg-emerald-500 hover:bg-emerald-600" : "bg-amber-100 text-amber-700 border-amber-200"
                                    )}>
                                        {status.status}
                                    </Badge>
                                </div>
                            ))}
                            {(!data?.marks_status || data.marks_status.length === 0) && (
                                <div className="text-center py-10 text-muted-foreground text-sm italic">
                                    No active exams found.
                                </div>
                            )}
                        </div>
                        <Button 
                            variant="ghost" 
                            className="w-full text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                            onClick={() => navigate('/teacher/marks')}
                        >
                            Go to Marks Manager
                            <ChevronRight size={16} className="ml-1" />
                        </Button>
                    </CardContent>
                </Card>
            </div>

            <div className="grid gap-6 md:grid-cols-12">
                {/* Recent Activity */}
                <Card className="md:col-span-4 glass border-none shadow-sm">
                    <CardHeader>
                        <CardTitle>Recent Activity</CardTitle>
                        <CardDescription>Your latest actions and updates.</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-6">
                            {data?.recent_activity?.map((activity, index) => (
                                <div key={index} className="flex gap-4">
                                    <div className="flex flex-col items-center">
                                        <div className="p-2 rounded-full bg-blue-100 text-blue-600">
                                            <Clock size={14} />
                                        </div>
                                        {index < data.recent_activity.length - 1 && (
                                            <div className="w-px h-full bg-blue-100 my-1" />
                                        )}
                                    </div>
                                    <div className="pb-4">
                                        <p className="text-sm font-semibold">{activity.title}</p>
                                        <p className="text-xs text-gray-500 my-1">{activity.desc}</p>
                                        <p className="text-[10px] text-muted-foreground uppercase tracking-wider">{activity.time}</p>
                                    </div>
                                </div>
                            ))}
                            {(!data?.recent_activity || data.recent_activity.length === 0) && (
                                <p className="text-sm text-muted-foreground italic text-center py-8">No recent activity.</p>
                            )}
                        </div>
                    </CardContent>
                </Card>

                {/* Performance Table */}
                <Card className="md:col-span-8 glass border-none shadow-sm overflow-hidden">
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <div>
                            <CardTitle>Student Performance</CardTitle>
                            <CardDescription>Overview of student engagement and grades.</CardDescription>
                        </div>
                        <div className="flex gap-2">
                            <Button variant="outline" size="sm">Export</Button>
                        </div>
                    </CardHeader>
                    <CardContent className="px-0">
                        <Table>
                            <TableHeader>
                                <TableRow className="bg-muted/30">
                                    <TableHead className="pl-6">Roll No</TableHead>
                                    <TableHead>Name</TableHead>
                                    <TableHead>Class</TableHead>
                                    <TableHead className="text-center">Attendance</TableHead>
                                    <TableHead className="text-center">Avg Marks</TableHead>
                                    <TableHead className="text-right pr-6">Status</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {data?.students?.map((student) => (
                                    <TableRow key={student.id} className="hover:bg-gray-50/50 transition-colors">
                                        <TableCell className="pl-6 font-mono text-xs">{student.roll_number}</TableCell>
                                        <TableCell className="font-semibold">{student.full_name}</TableCell>
                                        <TableCell>{student.class_name}</TableCell>
                                        <TableCell className="text-center">
                                            <Badge variant="outline" className={cn(
                                                "font-bold",
                                                student.attendance_pct < 75 ? "text-red-600 border-red-200 bg-red-50" : "text-emerald-600 border-emerald-200 bg-emerald-50"
                                            )}>
                                                {student.attendance_pct}%
                                            </Badge>
                                        </TableCell>
                                        <TableCell className="text-center font-bold text-gray-700">
                                            {student.avg_marks > 0 ? student.avg_marks : '-'}
                                        </TableCell>
                                        <TableCell className="text-right pr-6">
                                            <TooltipProvider>
                                                <Tooltip>
                                                    <TooltipTrigger asChild>
                                                        <div className="inline-flex">
                                                            {student.attendance_pct < 75 ? (
                                                                <AlertCircle size={18} className="text-red-500" />
                                                            ) : (
                                                                <TrendingUp size={18} className="text-emerald-500" />
                                                            )}
                                                        </div>
                                                    </TooltipTrigger>
                                                    <TooltipContent>
                                                        <p>{student.attendance_pct < 75 ? "Low Attendance Warning" : "Consistent Performance"}</p>
                                                    </TooltipContent>
                                                </Tooltip>
                                            </TooltipProvider>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};

export default TeacherDashboard;
