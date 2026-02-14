import React, { useState, useEffect } from 'react';
import {
    Plus,
    RefreshCw,
    Search,
    BookPlus
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
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from '@/lib/utils';

const Library = () => {
    const [books, setBooks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [open, setOpen] = useState(false);
    const [formData, setFormData] = useState({
        title: '',
        author: '',
        isbn: '',
        quantity: 1
    });

    const { toast } = useToast();

    const fetchBooks = async () => {
        setLoading(true);
        try {
            const response = await api.get('/library/books');
            setBooks(response.data);
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to fetch books",
                variant: "destructive",
            });
        } finally {
            setLoading(false);
        }
    };
    
    useEffect(() => {
        fetchBooks();
    }, []);

    const handleOpen = () => {
        setFormData({ title: '', author: '', isbn: '', quantity: 1 });
        setOpen(true);
    };

    const handleClose = () => setOpen(false);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async () => {
        try {
            await api.post('/library/books', formData);
            toast({
                title: "Success",
                description: "Book added successfully",
            });
            fetchBooks();
            handleClose();
        } catch (error) {
            toast({
                title: "Error",
                description: error.response?.data?.detail || "Failed to add book",
                variant: "destructive",
            });
        }
    };

    const columns = [
        { accessorKey: "title", header: "Title" },
        { accessorKey: "author", header: "Author" },
        { accessorKey: "isbn", header: "ISBN" },
        { accessorKey: "quantity", header: "Total Qty" },
        { accessorKey: "available_quantity", header: "Available" },
    ];

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Library Management</h2>
                    <p className="text-muted-foreground">Catalog and manage school library books and inventory.</p>
                </div>
                <div className="flex items-center space-x-2">
                    <Button variant="outline" onClick={fetchBooks} disabled={loading}>
                        <RefreshCw className={cn("mr-2 h-4 w-4", loading && "animate-spin")} />
                        Refresh
                    </Button>
                    <Button onClick={handleOpen}>
                        <Plus className="mr-2 h-4 w-4" />
                        Add Book
                    </Button>
                </div>
            </div>

            <Card className="glass border-none shadow-none">
                <CardHeader className="pb-2">
                    <CardTitle className="text-lg font-medium">Book Catalog</CardTitle>
                </CardHeader>
                <CardContent>
                    <DataTable 
                        columns={columns} 
                        data={books} 
                        loading={loading}
                        searchKey="title"
                    />
                </CardContent>
            </Card>

            <Dialog open={open} onOpenChange={setOpen}>
                <DialogContent className="sm:max-w-[425px]">
                    <DialogHeader>
                        <DialogTitle>Add New Book</DialogTitle>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                        <div className="grid gap-2">
                            <Label htmlFor="title">Title</Label>
                            <Input
                                id="title"
                                name="title"
                                value={formData.title}
                                onChange={handleChange}
                                placeholder="Book Title"
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="author">Author</Label>
                            <Input
                                id="author"
                                name="author"
                                value={formData.author}
                                onChange={handleChange}
                                placeholder="Author Name"
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="isbn">ISBN</Label>
                            <Input
                                id="isbn"
                                name="isbn"
                                value={formData.isbn}
                                onChange={handleChange}
                                placeholder="ISBN Number"
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="quantity">Quantity</Label>
                            <Input
                                id="quantity"
                                name="quantity"
                                type="number"
                                value={formData.quantity}
                                onChange={handleChange}
                            />
                        </div>
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={handleClose}>Cancel</Button>
                        <Button onClick={handleSubmit}>Add Book</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
};

export default Library;
