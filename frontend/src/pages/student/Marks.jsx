import React, { useState, useEffect } from 'react';
import { 
    Award, 
    TrendingUp, 
    FileText, 
    Download,
    CheckCircle2,
    XCircle,
    Loader2,
    ClipboardList,
    Trophy,
    Target
} from 'lucide-react';
import api from '../../api/axios';
import { useAuth } from '../../context/AuthContext';
import { useToast } from "@/components/ui/use-toast";
import { Button } from "@/components/ui/button";
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
import { cn } from '@/lib/utils';

const StatCard = ({ title, value, icon, color }) => (
    <Card className="glass border-none shadow-sm overflow-hidden relative">
        <CardContent className="p-6">
            <div className="flex justify-between items-center">
                <div>
                    <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-1">{title}</p>
                    <h3 className="text-3xl font-extrabold">{value}</h3>
                </div>
                <div className={cn("p-4 rounded-2xl shadow-inner", color)}>
                    {icon}
                </div>
            </div>
        </CardContent>
    </Card>
);

const Marks = () => {
    const { user } = useAuth();
    const { toast } = useToast();
    const [marks, setMarks] = useState([]);
    const [submissions, setSubmissions] = useState([]);
    const [assignments, setAssignments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({ total_exams: 0, highest: 0, average: 0 });

    useEffect(() => {
        const fetchAllData = async () => {
            try {
                const [marksRes, submissionsRes] = await Promise.all([
                    api.get(`/marks/student/${user.sub}`),
                    api.get('/assignments/my-submissions'),
                ]);
                
                const data = marksRes.data;
                const subs = submissionsRes.data.filter(s => s.grade !== null);
                
                const total_exams = data.length;
                const scores = data.map(m => (m.score / m.max_score) * 100);
                const highest = scores.length > 0 ? Math.max(...scores).toFixed(1) : 0;
                const sum = scores.reduce((a, b) => a + b, 0);
                const average = scores.length > 0 ? (sum / scores.length).toFixed(1) : 0;
                
                setMarks(data);
                setSubmissions(subs);
                setStats({ total_exams, highest, average });

                const studentRes = await api.get(`/students/${user.sub}`);
                const classId = studentRes.data.class_id;
                if (classId) {
                    const assignRes = await api.get(`/assignments/class/${classId}`);
                    setAssignments(assignRes.data);
                }

            } catch (error) {
                console.error("Failed to fetch marks data", error);
            } finally {
                setLoading(false);
            }
        };

        if (user?.sub) fetchAllData();
    }, [user]);

    const getAssignmentTitle = (id) => assignments.find(a => String(a.id) === String(id))?.title || 'Assignment';

    const getGrade = (percentage) => {
        if (percentage >= 90) return 'A+';
        if (percentage >= 80) return 'A';
        if (percentage >= 70) return 'B';
        if (percentage >= 60) return 'C';
        if (percentage >= 50) return 'D';
        return 'F';
    };

    const handleDownloadReport = async () => {
        try {
            const response = await api.get(`/marks/report-card/${user.sub}`, {
                responseType: 'blob',
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `Report_Card_${user.full_name}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
            toast({
                title: "Success",
                description: "Report card downloaded successfully",
            });
        } catch (error) {
            toast({
                title: "Download Failed",
                description: "Failed to generate report card",
                variant: "destructive",
            });
        }
    };

    if (loading) return (
        <div className="flex flex-col items-center justify-center h-[80vh] space-y-4">
            <Loader2 className="h-10 w-10 animate-spin text-blue-600" />
            <p className="text-muted-foreground font-medium">Calculating your final grades...</p>
        </div>
    );

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">My Performance</h2>
                    <p className="text-muted-foreground">Comprehensive record of your examination and assignment grades.</p>
                </div>
                <Button className="bg-purple-600 hover:bg-purple-700 shadow-lg" onClick={handleDownloadReport}>
                    <Download size={18} className="mr-2" />
                    Download PDF Report
                </Button>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
                <StatCard 
                    title="Exams Attempted" 
                    value={stats.total_exams} 
                    icon={<ClipboardList size={24} />} 
                    color="bg-blue-50 text-blue-600" 
                />
                <StatCard 
                    title="Highest Score %" 
                    value={`${stats.highest}%`} 
                    icon={<Trophy size={24} />} 
                    color="bg-amber-50 text-amber-600" 
                />
                <StatCard 
                    title="Average Grade %" 
                    value={`${stats.average}%`} 
                    icon={<Target size={24} />} 
                    color="bg-emerald-50 text-emerald-600" 
                />
            </div>

            <Card className="border-none shadow-xl overflow-hidden bg-white">
                <CardHeader className="bg-gray-50/50 border-b">
                    <CardTitle className="text-lg">Detailed Exam Report</CardTitle>
                </CardHeader>
                <Table>
                    <TableHeader>
                        <TableRow className="bg-muted/30 text-[11px] uppercase tracking-wider font-bold">
                            <TableHead className="pl-6">Subject</TableHead>
                            <TableHead className="text-center">Score</TableHead>
                            <TableHead className="text-center">Total</TableHead>
                            <TableHead className="text-center">Percentage</TableHead>
                            <TableHead className="text-center">Grade</TableHead>
                            <TableHead className="text-right pr-6">Status</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {marks.length > 0 ? marks.map((mark) => {
                            const percentage = (mark.score / mark.max_score) * 100;
                            return (
                                <TableRow key={mark.id} className="hover:bg-gray-50/50 group transition-colors">
                                    <TableCell className="pl-6 font-bold text-gray-800">{mark.subject}</TableCell>
                                    <TableCell className="text-center font-mono">{mark.score}</TableCell>
                                    <TableCell className="text-center font-mono text-muted-foreground">{mark.max_score}</TableCell>
                                    <TableCell className="text-center font-bold text-blue-600">{percentage.toFixed(1)}%</TableCell>
                                    <TableCell className="text-center">
                                        <Badge variant="outline" className="font-bold bg-blue-50 text-blue-700 border-blue-200">
                                            {getGrade(percentage)}
                                        </Badge>
                                    </TableCell>
                                    <TableCell className="text-right pr-6">
                                        <Badge className={cn(
                                            "font-bold",
                                            percentage >= 50 ? "bg-emerald-500" : "bg-red-500"
                                        )}>
                                            {percentage >= 50 ? "PASS" : "FAIL"}
                                        </Badge>
                                    </TableCell>
                                </TableRow>
                            );
                        }) : (
                            <TableRow>
                                <TableCell colSpan={6} className="h-32 text-center text-muted-foreground italic">
                                    No examination records found.
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </Card>

            <div className="space-y-4">
                <h3 className="text-2xl font-bold tracking-tight flex items-center gap-2">
                    <Award className="text-purple-600" />
                    Assignment Performance
                </h3>
                <Card className="border-none shadow-xl overflow-hidden bg-white">
                    <Table>
                        <TableHeader>
                            <TableRow className="bg-muted/30">
                                <TableHead className="pl-6">Assignment Title</TableHead>
                                <TableHead className="text-center">Submitted On</TableHead>
                                <TableHead className="text-center">Grade</TableHead>
                                <TableHead className="pr-6">Teacher Feedback</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {submissions.length > 0 ? submissions.map((sub) => (
                                <TableRow key={sub.id} className="hover:bg-gray-50/50">
                                    <TableCell className="pl-6 font-semibold">{getAssignmentTitle(sub.assignment_id)}</TableCell>
                                    <TableCell className="text-center text-xs text-muted-foreground">{sub.submission_date}</TableCell>
                                    <TableCell className="text-center">
                                        <Badge className="bg-blue-600 font-black px-3">
                                            {sub.grade}
                                        </Badge>
                                    </TableCell>
                                    <TableCell className="pr-6 text-sm text-gray-600 italic">
                                        {sub.feedback || "No feedback provided yet."}
                                    </TableCell>
                                </TableRow>
                            )) : (
                                <TableRow>
                                    <TableCell colSpan={4} className="h-32 text-center text-muted-foreground italic">
                                        No graded assignments to display.
                                    </TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </Card>
            </div>
        </div>
    );
};

export default Marks;
