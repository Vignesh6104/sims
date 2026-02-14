import React, { useState, useEffect } from 'react';
import {
    User,
    School,
    CreditCard,
    CalendarCheck,
    ClipboardList,
    ChevronDown,
    Loader2,
    Info,
    TrendingUp,
    Clock
} from 'lucide-react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { 
    Card, 
    CardContent, 
    CardHeader, 
    CardTitle, 
    CardDescription 
} from "@/components/ui/card";
import { 
    Select, 
    SelectContent, 
    SelectItem, 
    SelectTrigger, 
    SelectValue 
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { cn } from '@/lib/utils';

const ParentDashboard = () => {
    const { user } = useAuth();
    const [children, setChildren] = useState([]);
    const [selectedChildId, setSelectedChildId] = useState('');
    const [childData, setChildData] = useState({
        attendance: [],
        marks: [],
        assignments: [],
        fees: []
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchChildren = async () => {
            try {
                const response = await api.get('/parents/my-children/');
                setChildren(response.data);
                if (response.data.length > 0) {
                    setSelectedChildId(String(response.data[0].id));
                }
            } catch (error) {
                console.error("Failed to fetch children");
            } finally {
                setLoading(false);
            }
        };
        fetchChildren();
    }, []);

    useEffect(() => {
        if (!selectedChildId) return;

        const fetchChildDetails = async () => {
            setLoading(true);
            try {
                const selectedChild = children.find(c => String(c.id) === selectedChildId);
                
                const [attendanceRes, marksRes, feesRes, assignmentsRes] = await Promise.all([
                   api.get(`/attendance/?student_id=${selectedChildId}`),
                   api.get(`/marks/student/${selectedChildId}/`),
                   api.get(`/fees/payments/student/${selectedChildId}/`),
                   selectedChild?.class_id ? api.get(`/assignments/class/${selectedChild.class_id}/`) : Promise.resolve({ data: [] })
                ]);

                setChildData({
                    attendance: attendanceRes.data,
                    marks: marksRes.data,
                    fees: feesRes.data,
                    assignments: assignmentsRes.data
                });

            } catch (error) {
                console.error("Failed to fetch child data", error);
            } finally {
                setLoading(false);
            }
        };

        fetchChildDetails();
    }, [selectedChildId, children]);

    const handleChildChange = (value) => {
        setSelectedChildId(value);
    };

    const selectedChild = children.find(c => String(c.id) === selectedChildId);

    if (loading && children.length === 0) return (
        <div className="flex flex-col items-center justify-center h-[80vh] space-y-4">
            <Loader2 className="h-10 w-10 animate-spin text-blue-600" />
            <p className="text-muted-foreground font-medium">Connecting to your records...</p>
        </div>
    );

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Parent Dashboard</h2>
                    <p className="text-muted-foreground">Monitor your child's academic progress and attendance.</p>
                </div>
                
                {children.length > 0 && (
                    <div className="w-full sm:w-[250px]">
                        <Select value={selectedChildId} onValueChange={handleChildChange}>
                            <SelectTrigger className="glass">
                                <SelectValue placeholder="Select Child" />
                            </SelectTrigger>
                            <SelectContent>
                                {children.map((child) => (
                                    <SelectItem key={child.id} value={String(child.id)}>
                                        {child.full_name} ({child.roll_number})
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>
                )}
            </div>

            {!selectedChild ? (
                <Card className="p-12 text-center bg-gray-50/50 border-dashed border-2">
                    <Info size={48} className="mx-auto text-muted-foreground opacity-20 mb-4" />
                    <p className="text-lg font-medium text-muted-foreground">No students linked to your account.</p>
                </Card>
            ) : (
                <div className="space-y-8">
                    <div className="grid gap-4 sm:grid-cols-2">
                        <Card className="glass border-none shadow-sm">
                            <CardContent className="p-6 flex items-center gap-4">
                                <div className="p-4 bg-blue-100 text-blue-600 rounded-2xl shadow-sm">
                                    <User size={24} />
                                </div>
                                <div>
                                    <p className="text-xs font-semibold text-muted-foreground uppercase tracking-widest mb-1">Student Name</p>
                                    <h3 className="text-xl font-bold text-blue-900">{selectedChild.full_name}</h3>
                                </div>
                            </CardContent>
                        </Card>
                        <Card className="glass border-none shadow-sm">
                            <CardContent className="p-6 flex items-center gap-4">
                                <div className="p-4 bg-emerald-100 text-emerald-600 rounded-2xl shadow-sm">
                                    <School size={24} />
                                </div>
                                <div>
                                    <p className="text-xs font-semibold text-muted-foreground uppercase tracking-widest mb-1">Current Class</p>
                                    <h3 className="text-xl font-bold text-emerald-900">{selectedChild.class_id || 'N/A'}</h3>
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    <Card className="border-none shadow-xl overflow-hidden glass">
                        <Tabs defaultValue="attendance" className="w-full">
                            <div className="px-6 pt-6">
                                <TabsList className="grid w-full grid-cols-4 bg-gray-100/50 p-1">
                                    <TabsTrigger value="attendance" className="gap-2">
                                        <CalendarCheck size={16} className="hidden sm:inline" />
                                        Attendance
                                    </TabsTrigger>
                                    <TabsTrigger value="marks" className="gap-2">
                                        <TrendingUp size={16} className="hidden sm:inline" />
                                        Marks
                                    </TabsTrigger>
                                    <TabsTrigger value="fees" className="gap-2">
                                        <CreditCard size={16} className="hidden sm:inline" />
                                        Fees
                                    </TabsTrigger>
                                    <TabsTrigger value="assignments" className="gap-2">
                                        <ClipboardList size={16} className="hidden sm:inline" />
                                        Assignments
                                    </TabsTrigger>
                                </TabsList>
                            </div>
                            
                            <div className="p-6">
                                <TabsContent value="attendance" className="mt-0 space-y-4">
                                    <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                                        Recent Attendance History
                                    </h3>
                                    {childData.attendance.length > 0 ? (
                                        <div className="grid gap-2">
                                            {childData.attendance.slice(0, 10).map((att) => (
                                                <div key={att.id} className="flex items-center justify-between p-4 bg-white/60 border border-white/80 rounded-xl shadow-sm hover:shadow-md transition-shadow">
                                                    <span className="font-semibold text-gray-700">{new Date(att.date).toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</span>
                                                    <Badge variant={att.status === 'present' ? 'default' : 'destructive'} className={cn(
                                                        "px-3 py-1 uppercase tracking-tighter font-bold",
                                                        att.status === 'present' ? "bg-emerald-500 hover:bg-emerald-600" : "bg-red-500 hover:bg-red-600"
                                                    )}>
                                                        {att.status}
                                                    </Badge>
                                                </div>
                                            ))}
                                        </div>
                                    ) : <p className="text-center py-10 text-muted-foreground italic">No attendance records found.</p>}
                                </TabsContent>

                                <TabsContent value="marks" className="mt-0">
                                    <h3 className="text-lg font-bold mb-4">Academic Results</h3>
                                    {childData.marks.length > 0 ? (
                                        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                                            {childData.marks.map((mark) => (
                                                <Card key={mark.id} className="bg-white border-none shadow-sm group hover:ring-2 hover:ring-blue-100 transition-all">
                                                    <CardContent className="p-6">
                                                        <p className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-2">{mark.subject}</p>
                                                        <div className="flex items-baseline gap-1">
                                                            <span className="text-3xl font-extrabold text-blue-600">{mark.score}</span>
                                                            <span className="text-lg font-medium text-gray-300">/ {mark.max_score}</span>
                                                        </div>
                                                        <div className="mt-4 w-full bg-gray-100 rounded-full h-1.5 overflow-hidden">
                                                            <div 
                                                                className="bg-blue-600 h-full rounded-full transition-all duration-1000" 
                                                                style={{ width: `${(mark.score / mark.max_score) * 100}%` }}
                                                            />
                                                        </div>
                                                    </CardContent>
                                                </Card>
                                            ))}
                                        </div>
                                    ) : <p className="text-center py-10 text-muted-foreground italic">No marks recorded yet.</p>}
                                </TabsContent>
                                
                                <TabsContent value="fees" className="mt-0">
                                    <h3 className="text-lg font-bold mb-4">Fee Payment Status</h3>
                                    {childData.fees.length > 0 ? (
                                        <div className="space-y-3">
                                            {childData.fees.map((fee) => (
                                                <div key={fee.id} className="flex items-center justify-between p-4 bg-white/60 border border-white/80 rounded-xl">
                                                    <div>
                                                        <p className="font-bold text-gray-800 text-lg">Amount: ${fee.amount}</p>
                                                        <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1">
                                                            <Clock size={12} />
                                                            Due Date: {fee.due_date}
                                                        </p>
                                                    </div>
                                                    <Badge className={cn(
                                                        "px-4 py-1 font-bold",
                                                        fee.status === 'paid' ? "bg-emerald-500" : "bg-amber-500"
                                                    )}>
                                                        {fee.status.toUpperCase()}
                                                    </Badge>
                                                </div>
                                            ))}
                                        </div>
                                    ) : <p className="text-center py-10 text-muted-foreground italic">No fee records found.</p>}
                                </TabsContent>

                                <TabsContent value="assignments" className="mt-0">
                                    <h3 className="text-lg font-bold mb-4">Classroom Assignments</h3>
                                    {childData.assignments.length > 0 ? (
                                        <div className="grid gap-4">
                                            {childData.assignments.map((assignment) => (
                                                <Card key={assignment.id} className="bg-white border-none shadow-sm hover:shadow-md transition-shadow">
                                                    <CardContent className="p-6">
                                                        <div className="flex justify-between items-start gap-4">
                                                            <div>
                                                                <h4 className="text-lg font-bold text-gray-800 mb-2">{assignment.title}</h4>
                                                                <p className="text-sm text-gray-600 leading-relaxed mb-4">{assignment.description}</p>
                                                                <Badge variant="secondary" className="bg-blue-50 text-blue-700 border-blue-100 gap-2">
                                                                    <Clock size={12} />
                                                                    Due: {assignment.due_date}
                                                                </Badge>
                                                            </div>
                                                        </div>
                                                    </CardContent>
                                                </Card>
                                            ))}
                                        </div>
                                    ) : <p className="text-center py-10 text-muted-foreground italic">No active assignments for this class.</p>}
                                </TabsContent>
                            </div>
                        </Tabs>
                    </Card>
                </div>
            )}
        </div>
    );
};

export default ParentDashboard;
