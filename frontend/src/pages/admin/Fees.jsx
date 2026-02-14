import React, { useState, useEffect } from 'react';
import {
    Plus,
    RefreshCw,
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
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from '@/lib/utils';

const Fees = () => {
    const [structures, setStructures] = useState([]);
    const [classes, setClasses] = useState([]);
    const [loading, setLoading] = useState(false);
    const [open, setOpen] = useState(false);
    const { toast } = useToast();

    const [structureForm, setStructureForm] = useState({
        class_id: '',
        academic_year: '2024-2025',
        amount: '',
        description: '',
        due_date: ''
    });

    useEffect(() => {
        fetchStructures();
        fetchClasses();
    }, []);

    const fetchClasses = async () => {
        try {
            const res = await api.get('/class_rooms/');
            setClasses(res.data);
        } catch (error) {
            console.error("Failed to fetch classes");
        }
    };

    const fetchStructures = async () => {
        setLoading(true);
        try {
            const res = await api.get('/fees/structures');
            setStructures(res.data);
        } catch (error) {
            console.error("Failed to fetch structures");
        } finally {
            setLoading(false);
        }
    };

    const handleStructureSubmit = async () => {
        try {
            await api.post('/fees/structures', structureForm);
            toast({
                title: "Success",
                description: "Fee Structure added successfully",
            });
            setOpen(false);
            fetchStructures();
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to add fee structure",
                variant: "destructive",
            });
        }
    };

    const handleSelectChange = (name, value) => {
        setStructureForm({ ...structureForm, [name]: value });
    };

    const columns = [
        { accessorKey: "academic_year", header: "Year" },
        { 
            accessorKey: "class_id", 
            header: "Class",
            cell: ({ row }) => {
                const cls = classes.find(c => String(c.id) === String(row.original.class_id));
                return cls ? cls.name : row.original.class_id;
            }
        },
        { accessorKey: "amount", header: "Amount" },
        { accessorKey: "description", header: "Description" },
        { accessorKey: "due_date", header: "Due Date" },
    ];

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Fee Management</h2>
                    <p className="text-muted-foreground">Configure fee structures and track student payments.</p>
                </div>
                <div className="flex items-center space-x-2">
                    <Button variant="outline" onClick={fetchStructures} disabled={loading}>
                        <RefreshCw className={cn("mr-2 h-4 w-4", loading && "animate-spin")} />
                        Refresh
                    </Button>
                    <Button onClick={() => setOpen(true)}>
                        <Plus className="mr-2 h-4 w-4" />
                        Add Fee Structure
                    </Button>
                </div>
            </div>

            <Card className="glass border-none shadow-none">
                <CardHeader className="pb-2">
                    <CardTitle className="text-lg font-medium">Fee Structures</CardTitle>
                </CardHeader>
                <CardContent>
                    <DataTable 
                        columns={columns} 
                        data={structures} 
                        loading={loading}
                        searchKey="description"
                    />
                </CardContent>
            </Card>

            <Dialog open={open} onOpenChange={setOpen}>
                <DialogContent className="sm:max-w-[425px]">
                    <DialogHeader>
                        <DialogTitle>Add Fee Structure</DialogTitle>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                        <div className="grid gap-2">
                            <Label htmlFor="class_id">Class</Label>
                            <Select 
                                value={String(structureForm.class_id)} 
                                onValueChange={(value) => handleSelectChange('class_id', value)}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder="Select Class" />
                                </SelectTrigger>
                                <SelectContent>
                                    {classes.map((c) => (
                                        <SelectItem key={c.id} value={String(c.id)}>
                                            {c.name}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="amount">Amount</Label>
                            <Input
                                id="amount"
                                type="number"
                                value={structureForm.amount}
                                onChange={(e) => setStructureForm({...structureForm, amount: e.target.value})}
                                placeholder="Enter amount"
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="description">Description</Label>
                            <Input
                                id="description"
                                value={structureForm.description}
                                onChange={(e) => setStructureForm({...structureForm, description: e.target.value})}
                                placeholder="e.g. Tuition Fee"
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="due_date">Due Date</Label>
                            <Input
                                id="due_date"
                                type="date"
                                value={structureForm.due_date}
                                onChange={(e) => setStructureForm({...structureForm, due_date: e.target.value})}
                            />
                        </div>
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
                        <Button onClick={handleStructureSubmit}>Save Structure</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
};

export default Fees;
