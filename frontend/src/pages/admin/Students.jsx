import React, { useState, useEffect, useRef } from 'react';
import {
    Plus,
    RefreshCw,
    Pencil,
    Trash2,
    CloudUpload,
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

const Students = () => {
    const [students, setStudents] = useState([]);
    const [classes, setClasses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [open, setOpen] = useState(false);
    const [editMode, setEditMode] = useState(false);
    const [selectedId, setSelectedId] = useState(null);
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        full_name: '',
        roll_number: '',
        date_of_birth: '',
        address: '',
        class_id: ''
    });
    const { toast } = useToast();
    const fileInputRef = useRef(null);

    const fetchStudents = async () => {
        setLoading(true);
        try {
            const response = await api.get('/students/');
            setStudents(response.data);
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to fetch students",
                variant: "destructive",
            });
        } finally {
            setLoading(false);
        }
    };

    const fetchClasses = async () => {
        try {
            const response = await api.get('/class_rooms/');
            setClasses(response.data);
        } catch (error) {
            console.error('Failed to fetch classes');
        }
    };

    useEffect(() => {
        fetchStudents();
        fetchClasses();
    }, []);

    const handleOpen = () => {
        setEditMode(false);
        setFormData({
            email: '',
            password: '',
            full_name: '',
            roll_number: '',
            date_of_birth: '',
            address: '',
            class_id: ''
        });
        setOpen(true);
    };

    const handleEdit = (student) => {
        setEditMode(true);
        setSelectedId(student.id);
        setFormData({
            email: student.email,
            password: '',
            full_name: student.full_name,
            roll_number: student.roll_number || '',
            date_of_birth: student.date_of_birth || '',
            address: student.address || '',
            class_id: student.class_id ? String(student.class_id) : ''
        });
        setOpen(true);
    };

    const handleDelete = async (id) => {
        if (window.confirm('Are you sure you want to delete this student?')) {
            try {
                await api.delete(`/students/${id}/`);
                toast({
                    title: "Success",
                    description: "Student deleted successfully",
                });
                fetchStudents();
            } catch (error) {
                toast({
                    title: "Error",
                    description: "Failed to delete student",
                    variant: "destructive",
                });
            }
        }
    };

    const handleImportClick = () => {
        fileInputRef.current.click();
    };

    const handleFileChange = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            setLoading(true);
            const response = await api.post('/students/upload/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            
            toast({
                title: "Import Success",
                description: response.data.message,
            });
            if (response.data.errors && response.data.errors.length > 0) {
                response.data.errors.forEach(err => {
                    toast({
                        title: "Warning",
                        description: err,
                        variant: "destructive", // Or a warning variant if available
                    });
                });
            }
            fetchStudents();
        } catch (error) {
            toast({
                title: "Import Error",
                description: error.response?.data?.detail || "Import failed",
                variant: "destructive",
            });
        } finally {
            setLoading(false);
            event.target.value = null; // Reset input
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
            if (payload.class_id === '' || payload.class_id === 'none') payload.class_id = null;
            
            if (editMode) {
                if (!payload.password) delete payload.password;
                await api.put(`/students/${selectedId}/`, payload);
                toast({
                    title: "Success",
                    description: "Student updated successfully",
                });
            } else {
                await api.post('/auth/register/student', payload);
                toast({
                    title: "Success",
                    description: "Student added successfully",
                });
            }
            fetchStudents();
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
        { accessorKey: "roll_number", header: "Roll No" },
        { accessorKey: "full_name", header: "Name" },
        { accessorKey: "email", header: "Email" },
        { 
            accessorKey: "class_id", 
            header: "Class",
            cell: ({ row }) => {
                const cls = classes.find(c => String(c.id) === String(row.original.class_id));
                return cls ? cls.name : 'N/A';
            }
        },
        { accessorKey: "address", header: "Address" },
        {
            id: "actions",
            cell: ({ row }) => {
                const student = row.original;
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
                            <DropdownMenuItem onClick={() => handleEdit(student)}>
                                <Pencil className="mr-2 h-4 w-4" /> Edit
                            </DropdownMenuItem>
                            <DropdownMenuItem 
                                onClick={() => handleDelete(student.id)}
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
                    <h2 className="text-3xl font-bold tracking-tight">Students Management</h2>
                    <p className="text-muted-foreground">Manage student enrollments and records.</p>
                </div>
                <div className="flex items-center space-x-2">
                    <input
                        type="file"
                        ref={fileInputRef}
                        style={{ display: 'none' }}
                        onChange={handleFileChange}
                        accept=".csv"
                    />
                    <Button variant="outline" onClick={handleImportClick} disabled={loading}>
                        <CloudUpload className="mr-2 h-4 w-4" />
                        Import CSV
                    </Button>
                    <Button variant="outline" onClick={fetchStudents} disabled={loading}>
                        <RefreshCw className={cn("mr-2 h-4 w-4", loading && "animate-spin")} />
                        Refresh
                    </Button>
                    <Button onClick={handleOpen}>
                        <Plus className="mr-2 h-4 w-4" />
                        Add Student
                    </Button>
                </div>
            </div>

            <Card className="glass border-none shadow-none">
                <CardHeader className="pb-2">
                    <CardTitle className="text-lg font-medium">Student List</CardTitle>
                </CardHeader>
                <CardContent>
                    <DataTable 
                        columns={columns} 
                        data={students} 
                        loading={loading}
                        searchKey="full_name"
                    />
                </CardContent>
            </Card>

            <Dialog open={open} onOpenChange={setOpen}>
                <DialogContent className="sm:max-w-[425px]">
                    <DialogHeader>
                        <DialogTitle>{editMode ? 'Edit Student' : 'Add New Student'}</DialogTitle>
                    </DialogHeader>
                    <div className="grid gap-4 py-4 max-h-[70vh] overflow-y-auto pr-2">
                        <div className="grid gap-2">
                            <Label htmlFor="full_name">Full Name</Label>
                            <Input
                                id="full_name"
                                name="full_name"
                                value={formData.full_name}
                                onChange={handleChange}
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
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="password">
                                {editMode ? "Password (leave blank to keep)" : "Password"}
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
                            <Label htmlFor="roll_number">Roll Number</Label>
                            <Input
                                id="roll_number"
                                name="roll_number"
                                value={formData.roll_number}
                                onChange={handleChange}
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="date_of_birth">Date of Birth</Label>
                            <Input
                                id="date_of_birth"
                                name="date_of_birth"
                                type="date"
                                value={formData.date_of_birth}
                                onChange={handleChange}
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="class_id">Class</Label>
                            <Select 
                                value={formData.class_id} 
                                onValueChange={(value) => handleSelectChange('class_id', value)}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder="Select Class" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="none">None</SelectItem>
                                    {classes.map((cls) => (
                                        <SelectItem key={cls.id} value={String(cls.id)}>
                                            {cls.name}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="address">Address</Label>
                            <Input
                                id="address"
                                name="address"
                                value={formData.address}
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

export default Students;
