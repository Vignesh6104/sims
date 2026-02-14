import React, { useState, useEffect } from 'react';
import { 
    Search, 
    Book as BookIcon, 
    Library, 
    Clock, 
    Calendar,
    AlertCircle,
    Loader2,
    CheckCircle2,
    History
} from 'lucide-react';
import api from '../api/axios';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { cn } from '@/lib/utils';

const LibraryCatalog = () => {
    const [books, setBooks] = useState([]);
    const [myBooks, setMyBooks] = useState([]);
    const [search, setSearch] = useState('');
    const [loading, setLoading] = useState(false);

    const fetchBooks = async () => {
        setLoading(true);
        try {
            const params = search ? { search } : {};
            const response = await api.get('/library/books/', { params });
            setBooks(response.data);
        } catch (error) {
            console.error("Failed to fetch books");
        } finally {
            setLoading(false);
        }
    };

    const fetchMyBooks = async () => {
        try {
            const response = await api.get('/library/my-books/');
            setMyBooks(response.data);
        } catch (error) {
            console.error("Failed to fetch my books");
        }
    };

    useEffect(() => {
        fetchBooks();
        fetchMyBooks();
    }, [search]);

    const handleSearchChange = (e) => {
        setSearch(e.target.value);
    };

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            <div className="flex flex-col space-y-2">
                <h2 className="text-3xl font-bold tracking-tight text-blue-900">Library</h2>
                <p className="text-muted-foreground font-medium">Browse our collection or manage your borrowed items.</p>
            </div>
            
            <Tabs defaultValue="catalog" className="w-full" onValueChange={(v) => v === 'borrowed' && fetchMyBooks()}>
                <TabsList className="grid w-full grid-cols-2 max-w-[400px] mb-8 glass">
                    <TabsTrigger value="catalog" className="gap-2">
                        <Library size={16} />
                        Catalog
                    </TabsTrigger>
                    <TabsTrigger value="borrowed" className="gap-2">
                        <History size={16} />
                        My History
                    </TabsTrigger>
                </TabsList>

                <TabsContent value="catalog" className="m-0 space-y-8">
                    <Card className="glass border-none shadow-sm overflow-hidden">
                        <CardContent className="p-4 sm:p-6 flex items-center gap-4">
                            <div className="relative flex-1">
                                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground h-4 w-4" />
                                <Input
                                    className="pl-10 h-12 bg-white/50 border-white/80 focus:bg-white"
                                    placeholder="Search by book title, author, or ISBN..."
                                    value={search}
                                    onChange={handleSearchChange}
                                />
                            </div>
                            <Button className="bg-blue-600 hover:bg-blue-700 h-12 px-6" onClick={fetchBooks}>Search</Button>
                        </CardContent>
                    </Card>

                    {loading ? (
                        <div className="flex flex-col items-center justify-center py-24 space-y-4">
                            <Loader2 className="h-10 w-10 animate-spin text-blue-600" />
                            <p className="text-muted-foreground animate-pulse">Searching the archives...</p>
                        </div>
                    ) : (
                        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                            {books.map((book) => (
                                <Card key={book.id} className="glass border-none shadow-sm flex flex-col group hover:shadow-xl hover:translate-y-[-4px] transition-all duration-300">
                                    <CardHeader className="pb-4">
                                        <div className="flex justify-between items-start mb-2">
                                            <div className="p-2.5 bg-blue-100 text-blue-600 rounded-xl">
                                                <BookIcon size={20} />
                                            </div>
                                            <Badge className={cn(
                                                "font-bold uppercase tracking-tighter text-[10px]",
                                                book.available_quantity > 0 ? "bg-emerald-500" : "bg-red-500"
                                            )}>
                                                {book.available_quantity > 0 ? "In Stock" : "Out of Stock"}
                                            </Badge>
                                        </div>
                                        <CardTitle className="text-lg font-extrabold line-clamp-2 min-h-[3.5rem] group-hover:text-blue-600 transition-colors">
                                            {book.title}
                                        </CardTitle>
                                        <CardDescription className="text-blue-800 font-bold">
                                            by {book.author}
                                        </CardDescription>
                                    </CardHeader>
                                    <CardContent className="flex-1 flex flex-col space-y-4">
                                        <div className="text-xs text-muted-foreground flex items-center gap-2 bg-gray-50 p-2 rounded-lg border border-gray-100 italic">
                                            <span className="font-bold text-gray-400 not-italic uppercase tracking-widest text-[9px]">ISBN:</span>
                                            {book.isbn || 'N/A'}
                                        </div>
                                        <div className="mt-auto flex items-center justify-between pt-2">
                                            <p className="text-xs font-bold text-gray-500 uppercase">Availability:</p>
                                            <span className="text-sm font-black text-blue-900">
                                                {book.available_quantity} / {book.quantity} <span className="text-[10px] text-gray-400 font-medium">COPIES</span>
                                            </span>
                                        </div>
                                    </CardContent>
                                </Card>
                            ))}
                            {books.length === 0 && !loading && (
                                <div className="sm:col-span-2 lg:col-span-3 xl:col-span-4 flex flex-col items-center justify-center py-24 bg-gray-50/50 rounded-3xl border-2 border-dashed">
                                    <AlertCircle size={48} className="text-muted-foreground opacity-20 mb-4" />
                                    <p className="text-lg font-bold text-muted-foreground">No books found matching your search.</p>
                                </div>
                            )}
                        </div>
                    )}
                </TabsContent>

                <TabsContent value="borrowed" className="m-0">
                    <div className="grid gap-6 md:grid-cols-2">
                        {myBooks.length > 0 ? myBooks.map((record) => (
                            <Card key={record.id} className="glass border-none shadow-sm hover:shadow-md transition-shadow">
                                <CardContent className="p-6">
                                    <div className="flex justify-between items-start mb-4">
                                        <h3 className="text-xl font-extrabold text-blue-900">{record.book?.title || "Untitled Book"}</h3>
                                        <Badge variant={record.status === 'returned' ? "outline" : "default"} className={cn(
                                            "font-bold uppercase tracking-tighter text-[10px] px-3 py-1",
                                            record.status === 'returned' ? "bg-emerald-50 text-emerald-700 border-emerald-200" : "bg-blue-600"
                                        )}>
                                            {record.status}
                                        </Badge>
                                    </div>
                                    <Separator className="bg-blue-100/50 mb-6" />
                                    <div className="grid grid-cols-2 gap-y-6">
                                        <div className="space-y-1">
                                            <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest flex items-center gap-1">
                                                <Calendar size={10} />
                                                Issue Date
                                            </p>
                                            <p className="font-bold text-gray-700">{record.issue_date}</p>
                                        </div>
                                        <div className="space-y-1">
                                            <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest flex items-center gap-1">
                                                <Clock size={10} />
                                                Due Date
                                            </p>
                                            <p className="font-bold text-red-600">{record.due_date}</p>
                                        </div>
                                        {record.fine_amount > 0 && (
                                            <div className="col-span-2 p-3 bg-red-50 rounded-xl border border-red-100 flex justify-between items-center">
                                                <p className="text-xs font-bold text-red-800 uppercase tracking-tight">Accrued Overdue Fine:</p>
                                                <p className="text-lg font-black text-red-600">${record.fine_amount}</p>
                                            </div>
                                        )}
                                    </div>
                                </CardContent>
                            </Card>
                        )) : (
                            <div className="md:col-span-2 flex flex-col items-center justify-center py-32 bg-gray-50/50 rounded-3xl border-2 border-dashed">
                                <History size={64} className="text-muted-foreground opacity-10 mb-4" />
                                <p className="text-xl font-bold text-muted-foreground">Your borrowing history is empty.</p>
                                <p className="text-sm text-muted-foreground mt-1">Start by browsing the catalog and picking a book!</p>
                            </div>
                        )}
                    </div>
                </TabsContent>
            </Tabs>
        </div>
    );
};

export default LibraryCatalog;
