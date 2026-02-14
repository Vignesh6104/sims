import React, { useState, useEffect } from 'react';
import { 
    CalendarCheck, 
    ClipboardList, 
    Search, 
    ChevronRight, 
    Loader2, 
    CheckCircle2, 
    XCircle, 
    Clock,
    Filter
} from 'lucide-react';
import api from '../../api/axios';
import { useAuth } from '../../context/AuthContext';
import { useToast } from "@/components/ui/use-toast";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { 
    Table, 
    TableBody, 
    TableCell, 
    TableHead, 
    TableHeader, 
    TableRow 
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Badge } from "@/components/ui/badge";
import { cn } from '@/lib/utils';

const Attendance = () => {
    const { user } = useAuth();
    const [classes, setClasses] = useState([]);
    const [selectedClass, setSelectedIdClass] = useState('');
    
    // Mark Attendance State
    const [selectedDate, setSelectedDate] = useState(new Date().toLocaleDateString('en-CA')); // YYYY-MM-DD in local time
    const [students, setStudents] = useState([]);
    const [attendanceData, setAttendanceData] = useState({});
    
    // Report State
    const [reportData, setReportData] = useState([]);

    const [loading, setLoading] = useState(false);
    const { toast } = useToast();

    useEffect(() => {
        const fetchClasses = async () => {
            try {
                const response = await api.get(`/class_rooms/?teacher_id=${user.sub}`);
                setClasses(response.data);
            } catch (error) {
                console.error("Failed to fetch classes", error);
            }
        };
        if (user?.sub) fetchClasses();
    }, [user]);

    useEffect(() => {
        if (selectedClass) {
            fetchStudents(selectedClass);
            fetchReport(selectedClass);
        }
    }, [selectedClass]);

    const fetchStudents = async (classId) => {
        setLoading(true);
        try {
            const response = await api.get(`/students/?class_id=${classId}`);
            setStudents(response.data);
            const initialData = {};
            response.data.forEach(student => {
                initialData[student.id] = 'present';
            });
            setAttendanceData(initialData);
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to fetch student list",
                variant: "destructive",
            });
        } finally {
            setLoading(false);
        }
    };

    const fetchReport = async (classId) => {
        try {
            const response = await api.get(`/attendance/report/?class_id=${classId}`);
            setReportData(response.data);
        } catch (error) {
            console.error("Failed to fetch report");
        }
    };

    const handleAttendanceChange = (studentId, status) => {
        setAttendanceData(prev => ({
            ...prev,
            [studentId]: status
        }));
    };

    const handleSubmit = async () => {
        setLoading(true);
        try {
            const promises = students.map(student => {
                return api.post('/attendance/', {
                    student_id: student.id,
                    date: selectedDate,
                    status: attendanceData[student.id]
                });
            });
            
            await Promise.all(promises);
            toast({
                title: "Success",
                description: "Attendance marked successfully!",
            });
            fetchReport(selectedClass);
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to save attendance",
                variant: "destructive",
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <div className="flex flex-col space-y-2">
                <h2 className="text-3xl font-bold tracking-tight">Attendance Tracker</h2>
                <p className="text-muted-foreground">Log daily student presence or view class attendance reports.</p>
            </div>

            <Tabs defaultValue="mark" className="w-full">
                <TabsList className="grid w-full grid-cols-2 max-w-[400px] mb-8">
                    <TabsTrigger value="mark">Mark Attendance</TabsTrigger>
                    <TabsTrigger value="report">View Report</TabsTrigger>
                </TabsList>

                <Card className="glass border-none shadow-sm mb-6">
                    <CardContent className="pt-6">
                        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 items-end">
                            <div className="space-y-2">
                                <Label htmlFor="class-select">Select Class</Label>
                                <Select value={selectedClass} onValueChange={setSelectedIdClass}>
                                    <SelectTrigger id="class-select">
                                        <SelectValue placeholder="Choose a class" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {classes.map((cls) => (
                                            <SelectItem key={cls.id} value={String(cls.id)}>
                                                {cls.name}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                            
                            <TabsContent value="mark" className="m-0">
                                <div className="space-y-2">
                                    <Label htmlFor="date-select">Attendance Date</Label>
                                    <Input 
                                        id="date-select"
                                        type="date" 
                                        value={selectedDate} 
                                        onChange={(e) => setSelectedDate(e.target.value)}
                                    />
                                </div>
                            </TabsContent>
                        </div>
                    </CardContent>
                </Card>

                {selectedClass ? (
                    <div className="space-y-6">
                        <TabsContent value="mark" className="m-0">
                            <Card className="border-none shadow-xl overflow-hidden bg-white">
                                <Table>
                                    <TableHeader>
                                        <TableRow className="bg-muted/30">
                                            <TableHead className="pl-6">Roll No</TableHead>
                                            <TableHead>Student Name</TableHead>
                                            <TableHead className="text-center">Attendance Status</TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {loading ? (
                                            <TableRow>
                                                <TableCell colSpan={3} className="h-48 text-center">
                                                    <Loader2 className="h-8 w-8 animate-spin mx-auto text-blue-600 mb-2" />
                                                    <p className="text-muted-foreground">Fetching students...</p>
                                                </TableCell>
                                            </TableRow>
                                        ) : students.map((student) => (
                                            <TableRow key={student.id} className="hover:bg-gray-50/50">
                                                <TableCell className="pl-6 font-mono text-xs">{student.roll_number}</TableCell>
                                                <TableCell className="font-semibold">{student.full_name}</TableCell>
                                                <TableCell className="text-center">
                                                    <RadioGroup 
                                                        defaultValue="present"
                                                        value={attendanceData[student.id] || 'present'}
                                                        onValueChange={(val) => handleAttendanceChange(student.id, val)}
                                                        className="flex justify-center gap-6"
                                                    >
                                                        <div className="flex items-center space-x-2">
                                                            <RadioGroupItem value="present" id={`p-${student.id}`} className="text-emerald-600 border-emerald-600" />
                                                            <Label htmlFor={`p-${student.id}`} className="cursor-pointer text-emerald-700 font-bold">Present</Label>
                                                        </div>
                                                        <div className="flex items-center space-x-2">
                                                            <RadioGroupItem value="absent" id={`a-${student.id}`} className="text-red-600 border-red-600" />
                                                            <Label htmlFor={`a-${student.id}`} className="cursor-pointer text-red-700 font-bold">Absent</Label>
                                                        </div>
                                                        <div className="flex items-center space-x-2">
                                                            <RadioGroupItem value="late" id={`l-${student.id}`} className="text-amber-600 border-amber-600" />
                                                            <Label htmlFor={`l-${student.id}`} className="cursor-pointer text-amber-700 font-bold">Late</Label>
                                                        </div>
                                                    </RadioGroup>
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                                <div className="p-6 bg-gray-50/50 border-t flex justify-end">
                                    <Button size="lg" className="bg-blue-600 hover:bg-blue-700 h-12 px-8" onClick={handleSubmit} disabled={loading}>
                                        {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <CalendarCheck className="mr-2 h-5 w-5" />}
                                        Save Class Attendance
                                    </Button>
                                </div>
                            </Card>
                        </TabsContent>

                        <TabsContent value="report" className="m-0">
                            <Card className="border-none shadow-xl overflow-hidden bg-white">
                                <Table>
                                    <TableHeader>
                                        <TableRow className="bg-muted/30">
                                            <TableHead className="pl-6">Roll No</TableHead>
                                            <TableHead>Student Name</TableHead>
                                            <TableHead className="text-center">Total Days</TableHead>
                                            <TableHead className="text-center">Present</TableHead>
                                            <TableHead className="text-center">Absent</TableHead>
                                            <TableHead className="text-center">Late</TableHead>
                                            <TableHead className="text-right pr-6">Attendance %</TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {reportData.map((row) => {
                                            const percentage = row.total_days > 0 
                                                ? Math.round(((row.present + (row.late * 0.5)) / row.total_days) * 100) 
                                                : 0;
                                            return (
                                                <TableRow key={row.student_id} className="hover:bg-gray-50/50 transition-colors">
                                                    <TableCell className="pl-6 font-mono text-xs">{row.roll_number}</TableCell>
                                                    <TableCell className="font-semibold">{row.student_name}</TableCell>
                                                    <TableCell className="text-center font-medium">{row.total_days}</TableCell>
                                                    <TableCell className="text-center text-emerald-600 font-bold">{row.present}</TableCell>
                                                    <TableCell className="text-center text-red-600 font-bold">{row.absent}</TableCell>
                                                    <TableCell className="text-center text-amber-600 font-bold">{row.late}</TableCell>
                                                    <TableCell className="text-right pr-6">
                                                        <Badge variant="outline" className={cn(
                                                            "font-bold text-sm",
                                                            percentage < 75 ? "text-red-600 border-red-200 bg-red-50" : "text-emerald-600 border-emerald-200 bg-emerald-50"
                                                        )}>
                                                            {percentage}%
                                                        </Badge>
                                                    </TableCell>
                                                </TableRow>
                                            );
                                        })}
                                        {reportData.length === 0 && (
                                            <TableRow>
                                                <TableCell colSpan={7} className="h-48 text-center text-muted-foreground">
                                                    No attendance data found for this class.
                                                </TableCell>
                                            </TableRow>
                                        )}
                                    </TableBody>
                                </Table>
                            </Card>
                        </TabsContent>
                    </div>
                ) : (
                    <Card className="flex flex-col items-center justify-center py-24 bg-gray-50/50 border-dashed border-2">
                        <Filter size={48} className="text-muted-foreground opacity-20 mb-4" />
                        <p className="text-muted-foreground font-medium text-lg text-center">
                            Please select a class to start tracking attendance.
                        </p>
                    </Card>
                )}
            </Tabs>
        </div>
    );
};

export default Attendance;
