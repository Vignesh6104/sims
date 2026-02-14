import React, { useState, useEffect } from 'react';
import {
    Plus,
    RefreshCw,
    BookOpen,
    Play,
    Award,
    Clock
} from 'lucide-react';
import api from '../api/axios';
import { useToast } from "@/components/ui/use-toast";
import { DataTable } from "@/components/ui/data-table";
import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogFooter,
} from "@/components/ui/dialog";
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
import { Badge } from "@/components/ui/badge";
import { useAuth } from '../context/AuthContext';
import { cn } from '@/lib/utils';
import { useNavigate } from 'react-router-dom';

const Quizzes = () => {
    const [quizzes, setQuizzes] = useState([]);
    const [classes, setClasses] = useState([]);
    const [subjects, setSubjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [open, setOpen] = useState(false);
    const { role } = useAuth();
    const { toast } = useToast();
    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        title: '',
        description: '',
        class_id: '',
        subject_id: '',
        time_limit_minutes: 30,
        questions_data: [
            { question: '', options: ['', '', '', ''], correct_answer: 0, points: 1 }
        ]
    });

    const fetchData = async () => {
        setLoading(true);
        try {
            const [quizRes, classRes, subRes] = await Promise.all([
                api.get('/quizzes/'),
                api.get('/class_rooms/'),
                api.get('/subjects/')
            ]);
            setQuizzes(quizRes.data);
            setClasses(classRes.data);
            setSubjects(subRes.data);
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to fetch data",
                variant: "destructive",
            });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const handleAddQuestion = () => {
        setFormData({
            ...formData,
            questions_data: [...formData.questions_data, { question: '', options: ['', '', '', ''], correct_answer: 0, points: 1 }]
        });
    };

    const handleQuestionChange = (index, field, value) => {
        const newQuestions = [...formData.questions_data];
        newQuestions[index][field] = value;
        setFormData({ ...formData, questions_data: newQuestions });
    };

    const handleOptionChange = (qIndex, oIndex, value) => {
        const newQuestions = [...formData.questions_data];
        newQuestions[qIndex].options[oIndex] = value;
        setFormData({ ...formData, questions_data: newQuestions });
    };

    const handleSubmit = async () => {
        try {
            await api.post('/quizzes/', formData);
            toast({
                title: "Success",
                description: "Quiz created successfully",
            });
            fetchData();
            setOpen(false);
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to create quiz",
                variant: "destructive",
            });
        }
    };

    const columns = [
        { accessorKey: "title", header: "Title" },
        { 
            accessorKey: "subject_id", 
            header: "Subject",
            cell: ({ row }) => subjects.find(s => s.id === row.original.subject_id)?.name || 'N/A'
        },
        { 
            accessorKey: "class_id", 
            header: "Class",
            cell: ({ row }) => classes.find(c => c.id === row.original.class_id)?.name || 'N/A'
        },
        { 
            accessorKey: "time_limit_minutes", 
            header: "Time (min)",
            cell: ({ row }) => <div className="flex items-center"><Clock className="mr-1 h-3 w-3" /> {row.original.time_limit_minutes}</div>
        },
        {
            id: "actions",
            header: "Actions",
            cell: ({ row }) => {
                if (role === 'student') {
                    return (
                        <Button size="sm" onClick={() => navigate(`/student/quiz/${row.original.id}`)}>
                            <Play className="mr-2 h-4 w-4" /> Start
                        </Button>
                    );
                }
                return (
                    <Badge variant="outline">{row.original.questions_data.length} Questions</Badge>
                );
            }
        }
    ];

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Quizzes & Assessments</h2>
                    <p className="text-muted-foreground">Manage and take digital examinations.</p>
                </div>
                <div className="flex items-center space-x-2">
                    <Button variant="outline" onClick={fetchData} disabled={loading}>
                        <RefreshCw className={cn("mr-2 h-4 w-4", loading && "animate-spin")} />
                        Refresh
                    </Button>
                    {role === 'teacher' && (
                        <Button onClick={() => setOpen(true)}>
                            <Plus className="mr-2 h-4 w-4" />
                            Create Quiz
                        </Button>
                    )}
                </div>
            </div>

            <Card className="glass border-none">
                <CardHeader>
                    <CardTitle>Available Quizzes</CardTitle>
                </CardHeader>
                <CardContent>
                    <DataTable 
                        columns={columns} 
                        data={quizzes} 
                        loading={loading}
                        searchKey="title"
                    />
                </CardContent>
            </Card>

            <Dialog open={open} onOpenChange={setOpen}>
                <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
                    <DialogHeader>
                        <DialogTitle>Create New Quiz</DialogTitle>
                        <DialogDescription>Design your assessment with multiple choice questions.</DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div className="grid gap-2">
                                <Label>Title</Label>
                                <Input value={formData.title} onChange={(e) => setFormData({...formData, title: e.target.value})} />
                            </div>
                            <div className="grid gap-2">
                                <Label>Time Limit (minutes)</Label>
                                <Input type="number" value={formData.time_limit_minutes} onChange={(e) => setFormData({...formData, time_limit_minutes: parseInt(e.target.value)})} />
                            </div>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="grid gap-2">
                                <Label>Class</Label>
                                <Select onValueChange={(v) => setFormData({...formData, class_id: v})}>
                                    <SelectTrigger><SelectValue placeholder="Select Class" /></SelectTrigger>
                                    <SelectContent>
                                        {classes.map(c => <SelectItem key={c.id} value={c.id}>{c.name}</SelectItem>)}
                                    </SelectContent>
                                </Select>
                            </div>
                            <div className="grid gap-2">
                                <Label>Subject</Label>
                                <Select onValueChange={(v) => setFormData({...formData, subject_id: v})}>
                                    <SelectTrigger><SelectValue placeholder="Select Subject" /></SelectTrigger>
                                    <SelectContent>
                                        {subjects.map(s => <SelectItem key={s.id} value={s.id}>{s.name}</SelectItem>)}
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>

                        <div className="space-y-4 border-t pt-4">
                            <div className="flex items-center justify-between">
                                <h3 className="font-semibold">Questions</h3>
                                <Button type="button" variant="outline" size="sm" onClick={handleAddQuestion}>Add Question</Button>
                            </div>
                            {formData.questions_data.map((q, qIndex) => (
                                <Card key={qIndex} className="p-4 space-y-3">
                                    <div className="grid gap-2">
                                        <Label>Question {qIndex + 1}</Label>
                                        <Input value={q.question} onChange={(e) => handleQuestionChange(qIndex, 'question', e.target.value)} />
                                    </div>
                                    <div className="grid grid-cols-2 gap-2">
                                        {q.options.map((opt, oIndex) => (
                                            <div key={oIndex} className="flex items-center space-x-2">
                                                <input 
                                                    type="radio" 
                                                    name={`correct-${qIndex}`} 
                                                    checked={q.correct_answer === oIndex}
                                                    onChange={() => handleQuestionChange(qIndex, 'correct_answer', oIndex)}
                                                />
                                                <Input value={opt} onChange={(e) => handleOptionChange(qIndex, oIndex, e.target.value)} placeholder={`Option ${oIndex + 1}`} />
                                            </div>
                                        ))}
                                    </div>
                                </Card>
                            ))}
                        </div>
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
                        <Button onClick={handleSubmit}>Create Quiz</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
};

export default Quizzes;
