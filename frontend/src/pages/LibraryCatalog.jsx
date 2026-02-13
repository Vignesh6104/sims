import React, { useState, useEffect } from 'react';
import {
    Box,
    Paper,
    Typography,
    TextField,
    InputAdornment,
    Grid,
    Card,
    CardContent,
    CardActions,
    Button,
    Chip,
    Divider,
    Tab,
    Tabs
} from '@mui/material';
import { Search, Book as BookIcon } from '@mui/icons-material';
import api from '../api/axios';

const LibraryCatalog = () => {
    const [books, setBooks] = useState([]);
    const [myBooks, setMyBooks] = useState([]);
    const [search, setSearch] = useState('');
    const [tabValue, setTabValue] = useState(0);
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
        if (tabValue === 0) fetchBooks();
        else fetchMyBooks();
    }, [tabValue, search]);

    const handleSearchChange = (e) => {
        setSearch(e.target.value);
    };

    return (
        <Box>
            <Typography variant="h4" fontWeight="bold" sx={{ mb: 3 }}>Library</Typography>
            
            <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} sx={{ mb: 3 }}>
                <Tab label="Book Catalog" />
                <Tab label="My Borrowed Books" />
            </Tabs>

            {tabValue === 0 && (
                <>
                    <Box sx={{ mb: 4 }}>
                        <TextField
                            fullWidth
                            variant="outlined"
                            placeholder="Search by title or author..."
                            value={search}
                            onChange={handleSearchChange}
                            InputProps={{
                                startAdornment: (
                                    <InputAdornment position="start">
                                        <Search />
                                    </InputAdornment>
                                ),
                            }}
                        />
                    </Box>

                    <Grid container spacing={3}>
                        {books.map((book) => (
                            <Grid item xs={12} sm={6} md={4} key={book.id}>
                                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                                    <CardContent sx={{ flexGrow: 1 }}>
                                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                            <BookIcon color="primary" sx={{ mr: 1 }} />
                                            <Typography variant="h6" component="div">
                                                {book.title}
                                            </Typography>
                                        </Box>
                                        <Typography color="text.secondary" gutterBottom>
                                            by {book.author}
                                        </Typography>
                                        <Typography variant="body2">
                                            ISBN: {book.isbn || 'N/A'}
                                        </Typography>
                                        <Box sx={{ mt: 2 }}>
                                            <Chip 
                                                label={book.available_quantity > 0 ? "Available" : "Out of Stock"} 
                                                color={book.available_quantity > 0 ? "success" : "error"} 
                                                size="small" 
                                            />
                                            <Typography variant="caption" sx={{ ml: 1 }}>
                                                {book.available_quantity} / {book.quantity} copies
                                            </Typography>
                                        </Box>
                                    </CardContent>
                                </Card>
                            </Grid>
                        ))}
                    </Grid>
                </>
            )}

            {tabValue === 1 && (
                <Grid container spacing={3}>
                    {myBooks.length > 0 ? myBooks.map((record) => (
                        <Grid item xs={12} md={6} key={record.id}>
                            <Card>
                                <CardContent>
                                    <Typography variant="h6">
                                        {/* Since record.book might not be populated in list, be careful. 
                                            Currently API might return nested book if configured.
                                            Let's check schema. BorrowRecord has `book: Optional[Book]`.
                                        */}
                                        {record.book?.title || "Book Title"}
                                    </Typography>
                                    <Divider sx={{ my: 1 }} />
                                    <Grid container spacing={2}>
                                        <Grid item xs={6}>
                                            <Typography variant="caption" color="text.secondary">Issue Date</Typography>
                                            <Typography>{record.issue_date}</Typography>
                                        </Grid>
                                        <Grid item xs={6}>
                                            <Typography variant="caption" color="text.secondary">Due Date</Typography>
                                            <Typography>{record.due_date}</Typography>
                                        </Grid>
                                        <Grid item xs={6}>
                                            <Typography variant="caption" color="text.secondary">Status</Typography>
                                            <Chip 
                                                label={record.status} 
                                                color={record.status === 'returned' ? 'default' : 'primary'} 
                                                size="small" 
                                            />
                                        </Grid>
                                        {record.fine_amount > 0 && (
                                            <Grid item xs={6}>
                                                <Typography variant="caption" color="error">Fine</Typography>
                                                <Typography color="error">${record.fine_amount}</Typography>
                                            </Grid>
                                        )}
                                    </Grid>
                                </CardContent>
                            </Card>
                        </Grid>
                    )) : (
                        <Grid item xs={12}>
                            <Typography variant="body1" align="center" sx={{ mt: 4 }}>
                                No borrowing history found.
                            </Typography>
                        </Grid>
                    )}
                </Grid>
            )}
        </Box>
    );
};

export default LibraryCatalog;
