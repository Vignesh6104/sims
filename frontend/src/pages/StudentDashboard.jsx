import React, { useEffect, useState } from 'react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { 
    CalendarCheck, 
    TrendingUp, 
    BookOpen, 
    Award,
    AlertCircle,
    CheckCircle2,
    Clock,
    User,
    Loader2
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { cn } from '@/lib/utils';

const StatCard = ({ title, value, icon, color, status }) => (
    <Card className="glass border-none shadow-sm relative overflow-hidden">
        <CardContent className="p-6">
            <div className="flex justify-between items-start mb-4">
                <div className={cn("p-4 rounded-2xl shadow-sm", color.bg, color.icon)}>
                    {icon}
                </div>
                {status && (
                    <Badge variant="outline" className={cn(
                        "font-bold uppercase tracking-tighter text-[10px]",
                        status === 'Good' ? "text-emerald-600 border-emerald-200 bg-emerald-50" : 
                        status === 'Warning' ? "text-amber-600 border-amber-200 bg-amber-50" : 
                        "text-red-600 border-red-200 bg-red-50"
                    )}>
                        {status}
                    </Badge>
                )}
            </div>
            <div>
                <p className="text-xs font-semibold text-muted-foreground uppercase tracking-widest mb-1">
                    {title}
                </p>
                <h3 className="text-3xl font-bold">{value}</h3>
            </div>
        </CardContent>
    </Card>
);

const StudentDashboard = () => {
    const { user } = useAuth();
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState(null);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await api.get('/dashboard/student/stats/');
                setData(response.data);
            } catch (error) {
                console.error("Failed to fetch student stats", error);
            } finally {
                setLoading(false);
            }
        };

        if (user?.sub) fetchStats();
    }, [user]);

    if (loading) return (
        <div className="flex flex-col items-center justify-center h-[80vh] space-y-4">
            <Loader2 className="h-10 w-10 animate-spin text-blue-600" />
            <p className="text-muted-foreground font-medium">Loading your academic record...</p>
        </div>
    );

    if (!data) return (
        <div className="flex flex-col items-center justify-center h-[80vh] text-center p-6">
            <AlertCircle className="h-12 w-12 text-red-500 opacity-50 mb-4" />
            <h2 className="text-xl font-bold">Data Unavailable</h2>
            <p className="text-muted-foreground">We couldn't retrieve your dashboard information.</p>
        </div>
    );

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            <div className="flex flex-col space-y-2">
                <h2 className="text-3xl font-bold tracking-tight">Welcome back, {user?.full_name}</h2>
                <div className="flex items-center gap-2 text-muted-foreground">
                    <BookOpen size={18} className="text-blue-600" />
                    <span className="font-medium">Class: {data.classroom.name}</span>
                </div>
            </div>

            {/* Alerts Section */}
            <div className="grid gap-4">
                {data.alerts.map((alert, index) => (
                    alert && (
                        <Alert key={index} variant={alert.type === 'warning' ? "destructive" : "default"} className={cn(
                            "border-none shadow-sm",
                            alert.type === 'success' ? "bg-emerald-50 text-emerald-900 border-l-4 border-l-emerald-500" : "bg-red-50 text-red-900 border-l-4 border-l-red-500"
                        )}>
                            {alert.type === 'warning' ? <AlertCircle className="h-4 w-4" /> : <CheckCircle2 className="h-4 w-4" />}
                            <AlertTitle className="font-bold">{alert.type === 'warning' ? 'Action Required' : 'Success'}</AlertTitle>
                            <AlertDescription>{alert.msg}</AlertDescription>
                        </Alert>
                    )
                ))}
            </div>

            {/* Overview Cards */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <StatCard 
                    title="Attendance" 
                    value={`${data.attendance.percentage}%`} 
                    icon={<CalendarCheck size={24} />} 
                    color={{ bg: 'bg-blue-50', icon: 'text-blue-600' }}
                    status={data.attendance.status}
                />
                <StatCard 
                    title="Avg Marks" 
                    value={data.marks.average} 
                    icon={<TrendingUp size={24} />} 
                    color={{ bg: 'bg-emerald-50', icon: 'text-emerald-600' }}
                />
                <StatCard 
                    title="Exams Taken" 
                    value={data.marks.total_exams} 
                    icon={<Award size={24} />} 
                    color={{ bg: 'bg-purple-50', icon: 'text-purple-600' }}
                />
                <StatCard 
                    title="Latest Result" 
                    value={data.marks.latest_result ? data.marks.latest_result.split(' ')[0] : 'N/A'} 
                    icon={<BookOpen size={24} />} 
                    color={{ bg: 'bg-amber-50', icon: 'text-amber-600' }}
                    status={data.marks.latest_result || 'N/A'}
                />
            </div>

            {/* Quick Summary Panel */}
            <Card className="glass border-none shadow-sm overflow-hidden">
                <CardHeader>
                    <CardTitle>Quick Summary</CardTitle>
                    <CardDescription>A brief look at your recent statistics.</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="grid gap-4 sm:grid-cols-3">
                        <div className="p-4 rounded-2xl bg-white/60 border border-white/80 shadow-inner flex items-center gap-4">
                            <div className="p-3 bg-blue-100 text-blue-600 rounded-xl">
                                <Clock size={20} />
                            </div>
                            <div>
                                <p className="text-xs text-muted-foreground font-medium uppercase tracking-tighter">Last Attendance</p>
                                <p className="text-base font-bold text-blue-900">
                                    {data.attendance.last_marked ? new Date(data.attendance.last_marked).toLocaleDateString() : 'N/A'}
                                </p>
                            </div>
                        </div>
                        <div className="p-4 rounded-2xl bg-white/60 border border-white/80 shadow-inner flex items-center gap-4">
                            <div className="p-3 bg-emerald-100 text-emerald-600 rounded-xl">
                                <TrendingUp size={20} />
                            </div>
                            <div>
                                <p className="text-xs text-muted-foreground font-medium uppercase tracking-tighter">Latest Exam</p>
                                <p className="text-base font-bold text-emerald-900">
                                    {data.marks.latest_result || 'N/A'}
                                </p>
                            </div>
                        </div>
                        <div className="p-4 rounded-2xl bg-white/60 border border-white/80 shadow-inner flex items-center gap-4">
                            <div className="p-3 bg-purple-100 text-purple-600 rounded-xl">
                                <User size={20} />
                            </div>
                            <div>
                                <p className="text-xs text-muted-foreground font-medium uppercase tracking-tighter">Class Teacher</p>
                                <p className="text-base font-bold text-purple-900">Assigned</p>
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};

export default StudentDashboard;
