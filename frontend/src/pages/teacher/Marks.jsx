import React, { useState, useEffect } from 'react';
import { 
    Award, 
    BarChart3, 
    FileText, 
    Search, 
    ChevronRight, 
    Loader2, 
    CheckCircle2, 
    Clock,
    Filter,
    Plus,
    Save
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
import { Badge } from "@/components/ui/badge";
import { cn } from '@/lib/utils';

const Marks = () => {
    const { user } = useAuth();
    const [classes, setClasses] = useState([]);
    const [exams, setExams] = useState([]);
    const [subjects, setSubjects] = useState([]);
    const [assignments, setAssignments] = useState([]);
    
    const [selectedClass, setSelectedIdClass] = useState('');
    const [selectedExam, setSelectedExam] = useState('');
    const [selectedSubject, setSelectedSubject] = useState('');
    
    const [students, setStudents] = useState([]);
    const [marksData, setMarksData] = useState({});
    
    const [reportData, setReportData] = useState([]);
    const [assignmentSubmissions, setAssignmentSubmissions] = useState([]);
    
    const [loading, setLoading] = useState(false);
    const { toast } = useToast();

    useEffect(() => {
        const fetchInitialData = async () => {
            try {
                const [classesRes, examsRes, subjectsRes] = await Promise.all([
                    api.get(`/class_rooms?teacher_id=${user.sub}`),
                    api.get('/exams'),
                    api.get('/subjects')
                ]);
                setClasses(classesRes.data);
                setExams(examsRes.data);
                setSubjects(subjectsRes.data);
            } catch (error) {
                console.error("Failed to fetch initial data", error);
            }
        };
        if (user?.sub) fetchInitialData();
    }, [user]);

    const fetchStudentsAndMarks = async (classId, examId, subjId) => {
        setLoading(true);
        try {
            const studentsRes = await api.get(`/students?class_id=${classId}`);
            const studentsList = studentsRes.data;
            setStudents(studentsList);

            if (studentsList.length > 0) {
                const studentIds = studentsList.map(s => s.id);
                const subjObj = subjects.find(s => String(s.id) === String(subjId));
                const subjName = subjObj ? subjObj.name : '';
                
                const params = new URLSearchParams();
                params.append('exam_id', examId);
                params.append('subject', subjName);
                studentIds.forEach(id => params.append('student_ids', id));

                const marksRes = await api.get(`/marks/batch?${params.toString()}`);
                
                const newMarksData = {};
                studentsList.forEach(s => {
                    newMarksData[s.id] = { score: '', max_score: 100, id: null };
                });

                marksRes.data.forEach(mark => {
                    newMarksData[mark.student_id] = {
                        score: mark.score,
                        max_score: mark.max_score,
                        id: mark.id
                    };
                });
                
                setMarksData(newMarksData);
            }
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to fetch marks data",
                variant: "destructive",
            });
        } finally {
            setLoading(false);
        }
    };

    const fetchReport = async (classId) => {
        setLoading(true);
        try {
            const response = await api.get(`/marks/report?class_id=${classId}`);
            setReportData(response.data);
        } catch (error) {
            console.error("Failed to fetch report");
        } finally {
            setLoading(false);
        }
    };

    const fetchAssignmentGrades = async (classId) => {
        setLoading(true);
        try {
            const [assignRes, studentsRes] = await Promise.all([
                api.get(`/assignments/class/${classId}`),
                api.get(`/students?class_id=${classId}`)
            ]);
            
            const assignmentsList = assignRes.data;
            const studentsList = studentsRes.data;
            setAssignments(assignmentsList);
            setStudents(studentsList);

            const submissionsPromises = assignmentsList.map(a => 
                api.get(`/assignments/submissions/${a.id}`)
            );
            const submissionsResponses = await Promise.all(submissionsPromises);
            const allSubmissions = submissionsResponses.flatMap(r => r.data);
            setAssignmentSubmissions(allSubmissions);

        } catch (error) {
            console.error("Failed to fetch assignment grades");
        } finally {
            setLoading(false);
        }
    };

    const handleScoreChange = (studentId, field, value) => {
        setMarksData(prev => ({
            ...prev,
            [studentId]: {
                ...prev[studentId],
                [field]: value
            }
        }));
    };

    const handleSubmit = async () => {
        setLoading(true);
        try {
            const subjObj = subjects.find(s => String(s.id) === String(selectedSubject));
            const subjName = subjObj ? subjObj.name : '';

            const promises = students.map(student => {
                const data = marksData[student.id];
                if (data.score === '') return null;

                const payload = {
                    student_id: student.id,
                    subject: subjName,
                    score: parseFloat(data.score),
                    max_score: parseFloat(data.max_score),
                    exam_id: selectedExam
                };

                if (data.id) {
                    return api.put(`/marks/${data.id}`, payload);
                } else {
                    return api.post('/marks', payload);
                }
            }).filter(p => p !== null);
            
            await Promise.all(promises);
            toast({
                title: "Success",
                description: "Marks saved successfully!",
            });
            fetchStudentsAndMarks(selectedClass, selectedExam, selectedSubject);
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to save marks",
                variant: "destructive",
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <div className="flex flex-col space-y-2">
                <h2 className="text-3xl font-bold tracking-tight">Marks Management</h2>
                <p className="text-muted-foreground">Enter examination scores or track overall academic performance.</p>
            </div>

            <Tabs defaultValue="entry" className="w-full" onValueChange={(v) => {
                if (v === 'report' && selectedClass) fetchReport(selectedClass);
                if (v === 'assignment' && selectedClass) fetchAssignmentGrades(selectedClass);
                if (v === 'entry' && selectedClass && selectedExam && selectedSubject) fetchStudentsAndMarks(selectedClass, selectedExam, selectedSubject);
            }}>
                <TabsList className="grid w-full grid-cols-3 max-w-[600px] mb-8">
                    <TabsTrigger value="entry">Exam Entry</TabsTrigger>
                    <TabsTrigger value="report">Class Report</TabsTrigger>
                    <TabsTrigger value="assignment">Assignment Grades</TabsTrigger>
                </TabsList>

                <Card className="glass border-none shadow-sm mb-6">
                    <CardContent className="pt-6">
                        <div className="grid gap-6 md:grid-cols-3 items-end">
                            <div className="space-y-2">
                                <Label>Select Class</Label>
                                <Select value={selectedClass} onValueChange={(v) => {
                                    setSelectedIdClass(v);
                                    setStudents([]);
                                    setMarksData({});
                                }}>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Choose Class" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {classes.map((cls) => (
                                            <SelectItem key={cls.id} value={String(cls.id)}>{cls.name}</SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                            
                            <TabsContent value="entry" className="m-0 contents">
                                <div className="space-y-2">
                                    <Label>Select Exam</Label>
                                    <Select value={selectedExam} onValueChange={setSelectedExam}>
                                        <SelectTrigger>
                                            <SelectValue placeholder="Choose Exam" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            {exams.map((exam) => (
                                                <SelectItem key={exam.id} value={String(exam.id)}>{exam.name}</SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>
                                <div className="space-y-2">
                                    <Label>Select Subject</Label>
                                    <Select value={selectedSubject} onValueChange={(v) => {
                                        setSelectedSubject(v);
                                        if (selectedClass && selectedExam) fetchStudentsAndMarks(selectedClass, selectedExam, v);
                                    }}>
                                        <SelectTrigger>
                                            <SelectValue placeholder="Choose Subject" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            {subjects.map((subj) => (
                                                <SelectItem key={subj.id} value={String(subj.id)}>{subj.name}</SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>
                            </TabsContent>
                        </div>
                    </CardContent>
                </Card>

                {selectedClass ? (
                    <div className="space-y-6">
                        <TabsContent value="entry" className="m-0">
                            {selectedExam && selectedSubject ? (
                                <Card className="border-none shadow-xl overflow-hidden bg-white">
                                    <Table>
                                        <TableHeader>
                                            <TableRow className="bg-muted/30">
                                                <TableHead className="pl-6">Roll No</TableHead>
                                                <TableHead>Student Name</TableHead>
                                                <TableHead className="text-center">Score</TableHead>
                                                <TableHead className="text-center">Max Score</TableHead>
                                            </TableRow>
                                        </TableHeader>
                                        <TableBody>
                                            {loading ? (
                                                <TableRow>
                                                    <TableCell colSpan={4} className="h-48 text-center">
                                                        <Loader2 className="h-8 w-8 animate-spin mx-auto text-blue-600 mb-2" />
                                                        <p className="text-muted-foreground">Loading records...</p>
                                                    </TableCell>
                                                </TableRow>
                                            ) : students.map((student) => (
                                                <TableRow key={student.id} className="hover:bg-gray-50/50">
                                                    <TableCell className="pl-6 font-mono text-xs">{student.roll_number}</TableCell>
                                                    <TableCell className="font-semibold">{student.full_name}</TableCell>
                                                    <TableCell className="text-center">
                                                        <Input 
                                                            type="number" 
                                                            className="w-24 mx-auto text-center"
                                                            value={marksData[student.id]?.score || ''}
                                                            onChange={(e) => handleScoreChange(student.id, 'score', e.target.value)}
                                                        />
                                                    </TableCell>
                                                    <TableCell className="text-center">
                                                        <Input 
                                                            type="number" 
                                                            className="w-24 mx-auto text-center bg-gray-50"
                                                            value={marksData[student.id]?.max_score || 100}
                                                            onChange={(e) => handleScoreChange(student.id, 'max_score', e.target.value)}
                                                        />
                                                    </TableCell>
                                                </TableRow>
                                            ))}
                                        </TableBody>
                                    </Table>
                                    <div className="p-6 bg-gray-50/50 border-t flex justify-end">
                                        <Button size="lg" className="bg-blue-600 hover:bg-blue-700 h-12 px-8" onClick={handleSubmit} disabled={loading}>
                                            {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Save className="mr-2 h-5 w-5" />}
                                            Save All Marks
                                        </Button>
                                    </div>
                                </Card>
                            ) : (
                                <Card className="flex flex-col items-center justify-center py-24 bg-gray-50/50 border-dashed border-2">
                                    <Award size={48} className="text-muted-foreground opacity-20 mb-4" />
                                    <p className="text-muted-foreground font-medium text-lg text-center">
                                        Select an exam and subject to begin data entry.
                                    </p>
                                </Card>
                            )}
                        </TabsContent>

                        <TabsContent value="report" className="m-0">
                            <Card className="border-none shadow-xl overflow-hidden bg-white">
                                <Table>
                                    <TableHeader>
                                        <TableRow className="bg-muted/30">
                                            <TableHead className="pl-6">Roll No</TableHead>
                                            <TableHead>Student Name</TableHead>
                                            <TableHead>Exam</TableHead>
                                            <TableHead>Subject</TableHead>
                                            <TableHead className="text-center">Score</TableHead>
                                            <TableHead className="text-right pr-6">Grade %</TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {reportData.map((row, index) => (
                                            <TableRow key={index} className="hover:bg-gray-50/50">
                                                <TableCell className="pl-6 font-mono text-xs">{row.roll_number}</TableCell>
                                                <TableCell className="font-semibold">{row.student_name}</TableCell>
                                                <TableCell className="text-sm">{row.exam_name}</TableCell>
                                                <TableCell className="text-sm">{row.subject}</TableCell>
                                                <TableCell className="text-center font-medium">
                                                    {row.score} <span className="text-muted-foreground text-xs">/ {row.max_score}</span>
                                                </TableCell>
                                                <TableCell className="text-right pr-6">
                                                    <Badge variant="secondary" className={cn(
                                                        "font-bold",
                                                        row.percentage < 40 ? "text-red-600 bg-red-50" : "text-emerald-600 bg-emerald-50"
                                                    )}>
                                                        {row.percentage}%
                                                    </Badge>
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                        {reportData.length === 0 && (
                                            <TableRow>
                                                <TableCell colSpan={6} className="h-48 text-center text-muted-foreground italic">
                                                    No results found for this class.
                                                </TableCell>
                                            </TableRow>
                                        )}
                                    </TableBody>
                                </Table>
                            </Card>
                        </TabsContent>

                        <TabsContent value="assignment" className="m-0">
                            <Card className="border-none shadow-xl overflow-hidden bg-white overflow-x-auto">
                                <Table>
                                    <TableHeader>
                                        <TableRow className="bg-muted/30">
                                            <TableHead className="pl-6 sticky left-0 bg-white z-10">Student Name</TableHead>
                                            {assignments.map(a => (
                                                <TableHead key={a.id} className="text-center min-w-[150px]">{a.title}</TableHead>
                                            ))}
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {students.map(student => (
                                            <TableRow key={student.id} className="hover:bg-gray-50/50">
                                                <TableCell className="pl-6 font-semibold sticky left-0 bg-white z-10 border-r shadow-[2px_0_5px_rgba(0,0,0,0.05)]">
                                                    {student.full_name}
                                                </TableCell>
                                                {assignments.map(a => {
                                                    const sub = assignmentSubmissions.find(s => String(s.assignment_id) === String(a.id) && String(s.student_id) === String(student.id));
                                                    return (
                                                        <TableCell key={a.id} className="text-center">
                                                            {sub ? (
                                                                <div className="space-y-1">
                                                                    <Badge className="bg-blue-600 font-bold">
                                                                        {sub.grade !== null ? sub.grade : 'Pending'}
                                                                    </Badge>
                                                                    {sub.feedback && (
                                                                        <p className="text-[10px] text-muted-foreground truncate max-w-[120px] mx-auto" title={sub.feedback}>
                                                                            {sub.feedback}
                                                                        </p>
                                                                    )}
                                                                </div>
                                                            ) : (
                                                                <span className="text-xs text-muted-foreground italic opacity-50">No Sub.</span>
                                                            )}
                                                        </TableCell>
                                                    );
                                                })}
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            </Card>
                        </TabsContent>
                    </div>
                ) : (
                    <Card className="flex flex-col items-center justify-center py-24 bg-gray-50/50 border-dashed border-2">
                        <Filter size={48} className="text-muted-foreground opacity-20 mb-4" />
                        <p className="text-muted-foreground font-medium text-lg text-center">
                            Please select a class to view or manage marks.
                        </p>
                    </Card>
                )}
            </Tabs>
        </div>
    );
};

export default Marks;
