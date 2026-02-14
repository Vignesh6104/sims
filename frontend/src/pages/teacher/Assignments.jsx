import React, { useState, useEffect } from 'react';
import { 
    Plus, 
    FileEdit, 
    CheckCircle2, 
    ExternalLink, 
    Clock, 
    BookOpen,
    Loader2,
    Search,
    ChevronRight,
    Users
} from 'lucide-react';
import api from '../../api/axios';
import { useAuth } from '../../context/AuthContext';
import { useToast } from "@/components/ui/use-toast";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
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
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogFooter,
    DialogDescription,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { cn } from '@/lib/utils';

const Assignments = () => {
    const { user } = useAuth();
    const [assignments, setAssignments] = useState([]);
    const [classes, setClasses] = useState([]);
    const [subjects, setSubjects] = useState([]);
    
    // Create/Edit State
    const [open, setOpen] = useState(false);
    const [form, setForm] = useState({
        title: '',
        description: '',
        class_id: '',
        subject_id: '',
        due_date: ''
    });

    // Grading State
    const [submissions, setSubmissions] = useState([]);
    const [openGrade, setOpenGrade] = useState(false);
    const [selectedAssignment, setSelectedAssignment] = useState(null);
    const [gradeForm, setGradeForm] = useState({ grade: '', feedback: '' });
    const [selectedSubmissionId, setSelectedSubmissionId] = useState(null);

    const { toast } = useToast();

    useEffect(() => {
        fetchInitialData();
        fetchAssignments();
    }, []);

    const fetchInitialData = async () => {
        try {
            const [clsRes, subRes] = await Promise.all([
                api.get(`/class_rooms?teacher_id=${user.sub}`),
                api.get('/subjects')
            ]);
            setClasses(clsRes.data);
            setSubjects(subRes.data);
        } catch (error) {
            console.error("Failed to fetch metadata");
        }
    };

    const fetchAssignments = async () => {
        try {
            const res = await api.get('/assignments/teacher');
            setAssignments(res.data);
        } catch (error) {
            console.error("Failed to fetch assignments");
        }
    };

    const handleCreate = async () => {
        try {
            await api.post('/assignments', { ...form, teacher_id: user.sub });
            toast({
                title: "Success",
                description: "Assignment created successfully",
            });
            setOpen(false);
            fetchAssignments();
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to create assignment",
                variant: "destructive",
            });
        }
    };

    const handleViewSubmissions = async (assignment) => {
        setSelectedAssignment(assignment);
        setSubmissions([]); // Clear old submissions
        try {
            const res = await api.get(`/assignments/submissions/${assignment.id}`);
            setSubmissions(res.data);
            setOpenGrade(true);
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to fetch submissions",
                variant: "destructive",
            });
        }
    };

    const handleGrade = async () => {
        try {
            await api.put(`/assignments/submissions/${selectedSubmissionId}`, {
                grade: parseFloat(gradeForm.grade),
                feedback: gradeForm.feedback
            });
            toast({
                title: "Success",
                description: "Submission graded successfully",
            });
            handleViewSubmissions(selectedAssignment);
            setGradeForm({ grade: '', feedback: '' });
            setSelectedSubmissionId(null);
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to grade submission",
                variant: "destructive",
            });
        }
    };

    const getClassName = (id) => classes.find(c => String(c.id) === String(id))?.name || id;
    const getSubjectName = (id) => subjects.find(s => String(s.id) === String(id))?.name || id;

    const getFullUrl = (content) => {
        if (!content) return null;
        const trimmed = content.trim();
        
        // 1. If it's already a full absolute URL, return it
        if (/^https?:\/\//i.test(trimmed)) return trimmed;
        
        // 2. If it's a protocol-relative URL
        if (trimmed.startsWith('//')) return `https:${trimmed}`;

        // 3. Handle Cloudinary paths (often saved as image/upload/... or folder/...)
        if (trimmed.includes('cloudinary.com') || trimmed.includes('sims_assignments/')) {
            const cleanPath = trimmed.replace(/^https?:\/\//i, '').replace(/^\/+/, '');
            if (!cleanPath.startsWith('res.cloudinary.com')) {
                // If it's just the path, we know your cloud name is dievsawtw
                return `https://res.cloudinary.com/dievsawtw/${cleanPath.startsWith('image/upload/') ? cleanPath : `image/upload/${cleanPath}`}`;
            }
            return `https://${cleanPath}`;
        }

        // 4. Handle local uploads (starting with /uploads)
        if (trimmed.startsWith('/')) {
            const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
            const baseUrl = apiUrl.split('/api/v1')[0];
            return `${baseUrl}${trimmed}`;
        }
        
        return trimmed;
    };

    const isImage = (url) => {
        if (!url) return false;
        return url.toLowerCase().split(/[?#]/)[0].match(/\.(jpeg|jpg|gif|png|webp|svg)$/);
    };

    const isPdf = (url) => {
        if (!url) return false;
        return url.toLowerCase().split(/[?#]/)[0].match(/\.pdf$/);
    };

    const getPdfPreviewUrl = (url) => {
        if (!url) return null;
        // Cloudinary can render the first page of a PDF as a JPG by changing the extension
        if (url.includes('cloudinary.com')) {
            return url.replace(/\.pdf($|\?|#)/, '.jpg$1');
        }
        return null;
    };

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Assignments</h2>
                    <p className="text-muted-foreground">Distribute tasks and grade student submissions.</p>
                </div>
                <Button className="bg-blue-600 hover:bg-blue-700" onClick={() => setOpen(true)}>
                    <Plus className="mr-2 h-4 w-4" />
                    Create Assignment
                </Button>
            </div>

            <Card className="border-none shadow-xl overflow-hidden bg-white">
                <Table>
                    <TableHeader>
                        <TableRow className="bg-muted/30">
                            <TableHead className="pl-6">Title</TableHead>
                            <TableHead>Class</TableHead>
                            <TableHead>Subject</TableHead>
                            <TableHead>Due Date</TableHead>
                            <TableHead className="text-right pr-6">Actions</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {assignments.map((row) => (
                            <TableRow key={row.id} className="hover:bg-gray-50/50 group">
                                <TableCell className="pl-6 font-semibold">{row.title}</TableCell>
                                <TableCell>
                                    <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-100">
                                        {getClassName(row.class_id)}
                                    </Badge>
                                </TableCell>
                                <TableCell>{getSubjectName(row.subject_id)}</TableCell>
                                <TableCell>
                                    <div className="flex items-center text-sm text-muted-foreground">
                                        <Clock size={14} className="mr-1" />
                                        {row.due_date}
                                    </div>
                                </TableCell>
                                <TableCell className="text-right pr-6">
                                    <Button 
                                        variant="ghost" 
                                        size="sm" 
                                        className="text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                                        onClick={() => handleViewSubmissions(row)}
                                    >
                                        <Users className="mr-2 h-4 w-4" />
                                        Submissions
                                    </Button>
                                </TableCell>
                            </TableRow>
                        ))}
                        {assignments.length === 0 && (
                            <TableRow>
                                <TableCell colSpan={5} className="h-48 text-center text-muted-foreground italic">
                                    No assignments created yet.
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </Card>

            {/* Create Dialog */}
            <Dialog open={open} onOpenChange={setOpen}>
                <DialogContent className="sm:max-w-[500px]">
                    <DialogHeader>
                        <DialogTitle>Create New Assignment</DialogTitle>
                        <DialogDescription>Fill in the details to publish a new task for your students.</DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                        <div className="grid gap-2">
                            <Label htmlFor="title">Title</Label>
                            <Input
                                id="title"
                                value={form.title}
                                onChange={(e) => setForm({...form, title: e.target.value})}
                                placeholder="e.g. Weekly Math Quiz"
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="desc">Description</Label>
                            <Textarea
                                id="desc"
                                value={form.description}
                                onChange={(e) => setForm({...form, description: e.target.value})}
                                placeholder="Describe the requirements..."
                                rows={3}
                            />
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="grid gap-2">
                                <Label>Class</Label>
                                <Select value={String(form.class_id)} onValueChange={(v) => setForm({...form, class_id: v})}>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Select Class" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {classes.map(c => <SelectItem key={c.id} value={String(c.id)}>{c.name}</SelectItem>)}
                                    </SelectContent>
                                </Select>
                            </div>
                            <div className="grid gap-2">
                                <Label>Subject</Label>
                                <Select value={String(form.subject_id)} onValueChange={(v) => setForm({...form, subject_id: v})}>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Select Subject" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {subjects.map(s => <SelectItem key={s.id} value={String(s.id)}>{s.name}</SelectItem>)}
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="due">Due Date</Label>
                            <Input
                                id="due"
                                type="date"
                                value={form.due_date}
                                onChange={(e) => setForm({...form, due_date: e.target.value})}
                            />
                        </div>
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
                        <Button className="bg-blue-600 hover:bg-blue-700" onClick={handleCreate}>Publish Assignment</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            {/* Grading Dialog */}
            <Dialog open={openGrade} onOpenChange={setOpenGrade}>
                <DialogContent className="sm:max-w-[800px] max-h-[90vh] overflow-y-auto">
                    <DialogHeader>
                        <DialogTitle>Submissions: {selectedAssignment?.title}</DialogTitle>
                        <DialogDescription>Review and grade student work for this assignment.</DialogDescription>
                    </DialogHeader>
                    
                    <div className="mt-6 border rounded-xl overflow-hidden">
                        <Table>
                            <TableHeader>
                                <TableRow className="bg-muted/50">
                                    <TableHead>Student</TableHead>
                                    <TableHead>Submitted On</TableHead>
                                    <TableHead>Content</TableHead>
                                    <TableHead>Grade</TableHead>
                                    <TableHead className="text-right">Action</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {submissions.map((sub) => (
                                    <TableRow key={sub.id}>
                                        <TableCell>
                                            <div className="font-semibold text-sm">{sub.student_name || 'N/A'}</div>
                                            <div className="text-[10px] text-muted-foreground font-mono">{sub.student_id}</div>
                                        </TableCell>
                                        <TableCell className="text-xs">{sub.submission_date}</TableCell>
                                        <TableCell>
                                            <Button 
                                                asChild
                                                variant="outline" 
                                                size="sm"
                                                className="h-8"
                                            >
                                                <a href={getFullUrl(sub.content)} download target="_blank" rel="noreferrer">
                                                    <BookOpen className="mr-2 h-3 w-3" />
                                                    Download
                                                </a>
                                            </Button>
                                        </TableCell>
                                        <TableCell>
                                            <Badge variant={sub.grade !== null ? "default" : "secondary"} className={cn(
                                                sub.grade !== null ? "bg-emerald-500" : "bg-gray-100"
                                            )}>
                                                {sub.grade !== null ? sub.grade : 'Ungraded'}
                                            </Badge>
                                        </TableCell>
                                        <TableCell className="text-right">
                                            {selectedSubmissionId === sub.id ? (
                                                <div className="flex items-center justify-end gap-2">
                                                    <Input 
                                                        className="h-8 w-16 text-center" 
                                                        placeholder="0-100" 
                                                        value={gradeForm.grade}
                                                        onChange={(e) => setGradeForm({...gradeForm, grade: e.target.value})}
                                                    />
                                                    <Button size="icon" className="h-8 w-8 bg-emerald-600 hover:bg-emerald-700" onClick={handleGrade}>
                                                        <CheckCircle2 size={16} />
                                                    </Button>
                                                </div>
                                            ) : (
                                                <Button variant="ghost" size="sm" onClick={() => {
                                                    setSelectedSubmissionId(sub.id);
                                                    setGradeForm({ grade: sub.grade || '', feedback: sub.feedback || '' });
                                                }}>
                                                    Grade
                                                </Button>
                                            )}
                                        </TableCell>
                                    </TableRow>
                                ))}
                                {submissions.length === 0 && (
                                    <TableRow>
                                        <TableCell colSpan={5} className="h-32 text-center text-muted-foreground italic">
                                            No submissions received yet.
                                        </TableCell>
                                    </TableRow>
                                )}
                            </TableBody>
                        </Table>
                    </div>
                    
                    <DialogFooter className="mt-6">
                        <Button variant="outline" onClick={() => setOpenGrade(false)}>Close Window</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
};

export default Assignments;
