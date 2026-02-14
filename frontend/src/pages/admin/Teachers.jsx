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

const Teachers = () => {
    const [teachers, setTeachers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [open, setOpen] = useState(false);
    const [editMode, setEditMode] = useState(false);
    const [selectedId, setSelectedId] = useState(null);
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        full_name: '',
        qualification: '',
        subject_specialization: ''
    });
    const { toast } = useToast();

    const fetchTeachers = async () => {
        setLoading(true);
        try {
            const response = await api.get('/teachers/');
            setTeachers(response.data);
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to fetch teachers",
                variant: "destructive",
            });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchTeachers();
    }, []);

    const handleOpen = () => {
        setEditMode(false);
        setFormData({
            email: '',
            password: '',
            full_name: '',
            qualification: '',
            subject_specialization: ''
        });
        setOpen(true);
    };

    const handleEdit = (teacher) => {
        setEditMode(true);
        setSelectedId(teacher.id);
        setFormData({
            email: teacher.email,
            password: '', // Password optional on edit
            full_name: teacher.full_name,
            qualification: teacher.qualification,
            subject_specialization: teacher.subject_specialization
        });
        setOpen(true);
    };

    const handleDelete = async (id) => {
        if (window.confirm('Are you sure you want to delete this teacher?')) {
            try {
                await api.delete(`/teachers/${id}/`);
                toast({
                    title: "Success",
                    description: "Teacher deleted successfully",
                });
                fetchTeachers();
            } catch (error) {
                toast({
                    title: "Error",
                    description: "Failed to delete teacher",
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
                const updateData = { ...formData };
                if (!updateData.password) delete updateData.password;
                
                await api.put(`/teachers/${selectedId}/`, updateData);
                toast({
                    title: "Success",
                    description: "Teacher updated successfully",
                });
            } else {
                await api.post('/auth/register/teacher', formData);
                toast({
                    title: "Success",
                    description: "Teacher added successfully",
                });
            }
            fetchTeachers();
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
        { accessorKey: "full_name", header: "Name" },
        { accessorKey: "email", header: "Email" },
        { accessorKey: "qualification", header: "Qualification" },
        { accessorKey: "subject_specialization", header: "Specialization" },
        {
            id: "actions",
            cell: ({ row }) => {
                const teacher = row.original;
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
                            <DropdownMenuItem onClick={() => handleEdit(teacher)}>
                                <Pencil className="mr-2 h-4 w-4" /> Edit
                            </DropdownMenuItem>
                            <DropdownMenuItem 
                                onClick={() => handleDelete(teacher.id)}
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
                    <h2 className="text-3xl font-bold tracking-tight">Teachers Management</h2>
                    <p className="text-muted-foreground">Manage your school teachers and their specializations.</p>
                </div>
                <div className="flex items-center space-x-2">
                    <Button variant="outline" onClick={fetchTeachers} disabled={loading}>
                        <RefreshCw className={cn("mr-2 h-4 w-4", loading && "animate-spin")} />
                        Refresh
                    </Button>
                    <Button onClick={handleOpen}>
                        <Plus className="mr-2 h-4 w-4" />
                        Add Teacher
                    </Button>
                </div>
            </div>

            <Card className="glass border-none shadow-none">
                <CardHeader className="pb-2">
                    <CardTitle className="text-lg font-medium">Teacher List</CardTitle>
                </CardHeader>
                <CardContent>
                    <DataTable 
                        columns={columns} 
                        data={teachers} 
                        loading={loading}
                        searchKey="full_name"
                    />
                </CardContent>
            </Card>

            <Dialog open={open} onOpenChange={setOpen}>
                <DialogContent className="sm:max-w-[425px]">
                    <DialogHeader>
                        <DialogTitle>{editMode ? 'Edit Teacher' : 'Add New Teacher'}</DialogTitle>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                        <div className="grid gap-2">
                            <Label htmlFor="full_name">Full Name</Label>
                            <Input
                                id="full_name"
                                name="full_name"
                                value={formData.full_name}
                                onChange={handleChange}
                                placeholder="John Doe"
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="email">Email Address</Label>
                            <Input
                                id="email"
                                name="email"
                                type="email"
                                value={formData.email}
                                onChange={handleChange}
                                placeholder="john@example.com"
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="password">
                                {editMode ? "Password (leave blank to keep current)" : "Password"}
                            </Label>
                            <Input
                                id="password"
                                name="password"
                                type="password"
                                value={formData.password}
                                onChange={handleChange}
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="qualification">Qualification</Label>
                            <Input
                                id="qualification"
                                name="qualification"
                                value={formData.qualification}
                                onChange={handleChange}
                                placeholder="M.Sc. Education"
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="subject_specialization">Specialization</Label>
                            <Input
                                id="subject_specialization"
                                name="subject_specialization"
                                value={formData.subject_specialization}
                                onChange={handleChange}
                                placeholder="Mathematics"
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

export default Teachers;
