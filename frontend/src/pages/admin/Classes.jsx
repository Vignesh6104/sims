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
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from '@/lib/utils';

const Classes = () => {
    const [classes, setClasses] = useState([]);
    const [teachers, setTeachers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [open, setOpen] = useState(false);
    const [editMode, setEditMode] = useState(false);
    const [selectedId, setSelectedId] = useState(null);
    const [formData, setFormData] = useState({
        name: '',
        teacher_id: ''
    });
    const { toast } = useToast();

    const fetchData = async () => {
        setLoading(true);
        try {
            const [classesRes, teachersRes] = await Promise.all([
                api.get('/class_rooms/'),
                api.get('/teachers/')
            ]);
            setClasses(classesRes.data);
            setTeachers(teachersRes.data);
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

    const handleOpen = () => {
        setEditMode(false);
        setFormData({ name: '', teacher_id: '' });
        setOpen(true);
    };

    const handleEdit = (cls) => {
        setEditMode(true);
        setSelectedId(cls.id);
        setFormData({
            name: cls.name,
            teacher_id: cls.teacher_id ? String(cls.teacher_id) : ''
        });
        setOpen(true);
    };

    const handleDelete = async (id) => {
        if (window.confirm('Are you sure you want to delete this class?')) {
            try {
                await api.delete(`/class_rooms/${id}/`);
                toast({
                    title: "Success",
                    description: "Class deleted successfully",
                });
                fetchData();
            } catch (error) {
                toast({
                    title: "Error",
                    description: "Failed to delete class",
                    variant: "destructive",
                });
            }
        }
    };

    const handleClose = () => setOpen(false);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSelectChange = (name, value) => {
        setFormData({ ...formData, [name]: value });
    };

    const handleSubmit = async () => {
        try {
            const payload = { ...formData };
            if (payload.teacher_id === '' || payload.teacher_id === 'none') payload.teacher_id = null;

            if (editMode) {
                await api.put(`/class_rooms/${selectedId}/`, payload);
                toast({
                    title: "Success",
                    description: "Class updated successfully",
                });
            } else {
                await api.post('/class_rooms/', payload);
                toast({
                    title: "Success",
                    description: "Class added successfully",
                });
            }
            fetchData();
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
        { accessorKey: "name", header: "Class Name" },
        { 
            accessorKey: "teacher_id", 
            header: "Class Teacher",
            cell: ({ row }) => {
                const teacher = teachers.find(t => String(t.id) === String(row.original.teacher_id));
                return teacher ? teacher.full_name : 'Not Assigned';
            }
        },
        {
            id: "actions",
            cell: ({ row }) => {
                const cls = row.original;
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
                            <DropdownMenuItem onClick={() => handleEdit(cls)}>
                                <Pencil className="mr-2 h-4 w-4" /> Edit
                            </DropdownMenuItem>
                            <DropdownMenuItem 
                                onClick={() => handleDelete(cls.id)}
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
                    <h2 className="text-3xl font-bold tracking-tight">Classes Management</h2>
                    <p className="text-muted-foreground">Manage school classes and assign class teachers.</p>
                </div>
                <div className="flex items-center space-x-2">
                    <Button variant="outline" onClick={fetchData} disabled={loading}>
                        <RefreshCw className={cn("mr-2 h-4 w-4", loading && "animate-spin")} />
                        Refresh
                    </Button>
                    <Button onClick={handleOpen}>
                        <Plus className="mr-2 h-4 w-4" />
                        Add Class
                    </Button>
                </div>
            </div>

            <Card className="glass border-none shadow-none">
                <CardHeader className="pb-2">
                    <CardTitle className="text-lg font-medium">Class List</CardTitle>
                </CardHeader>
                <CardContent>
                    <DataTable 
                        columns={columns} 
                        data={classes} 
                        loading={loading}
                        searchKey="name"
                    />
                </CardContent>
            </Card>

            <Dialog open={open} onOpenChange={setOpen}>
                <DialogContent className="sm:max-w-[425px]">
                    <DialogHeader>
                        <DialogTitle>{editMode ? 'Edit Class' : 'Add New Class'}</DialogTitle>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                        <div className="grid gap-2">
                            <Label htmlFor="name">Class Name</Label>
                            <Input
                                id="name"
                                name="name"
                                value={formData.name}
                                onChange={handleChange}
                                placeholder="e.g. Grade 10-A"
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="teacher_id">Class Teacher</Label>
                            <Select 
                                value={formData.teacher_id} 
                                onValueChange={(value) => handleSelectChange('teacher_id', value)}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder="Assign Teacher" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="none">None</SelectItem>
                                    {teachers.map((teacher) => (
                                        <SelectItem key={teacher.id} value={String(teacher.id)}>
                                            {teacher.full_name}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
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

export default Classes;
