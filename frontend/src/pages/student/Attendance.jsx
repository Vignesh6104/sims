import React, { useState, useEffect } from 'react';
import { 
    CalendarCheck, 
    CalendarX, 
    Clock, 
    Filter,
    ArrowUpRight,
    Loader2,
    CalendarDays
} from 'lucide-react';
import api from '../../api/axios';
import { useAuth } from '../../context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { 
    Table, 
    TableBody, 
    TableCell, 
    TableHead, 
    TableHeader, 
    TableRow 
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { cn } from '@/lib/utils';

const Attendance = () => {
    const { user } = useAuth();
    const [attendance, setAttendance] = useState([]);
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({ present: 0, absent: 0, late: 0, total: 0, percentage: 0 });

    useEffect(() => {
        const fetchAttendance = async () => {
            try {
                const response = await api.get(`/attendance/?student_id=${user.sub}`);
                setAttendance(response.data);
                
                const total = response.data.length;
                const present = response.data.filter(r => r.status === 'present').length;
                const absent = response.data.filter(r => r.status === 'absent').length;
                const late = response.data.filter(r => r.status === 'late').length;
                
                const percentage = total > 0 ? Math.round(((present + (late * 0.5)) / total) * 100) : 0;
                
                setStats({ present, absent, late, total, percentage });
            } catch (error) {
                console.error("Failed to fetch attendance", error);
            } finally {
                setLoading(false);
            }
        };

        if (user?.sub) fetchAttendance();
    }, [user]);

    const getStatusBadge = (status) => {
        switch (status) {
            case 'present': return <Badge variant="outline" className="bg-emerald-50 text-emerald-700 border-emerald-200">Present</Badge>;
            case 'absent': return <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200">Absent</Badge>;
            case 'late': return <Badge variant="outline" className="bg-amber-50 text-amber-700 border-amber-200">Late</Badge>;
            default: return <Badge variant="outline">{status}</Badge>;
        }
    };

    if (loading) return (
        <div className="flex flex-col items-center justify-center h-[80vh] space-y-4">
            <Loader2 className="h-10 w-10 animate-spin text-blue-600" />
            <p className="text-muted-foreground font-medium">Gathering your attendance log...</p>
        </div>
    );

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            <div className="flex flex-col space-y-2">
                <h2 className="text-3xl font-bold tracking-tight">My Attendance</h2>
                <p className="text-muted-foreground">Detailed overview of your classroom presence and punctuality.</p>
            </div>

            <div className="grid gap-6 md:grid-cols-12">
                {/* Percentage Card */}
                <Card className="md:col-span-4 bg-blue-600 border-none shadow-xl text-white overflow-hidden relative">
                    <CardContent className="p-8 flex flex-col items-center text-center h-full justify-center relative z-10">
                        <div className="text-6xl font-black mb-2">{stats.percentage}%</div>
                        <p className="text-blue-100 font-medium uppercase tracking-widest text-xs mb-6">Overall Attendance</p>
                        <Badge className={cn(
                            "px-4 py-1.5 rounded-full font-bold shadow-lg border-none",
                            stats.percentage >= 75 ? "bg-white text-emerald-600" : "bg-white text-red-600"
                        )}>
                            {stats.percentage >= 75 ? "Good Standing" : "Attendance Shortage"}
                        </Badge>
                    </CardContent>
                    {/* Background decorations */}
                    <div className="absolute -bottom-10 -right-10 w-40 h-40 bg-blue-500 rounded-full opacity-50 blur-3xl" />
                    <div className="absolute -top-10 -left-10 w-40 h-40 bg-blue-700 rounded-full opacity-50 blur-3xl" />
                </Card>

                {/* Summary Details */}
                <Card className="md:col-span-8 glass border-none shadow-sm">
                    <CardHeader>
                        <CardTitle>Attendance Summary</CardTitle>
                        <CardDescription>Breakdown of working days and your status counts.</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-8">
                        <div className="grid gap-4 grid-cols-3">
                            <div className="p-4 rounded-2xl bg-gray-50 border border-gray-100 text-center">
                                <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
                                <p className="text-[10px] uppercase font-bold text-muted-foreground tracking-tighter">Working Days</p>
                            </div>
                            <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-100 text-center">
                                <p className="text-2xl font-bold text-emerald-600">{stats.present}</p>
                                <p className="text-[10px] uppercase font-bold text-emerald-700 tracking-tighter">Present</p>
                            </div>
                            <div className="p-4 rounded-2xl bg-red-50 border border-red-100 text-center">
                                <p className="text-2xl font-bold text-red-600">{stats.absent}</p>
                                <p className="text-[10px] uppercase font-bold text-red-700 tracking-tighter">Absent</p>
                            </div>
                        </div>
                        
                        <div className="space-y-3">
                            <div className="flex justify-between items-end">
                                <p className="text-sm font-semibold text-gray-600">Compliance Progress</p>
                                <p className="text-sm font-bold text-blue-600">{stats.percentage}%</p>
                            </div>
                            <Progress value={stats.percentage} className="h-3" />
                            <p className="text-[11px] text-muted-foreground">
                                Minimum 75% attendance is required for examination eligibility.
                            </p>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Detailed Table */}
            <Card className="border-none shadow-xl overflow-hidden bg-white">
                <CardHeader className="bg-gray-50/50 border-b">
                    <CardTitle className="text-lg">Monthly Attendance Log</CardTitle>
                </CardHeader>
                <Table>
                    <TableHeader>
                        <TableRow className="bg-muted/30">
                            <TableHead className="pl-6">Date</TableHead>
                            <TableHead>Day</TableHead>
                            <TableHead>Status</TableHead>
                            <TableHead>Class</TableHead>
                            <TableHead className="pr-6 text-right">Remarks</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {attendance.length > 0 ? attendance.map((record) => (
                            <TableRow key={record.id} className="hover:bg-gray-50/50 group transition-colors">
                                <TableCell className="pl-6 font-medium">
                                    {new Date(record.date).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })}
                                </TableCell>
                                <TableCell className="text-muted-foreground">
                                    {new Date(record.date).toLocaleDateString('en-US', { weekday: 'long' })}
                                </TableCell>
                                <TableCell>{getStatusBadge(record.status)}</TableCell>
                                <TableCell>Class A</TableCell>
                                <TableCell className="pr-6 text-right text-gray-500 italic text-sm">
                                    {record.remarks || '-'}
                                </TableCell>
                            </TableRow>
                        )) : (
                            <TableRow>
                                <TableCell colSpan={5} className="h-48 text-center text-muted-foreground italic">
                                    No attendance records found for your account.
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </Card>
        </div>
    );
};

export default Attendance;
