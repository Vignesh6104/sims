import React, { useEffect, useState } from 'react';
import api from '../api/axios';
import { 
    BarChart, 
    Bar, 
    XAxis, 
    YAxis, 
    CartesianGrid, 
    Tooltip as ChartTooltip, 
    Legend, 
    ResponsiveContainer, 
    PieChart, 
    Pie, 
    Cell 
} from 'recharts';
import { 
    GraduationCap, 
    Users, 
    School, 
    CalendarCheck, 
    TrendingUp,
    Loader2
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { cn } from '@/lib/utils';

const StatCard = ({ title, value, icon, color, description }) => (
    <Card className="glass relative overflow-hidden border-none shadow-sm">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
                {title}
            </CardTitle>
            <div className={cn("p-2 rounded-xl text-white shadow-sm", color)}>
                {icon}
            </div>
        </CardHeader>
        <CardContent>
            <div className="text-3xl font-bold">{value}</div>
            {description && <p className="text-xs text-muted-foreground mt-1">{description}</p>}
        </CardContent>
        {/* Decorative elements */}
        <div className={cn("absolute -bottom-6 -right-6 w-24 h-24 rounded-full opacity-10", color)} />
    </Card>
);

const AdminDashboard = () => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await api.get('/dashboard/stats');
                setStats(response.data);
            } catch (error) {
                console.error("Failed to fetch dashboard stats", error);
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
    }, []);

    if (loading) return (
        <div className="flex flex-col items-center justify-center h-[80vh] space-y-4">
            <Loader2 className="h-10 w-10 animate-spin text-blue-600" />
            <p className="text-muted-foreground font-medium">Loading dashboard data...</p>
        </div>
    );

    const pieData = [
        { name: 'Students', value: stats?.total_students || 0 },
        { name: 'Teachers', value: stats?.total_teachers || 0 },
    ];
    const COLORS = ['#2563eb', '#10b981'];

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            <div className="flex flex-col space-y-2">
                <h2 className="text-3xl font-bold tracking-tight">Dashboard Overview</h2>
                <p className="text-muted-foreground">Welcome back! Here's a snapshot of your school today.</p>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <StatCard 
                    title="Total Students" 
                    value={stats?.total_students || 0} 
                    icon={<GraduationCap size={20} />} 
                    color="bg-blue-600"
                    description="+2 this month"
                />
                <StatCard 
                    title="Total Teachers" 
                    value={stats?.total_teachers || 0} 
                    icon={<Users size={20} />} 
                    color="bg-emerald-600"
                    description="1 on leave"
                />
                <StatCard 
                    title="Total Classes" 
                    value={stats?.total_classes || 0} 
                    icon={<School size={20} />} 
                    color="bg-amber-600"
                    description="Primary & Secondary"
                />
                <StatCard 
                    title="Attendance Records" 
                    value={stats?.total_attendance_records || 0} 
                    icon={<CalendarCheck size={20} />} 
                    color="bg-violet-600"
                    description="Total history"
                />
            </div>

            <div className="grid gap-4 md:grid-cols-7">
                <Card className="md:col-span-4 glass border-none shadow-sm">
                    <CardHeader>
                        <CardTitle>Attendance Trends</CardTitle>
                        <CardDescription>Comparison of total students vs present count per class.</CardDescription>
                    </CardHeader>
                    <CardContent className="pl-2 h-[350px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={stats?.chart_data || []} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} opacity={0.3} />
                                <XAxis 
                                    dataKey="name" 
                                    stroke="#888888" 
                                    fontSize={12} 
                                    tickLine={false} 
                                    axisLine={false}
                                />
                                <YAxis 
                                    stroke="#888888" 
                                    fontSize={12} 
                                    tickLine={false} 
                                    axisLine={false} 
                                    tickFormatter={(value) => `${value}`}
                                />
                                <ChartTooltip 
                                    contentStyle={{ backgroundColor: 'white', borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)' }}
                                />
                                <Bar dataKey="students" name="Total Students" fill="#2563eb" radius={[4, 4, 0, 0]} barSize={30} />
                                <Bar dataKey="attendance" name="Attendance Count" fill="#10b981" radius={[4, 4, 0, 0]} barSize={30} />
                            </BarChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>

                <div className="md:col-span-3 space-y-4">
                    <Card className="glass border-none shadow-sm">
                        <CardHeader className="pb-2">
                            <CardTitle>User Distribution</CardTitle>
                        </CardHeader>
                        <CardContent className="h-[200px]">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={pieData}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={60}
                                        outerRadius={80}
                                        paddingAngle={5}
                                        dataKey="value"
                                    >
                                        {pieData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                        ))}
                                    </Pie>
                                    <ChartTooltip />
                                    <Legend />
                                </PieChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>

                    <Card className="glass border-none shadow-sm">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-base">Recent Activities</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                {stats?.recent_activities?.length > 0 ? (
                                    stats.recent_activities.map((activity, index) => (
                                        <div key={index} className="flex items-start space-x-3">
                                            <div className="mt-1 p-1.5 rounded-full bg-blue-100 text-blue-600">
                                                <TrendingUp size={12} />
                                            </div>
                                            <div className="space-y-1">
                                                <p className="text-sm font-medium leading-none">{activity.text}</p>
                                                <p className="text-xs text-muted-foreground">{activity.time}</p>
                                            </div>
                                        </div>
                                    ))
                                ) : (
                                    <p className="text-sm text-muted-foreground">No recent activities found.</p>
                                )}
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
};

export default AdminDashboard;
