import React, { useState, useEffect } from 'react';
import {
    Plus,
    RefreshCw,
    Pencil,
    Trash2,
    MoreHorizontal
} from 'lucide-react';
import api from '../../api/axios';
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
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from '@/lib/utils';

const Exams = () => {
    const [exams, setExams] = useState([]);
    const [loading, setLoading] = useState(true);
    const [open, setOpen] = useState(false);
    const [editMode, setEditMode] = useState(false);
    const [selectedId, setSelectedId] = useState(null);
    const [formData, setFormData] = useState({
        name: '',
        date: ''
    });
    const { toast } = useToast();

    const fetchExams = async () => {
        setLoading(true);
        try {
            const response = await api.get('/exams/');
            setExams(response.data);
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to fetch exams",
                variant: "destructive",
            });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchExams();
    }, []);

    const handleOpen = () => {
        setEditMode(false);
        setFormData({ name: '', date: '' });
        setOpen(true);
    };

    const handleEdit = (exam) => {
        setEditMode(true);
        setSelectedId(exam.id);
        setFormData({
            name: exam.name,
            date: exam.date
        });
        setOpen(true);
    };

    const handleDelete = async (id) => {
        if (window.confirm('Are you sure you want to delete this exam?')) {
            try {
                await api.delete(`/exams/${id}/`);
                toast({
                    title: "Success",
                    description: "Exam deleted successfully",
                });
                fetchExams();
            } catch (error) {
                toast({
                    title: "Error",
                    description: "Failed to delete exam",
                    variant: "destructive",
                });
            }
        }
    };

    const handleClose = () => setOpen(false);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async () => {
        try {
            if (editMode) {
                await api.put(`/exams/${selectedId}/`, formData);
                toast({
                    title: "Success",
                    description: "Exam updated successfully",
                });
            } else {
                await api.post('/exams/', formData);
                toast({
                    title: "Success",
                    description: "Exam added successfully",
                });
            }
            fetchExams();
            handleClose();
        } catch (error) {
            toast({
                title: "Error",
                description: error.response?.data?.detail || "Operation failed",
                variant: "destructive",
            });
        }
    };

    const columns = [
        { accessorKey: "name", header: "Exam Name" },
        { accessorKey: "date", header: "Date" },
        {
            id: "actions",
            cell: ({ row }) => {
                const exam = row.original;
                return (
                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <Button variant="ghost" className="h-8 w-8 p-0">
                                <span className="sr-only">Open menu</span>
                                <MoreHorizontal className="h-4 w-4" />
                            </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                            <DropdownMenuLabel>Actions</DropdownMenuLabel>
                            <DropdownMenuItem onClick={() => handleEdit(exam)}>
                                <Pencil className="mr-2 h-4 w-4" /> Edit
                            </DropdownMenuItem>
                            <DropdownMenuItem 
                                onClick={() => handleDelete(exam.id)}
                                className="text-red-600 focus:text-red-600"
                            >
                                <Trash2 className="mr-2 h-4 w-4" /> Delete
                            </DropdownMenuItem>
                        </DropdownMenuContent>
                    </DropdownMenu>
                );
            }
        }
    ];

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Exams Management</h2>
                    <p className="text-muted-foreground">Schedule and manage school examination periods.</p>
                </div>
                <div className="flex items-center space-x-2">
                    <Button variant="outline" onClick={fetchExams} disabled={loading}>
                        <RefreshCw className={cn("mr-2 h-4 w-4", loading && "animate-spin")} />
                        Refresh
                    </Button>
                    <Button onClick={handleOpen}>
                        <Plus className="mr-2 h-4 w-4" />
                        Add Exam
                    </Button>
                </div>
            </div>

            <Card className="glass border-none shadow-none">
                <CardHeader className="pb-2">
                    <CardTitle className="text-lg font-medium">Exam Schedule</CardTitle>
                </CardHeader>
                <CardContent>
                    <DataTable 
                        columns={columns} 
                        data={exams} 
                        loading={loading}
                        searchKey="name"
                    />
                </CardContent>
            </Card>

            <Dialog open={open} onOpenChange={setOpen}>
                <DialogContent className="sm:max-w-[425px]">
                    <DialogHeader>
                        <DialogTitle>{editMode ? 'Edit Exam' : 'Add New Exam'}</DialogTitle>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                        <div className="grid gap-2">
                            <Label htmlFor="name">Exam Name</Label>
                            <Input
                                id="name"
                                name="name"
                                value={formData.name}
                                onChange={handleChange}
                                placeholder="e.g. Final Term Examination"
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="date">Exam Date</Label>
                            <Input
                                id="date"
                                name="date"
                                type="date"
                                value={formData.date}
                                onChange={handleChange}
                            />
                        </div>
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={handleClose}>Cancel</Button>
                        <Button onClick={handleSubmit}>{editMode ? 'Update' : 'Add'}</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
};

export default Exams;
