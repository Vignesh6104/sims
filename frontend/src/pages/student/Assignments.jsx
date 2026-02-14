import React, { useState, useEffect } from 'react';
import { 
    Plus, 
    FileUp, 
    CheckCircle2, 
    ExternalLink, 
    Clock, 
    BookOpen,
    Loader2,
    Search,
    ChevronRight,
    ClipboardList,
    AlertCircle,
    FileCheck
} from 'lucide-react';
import api from '../../api/axios';
import { useAuth } from '../../context/AuthContext';
import { useToast } from "@/components/ui/use-toast";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
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
    const [submissions, setSubmissions] = useState([]);
    const [myClassId, setMyClassId] = useState(null);
    const [loading, setLoading] = useState(true);
    
    const [open, setOpen] = useState(false);
    const [selectedAssignment, setSelectedAssignment] = useState(null);
    const [file, setFile] = useState(null);
    
    const { toast } = useToast();

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const res = await api.get(`/students/${user.sub}`);
                setMyClassId(res.data.class_id);
            } catch (error) {
                console.error("Failed to fetch profile", error);
                setLoading(false);
            }
        };
        if (user?.sub) fetchProfile();
    }, [user]);

    const fetchData = async () => {
        if (!myClassId) {
            setLoading(false);
            return;
        }
        setLoading(true);
        try {
            const [assignRes, subRes] = await Promise.all([
                api.get(`/assignments/class/${myClassId}`),
                api.get('/assignments/my-submissions')
            ]);
            setAssignments(assignRes.data);
            setSubmissions(subRes.data);
        } catch (error) {
            console.error("Failed to fetch data");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [myClassId]);

    const handleSubmit = async () => {
        if (!file) {
            toast({
                title: "No file selected",
                description: "Please select a file to upload.",
                variant: "destructive",
            });
            return;
        }

        const formData = new FormData();
        formData.append('assignment_id', selectedAssignment.id);
        formData.append('file', file);

        try {
            await api.post('/assignments/submissions', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            toast({
                title: "Success",
                description: "Your work has been submitted successfully!",
            });
            setOpen(false);
            setFile(null);
            fetchData();
        } catch (error) {
            toast({
                title: "Error",
                description: error.response?.data?.detail || "Submission failed",
                variant: "destructive",
            });
        }
    };

    const handleOpenSubmit = (assignment) => {
        setSelectedAssignment(assignment);
        setFile(null);
        setOpen(true);
    };

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

    const getSubmission = (assignmentId) => {
        return submissions.find(s => String(s.assignment_id) === String(assignmentId));
    };

    if (loading && !assignments.length) return (
        <div className="flex flex-col items-center justify-center h-[80vh] space-y-4">
            <Loader2 className="h-10 w-10 animate-spin text-blue-600" />
            <p className="text-muted-foreground font-medium">Loading your assignments...</p>
        </div>
    );

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            <div className="flex flex-col space-y-2">
                <h2 className="text-3xl font-bold tracking-tight">My Assignments</h2>
                <p className="text-muted-foreground">Manage your homework, projects, and track your scores.</p>
            </div>

            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {assignments.map((assign) => {
                    const submission = getSubmission(assign.id);
                    return (
                        <Card key={assign.id} className="glass border-none shadow-sm flex flex-col hover:shadow-md transition-all duration-300 group">
                            <CardHeader className="pb-4">
                                <div className="flex justify-between items-start gap-4 mb-2">
                                    <Badge className={cn(
                                        "uppercase tracking-tighter text-[10px] font-bold px-3",
                                        submission ? "bg-emerald-500" : "bg-amber-500"
                                    )}>
                                        {submission ? "Submitted" : "Pending"}
                                    </Badge>
                                    <div className="flex items-center text-[10px] font-bold text-muted-foreground uppercase">
                                        <Clock size={12} className="mr-1" />
                                        Due: {assign.due_date}
                                    </div>
                                </div>
                                <CardTitle className="text-lg font-bold group-hover:text-blue-600 transition-colors line-clamp-1">
                                    {assign.title}
                                </CardTitle>
                            </CardHeader>
                            
                            <CardContent className="flex-1 flex flex-col">
                                <p className="text-sm text-gray-600 leading-relaxed mb-6 line-clamp-3">
                                    {assign.description}
                                </p>
                                
                                {submission && (
                                    <div className="mt-auto mb-6 p-3 rounded-xl bg-blue-50/50 border border-blue-100 flex items-center justify-between">
                                        <div className="flex items-center gap-2">
                                            <div className="p-1.5 bg-blue-600 rounded-lg text-white">
                                                <FileCheck size={14} />
                                            </div>
                                            <span className="text-[10px] font-bold text-blue-900 uppercase">Grade:</span>
                                        </div>
                                        <span className="text-lg font-black text-blue-600">
                                            {submission.grade !== null ? submission.grade : '--'}
                                        </span>
                                    </div>
                                )}

                                <div className="flex flex-wrap gap-2 mt-auto">
                                    {!submission || submission.grade === null ? (
                                        <Button 
                                            className="bg-blue-600 hover:bg-blue-700 flex-1 h-10 font-bold"
                                            onClick={() => handleOpenSubmit(assign)}
                                        >
                                            <FileUp size={16} className="mr-2" />
                                            {submission ? "Update Work" : "Submit Now"}
                                        </Button>
                                    ) : (
                                        <Button className="flex-1 h-10 font-bold" disabled variant="secondary">
                                            <CheckCircle2 size={16} className="mr-2" />
                                            Finalized
                                        </Button>
                                    )}
                                    
                                    {submission && (
                                        <Button 
                                            variant="outline" 
                                            className="h-10 px-3 border-blue-200 text-blue-600 hover:bg-blue-50"
                                            asChild
                                        >
                                            <a href={getFullUrl(submission.content)} target="_blank" rel="noreferrer">
                                                <ExternalLink size={16} />
                                            </a>
                                        </Button>
                                    )}
                                </div>
                            </CardContent>
                        </Card>
                    );
                })}
                
                {assignments.length === 0 && (
                    <Card className="sm:col-span-2 lg:col-span-3 flex flex-col items-center justify-center py-32 bg-gray-50/50 border-dashed border-2">
                        <ClipboardList size={64} className="text-muted-foreground opacity-10 mb-4" />
                        <p className="text-xl font-bold text-muted-foreground">Relax! No assignments yet.</p>
                        <p className="text-sm text-muted-foreground mt-1 text-center max-w-xs">
                            Your teachers haven't posted any tasks for your class. Check back later!
                        </p>
                    </Card>
                )}
            </div>

            <Dialog open={open} onOpenChange={setOpen}>
                <DialogContent className="sm:max-w-[425px]">
                    <DialogHeader>
                        <DialogTitle>
                            {getSubmission(selectedAssignment?.id) ? "Update Submission" : "Hand in Assignment"}
                        </DialogTitle>
                        <DialogDescription className="text-blue-600 font-medium">
                            {selectedAssignment?.title}
                        </DialogDescription>
                    </DialogHeader>
                    
                    <div className="grid gap-6 py-6">
                        {getSubmission(selectedAssignment?.id) && (
                            <div className="p-3 bg-amber-50 border border-amber-100 rounded-lg flex gap-3">
                                <AlertCircle className="text-amber-600 shrink-0" size={18} />
                                <p className="text-xs text-amber-800 leading-tight">
                                    You already have a submission. Uploading a new file will replace your existing work.
                                </p>
                            </div>
                        )}
                        
                        <div className="flex flex-col items-center justify-center border-2 border-dashed rounded-2xl p-10 bg-gray-50/50 group hover:bg-gray-50 hover:border-blue-400 transition-colors cursor-pointer relative">
                            <input
                                type="file"
                                className="absolute inset-0 opacity-0 cursor-pointer z-10"
                                onChange={(e) => setFile(e.target.files[0])}
                            />
                            <div className="p-4 bg-white rounded-2xl shadow-sm mb-4 group-hover:scale-110 transition-transform pointer-events-none">
                                <FileUp className="text-blue-600" size={32} />
                            </div>
                            <p className="text-sm font-bold text-gray-700 pointer-events-none">
                                {file ? file.name : "Click or drag to select file"}
                            </p>
                            {file && (
                                <p className="text-[10px] text-muted-foreground mt-1 pointer-events-none">
                                    {(file.size / 1024).toFixed(2)} KB • Ready to upload
                                </p>
                            )}
                        </div>
                    </div>
                    
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
                        <Button 
                            className="bg-blue-600 hover:bg-blue-700" 
                            onClick={handleSubmit} 
                            disabled={!file}
                        >
                            Upload Submission
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
};

export default Assignments;
