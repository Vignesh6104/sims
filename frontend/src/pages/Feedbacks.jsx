import React, { useState, useEffect } from 'react';
import {
    Plus,
    RefreshCw,
    MessageSquare,
    AlertCircle,
    CheckCircle2
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
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useAuth } from '../context/AuthContext';
import { cn } from '@/lib/utils';
import { format } from 'date-fns';

const Feedbacks = () => {
    const [feedbacks, setFeedbacks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [open, setOpen] = useState(false);
    const [responseOpen, setResponseOpen] = useState(false);
    const [selectedFeedback, setSelectedFeedback] = useState(null);
    const [adminResponse, setAdminResponse] = useState('');
    const { role } = useAuth();
    const { toast } = useToast();

    const [formData, setFormData] = useState({
        subject: '',
        description: '',
        priority: 'MEDIUM'
    });

    const fetchFeedbacks = async () => {
        setLoading(true);
        try {
            const response = await api.get('/feedbacks/');
            setFeedbacks(response.data);
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to fetch feedbacks",
                variant: "destructive",
            });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchFeedbacks();
    }, []);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSelectChange = (name, value) => {
        setFormData({ ...formData, [name]: value });
    };

    const handleSubmit = async () => {
        try {
            await api.post('/feedbacks/', formData);
            toast({
                title: "Success",
                description: "Feedback submitted successfully",
            });
            fetchFeedbacks();
            setOpen(false);
            setFormData({ subject: '', description: '', priority: 'MEDIUM' });
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to submit feedback",
                variant: "destructive",
            });
        }
    };

    const handleAdminResponse = async () => {
        try {
            await api.put(`/feedbacks/${selectedFeedback.id}`, { 
                admin_response: adminResponse,
                status: 'RESOLVED'
            });
            toast({
                title: "Responded",
                description: "Response sent successfully",
            });
            fetchFeedbacks();
            setResponseOpen(false);
            setAdminResponse('');
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to send response",
                variant: "destructive",
            });
        }
    };

    const columns = [
        { 
            accessorKey: "created_at", 
            header: "Date",
            cell: ({ row }) => format(new Date(row.original.created_at), 'PPP')
        },
        { accessorKey: "subject", header: "Subject" },
        { 
            accessorKey: "priority", 
            header: "Priority",
            cell: ({ row }) => {
                const priority = row.original.priority;
                return (
                    <Badge variant={priority === 'HIGH' ? 'destructive' : priority === 'MEDIUM' ? 'default' : 'outline'}>
                        {priority}
                    </Badge>
                );
            }
        },
        { 
            accessorKey: "status", 
            header: "Status",
            cell: ({ row }) => (
                <Badge className={cn(
                    row.original.status === 'RESOLVED' ? 'bg-green-500' : 'bg-blue-500'
                )}>
                    {row.original.status}
                </Badge>
            )
        },
        {
            id: "actions",
            header: "Actions",
            cell: ({ row }) => {
                const fb = row.original;
                if (role === 'admin' && fb.status !== 'RESOLVED') {
                    return (
                        <Button size="sm" onClick={() => {
                            setSelectedFeedback(fb);
                            setResponseOpen(true);
                        }}>
                            Respond
                        </Button>
                    );
                }
                return null;
            }
        }
    ];

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Feedback & Grievances</h2>
                    <p className="text-muted-foreground">Submit suggestions or report issues.</p>
                </div>
                <div className="flex items-center space-x-2">
                    <Button variant="outline" onClick={fetchFeedbacks} disabled={loading}>
                        <RefreshCw className={cn("mr-2 h-4 w-4", loading && "animate-spin")} />
                        Refresh
                    </Button>
                    {role !== 'admin' && (
                        <Button onClick={() => setOpen(true)}>
                            <Plus className="mr-2 h-4 w-4" />
                            Submit Feedback
                        </Button>
                    )}
                </div>
            </div>

            <Card className="glass border-none">
                <CardHeader>
                    <CardTitle>History</CardTitle>
                </CardHeader>
                <CardContent>
                    <DataTable 
                        columns={columns} 
                        data={feedbacks} 
                        loading={loading}
                        searchKey="subject"
                    />
                </CardContent>
            </Card>

            {/* Submit Feedback Dialog */}
            <Dialog open={open} onOpenChange={setOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Submit New Feedback</DialogTitle>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                        <div className="grid gap-2">
                            <Label htmlFor="subject">Subject</Label>
                            <Input id="subject" name="subject" value={formData.subject} onChange={handleChange} placeholder="What is this about?" />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="priority">Priority</Label>
                            <Select value={formData.priority} onValueChange={(v) => handleSelectChange('priority', v)}>
                                <SelectTrigger>
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="LOW">Low</SelectItem>
                                    <SelectItem value="MEDIUM">Medium</SelectItem>
                                    <SelectItem value="HIGH">High</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="description">Description</Label>
                            <Textarea id="description" name="description" value={formData.description} onChange={handleChange} placeholder="Provide details..." />
                        </div>
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
                        <Button onClick={handleSubmit}>Submit</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            {/* Admin Response Dialog */}
            <Dialog open={responseOpen} onOpenChange={setResponseOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Respond to Feedback</DialogTitle>
                    </DialogHeader>
                    {selectedFeedback && (
                        <div className="space-y-4 py-4">
                            <div className="bg-muted p-3 rounded-md">
                                <p className="text-sm font-semibold">{selectedFeedback.subject}</p>
                                <p className="text-sm italic">"{selectedFeedback.description}"</p>
                            </div>
                            <div className="grid gap-2">
                                <Label htmlFor="admin_response">Your Response</Label>
                                <Textarea 
                                    id="admin_response" 
                                    value={adminResponse} 
                                    onChange={(e) => setAdminResponse(e.target.value)} 
                                    placeholder="Type your response here..."
                                />
                            </div>
                        </div>
                    )}
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setResponseOpen(false)}>Cancel</Button>
                        <Button onClick={handleAdminResponse}>Send Response & Resolve</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
};

export default Feedbacks;
