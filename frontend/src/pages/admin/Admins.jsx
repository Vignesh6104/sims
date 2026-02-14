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

const Admins = () => {
    const [admins, setAdmins] = useState([]);
    const [loading, setLoading] = useState(true);
    const [open, setOpen] = useState(false);
    const [editMode, setEditMode] = useState(false);
    const [selectedId, setSelectedId] = useState(null);
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        full_name: '',
        department: '',
        position: ''
    });
    const { toast } = useToast();

    const fetchAdmins = async () => {
        setLoading(true);
        try {
            const response = await api.get('/admins/');
            setAdmins(response.data);
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to fetch admins",
                variant: "destructive",
            });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAdmins();
    }, []);

    const handleOpen = () => {
        setEditMode(false);
        setFormData({
            email: '',
            password: '',
            full_name: '',
            department: '',
            position: ''
        });
        setOpen(true);
    };

    const handleEdit = (admin) => {
        setEditMode(true);
        setSelectedId(admin.id);
        setFormData({
            email: admin.email,
            password: '',
            full_name: admin.full_name,
            department: admin.department || '',
            position: admin.position || ''
        });
        setOpen(true);
    };

    const handleDelete = async (id) => {
        if (window.confirm('Are you sure you want to delete this admin?')) {
            try {
                await api.delete(`/admins/${id}/`);
                toast({
                    title: "Success",
                    description: "Admin deleted successfully",
                });
                fetchAdmins();
            } catch (error) {
                toast({
                    title: "Error",
                    description: error.response?.data?.detail || "Failed to delete admin",
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
                
                await api.put(`/admins/${selectedId}/`, updateData);
                toast({
                    title: "Success",
                    description: "Admin updated successfully",
                });
            } else {
                await api.post('/admins/', formData);
                toast({
                    title: "Success",
                    description: "Admin added successfully",
                });
            }
            fetchAdmins();
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
        { accessorKey: "department", header: "Department" },
        { accessorKey: "position", header: "Position" },
        {
            id: "actions",
            cell: ({ row }) => {
                const admin = row.original;
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
                            <DropdownMenuItem onClick={() => handleEdit(admin)}>
                                <Pencil className="mr-2 h-4 w-4" /> Edit
                            </DropdownMenuItem>
                            <DropdownMenuItem 
                                onClick={() => handleDelete(admin.id)}
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
                    <h2 className="text-3xl font-bold tracking-tight">Admins Management</h2>
                    <p className="text-muted-foreground">Manage administrative accounts and their roles.</p>
                </div>
                <div className="flex items-center space-x-2">
                    <Button variant="outline" onClick={fetchAdmins} disabled={loading}>
                        <RefreshCw className={cn("mr-2 h-4 w-4", loading && "animate-spin")} />
                        Refresh
                    </Button>
                    <Button onClick={handleOpen}>
                        <Plus className="mr-2 h-4 w-4" />
                        Add Admin
                    </Button>
                </div>
            </div>

            <Card className="glass border-none shadow-none">
                <CardHeader className="pb-2">
                    <CardTitle className="text-lg font-medium">Admin List</CardTitle>
                </CardHeader>
                <CardContent>
                    <DataTable 
                        columns={columns} 
                        data={admins} 
                        loading={loading}
                        searchKey="full_name"
                    />
                </CardContent>
            </Card>

            <Dialog open={open} onOpenChange={setOpen}>
                <DialogContent className="sm:max-w-[425px]">
                    <DialogHeader>
                        <DialogTitle>{editMode ? 'Edit Admin' : 'Add New Admin'}</DialogTitle>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                        <div className="grid gap-2">
                            <Label htmlFor="full_name">Full Name</Label>
                            <Input
                                id="full_name"
                                name="full_name"
                                value={formData.full_name}
                                onChange={handleChange}
                                placeholder="Admin Name"
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
                                placeholder="admin@example.com"
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
                            <Label htmlFor="department">Department</Label>
                            <Input
                                id="department"
                                name="department"
                                value={formData.department}
                                onChange={handleChange}
                                placeholder="IT Department"
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="position">Position</Label>
                            <Input
                                id="position"
                                name="position"
                                value={formData.position}
                                onChange={handleChange}
                                placeholder="System Administrator"
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

export default Admins;
