import React, { useState, useEffect } from 'react';
import {
    Plus,
    RefreshCw,
    CheckCircle,
    XCircle,
    Clock,
    Calendar as CalendarIcon
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
    DialogDescription,
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
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useAuth } from '../context/AuthContext';
import { cn } from '@/lib/utils';
import { format } from 'date-fns';

const Leaves = () => {
    const [leaves, setLeaves] = useState([]);
    const [loading, setLoading] = useState(true);
    const [open, setOpen] = useState(false);
    const { user, role } = useAuth();
    const { toast } = useToast();

    const [formData, setFormData] = useState({
        start_date: '',
        end_date: '',
        leave_type: 'CASUAL',
        reason: ''
    });

    const fetchLeaves = async () => {
        setLoading(true);
        try {
            const response = await api.get('/leaves/');
            setLeaves(response.data);
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to fetch leaves",
                variant: "destructive",
            });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchLeaves();
    }, []);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSelectChange = (name, value) => {
        setFormData({ ...formData, [name]: value });
    };

    const handleSubmit = async () => {
        try {
            await api.post('/leaves/', formData);
            toast({
                title: "Success",
                description: "Leave application submitted successfully",
            });
            fetchLeaves();
            setOpen(false);
        } catch (error) {
            toast({
                title: "Error",
                description: error.response?.data?.detail || "Failed to submit leave",
                variant: "destructive",
            });
        }
    };

    const handleStatusUpdate = async (id, status) => {
        try {
            await api.put(`/leaves/${id}`, { status });
            toast({
                title: "Updated",
                description: `Leave ${status.toLowerCase()} successfully`,
            });
            fetchLeaves();
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to update leave status",
                variant: "destructive",
            });
        }
    };

    const columns = [
        { 
            accessorKey: "created_at", 
            header: "Applied On",
            cell: ({ row }) => format(new Date(row.original.created_at), 'PPP')
        },
        { 
            accessorKey: "leave_type", 
            header: "Type",
            cell: ({ row }) => <Badge variant="outline">{row.original.leave_type}</Badge>
        },
        { 
            accessorKey: "start_date", 
            header: "From",
            cell: ({ row }) => format(new Date(row.original.start_date), 'PP')
        },
        { 
            accessorKey: "end_date", 
            header: "To",
            cell: ({ row }) => format(new Date(row.original.end_date), 'PP')
        },
        { accessorKey: "reason", header: "Reason" },
        { 
            accessorKey: "status", 
            header: "Status",
            cell: ({ row }) => {
                const status = row.original.status;
                return (
                    <Badge className={cn(
                        status === 'APPROVED' ? 'bg-green-500' : 
                        status === 'REJECTED' ? 'bg-red-500' : 'bg-yellow-500'
                    )}>
                        {status}
                    </Badge>
                );
            }
        },
        {
            id: "actions",
            header: "Actions",
            cell: ({ row }) => {
                const leave = row.original;
                if (role === 'admin' && leave.status === 'PENDING') {
                    return (
                        <div className="flex space-x-2">
                            <Button size="sm" variant="outline" className="text-green-600" onClick={() => handleStatusUpdate(leave.id, 'APPROVED')}>
                                <CheckCircle className="h-4 w-4" />
                            </Button>
                            <Button size="sm" variant="outline" className="text-red-600" onClick={() => handleStatusUpdate(leave.id, 'REJECTED')}>
                                <XCircle className="h-4 w-4" />
                            </Button>
                        </div>
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
                    <h2 className="text-3xl font-bold tracking-tight">Leave Management</h2>
                    <p className="text-muted-foreground">Apply for leaves and track status.</p>
                </div>
                <div className="flex items-center space-x-2">
                    <Button variant="outline" onClick={fetchLeaves} disabled={loading}>
                        <RefreshCw className={cn("mr-2 h-4 w-4", loading && "animate-spin")} />
                        Refresh
                    </Button>
                    {(role === 'student' || role === 'teacher') && (
                        <Button onClick={() => setOpen(true)}>
                            <Plus className="mr-2 h-4 w-4" />
                            Apply Leave
                        </Button>
                    )}
                </div>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
                <Card className="glass border-none">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Pending Requests</CardTitle>
                        <Clock className="h-4 w-4 text-yellow-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">
                            {leaves.filter(l => l.status === 'PENDING').length}
                        </div>
                    </CardContent>
                </Card>
                <Card className="glass border-none">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Approved</CardTitle>
                        <CheckCircle className="h-4 w-4 text-green-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">
                            {leaves.filter(l => l.status === 'APPROVED').length}
                        </div>
                    </CardContent>
                </Card>
                <Card className="glass border-none">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Rejected</CardTitle>
                        <XCircle className="h-4 w-4 text-red-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">
                            {leaves.filter(l => l.status === 'REJECTED').length}
                        </div>
                    </CardContent>
                </Card>
            </div>

            <Card className="glass border-none">
                <CardHeader>
                    <CardTitle>Leave Records</CardTitle>
                </CardHeader>
                <CardContent>
                    <DataTable 
                        columns={columns} 
                        data={leaves} 
                        loading={loading}
                    />
                </CardContent>
            </Card>

            <Dialog open={open} onOpenChange={setOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Apply for Leave</DialogTitle>
                        <DialogDescription>Submit your leave request for approval.</DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div className="grid gap-2">
                                <Label htmlFor="start_date">Start Date</Label>
                                <Input id="start_date" name="start_date" type="date" value={formData.start_date} onChange={handleChange} />
                            </div>
                            <div className="grid gap-2">
                                <Label htmlFor="end_date">End Date</Label>
                                <Input id="end_date" name="end_date" type="date" value={formData.end_date} onChange={handleChange} />
                            </div>
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="leave_type">Leave Type</Label>
                            <Select value={formData.leave_type} onValueChange={(v) => handleSelectChange('leave_type', v)}>
                                <SelectTrigger>
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="SICK">Sick Leave</SelectItem>
                                    <SelectItem value="CASUAL">Casual Leave</SelectItem>
                                    <SelectItem value="EMERGENCY">Emergency Leave</SelectItem>
                                    <SelectItem value="OTHER">Other</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="reason">Reason</Label>
                            <Input id="reason" name="reason" value={formData.reason} onChange={handleChange} placeholder="Briefly explain the reason" />
                        </div>
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
                        <Button onClick={handleSubmit}>Submit Application</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
};

export default Leaves;
