import React, { useState, useEffect } from 'react';
import {
    Box,
    Button,
    Paper,
    Typography,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    IconButton,
    Tooltip,
    Tab,
    Tabs
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { Add as AddIcon, Refresh as RefreshIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import api from '../../api/axios';
import { useSnackbar } from 'notistack';

const Library = () => {
    const [books, setBooks] = useState([]);
    const [borrowed, setBorrowed] = useState([]);
    const [loading, setLoading] = useState(true);
    const [open, setOpen] = useState(false);
    const [issueOpen, setIssueOpen] = useState(false);
    const [tabValue, setTabValue] = useState(0);
    const [formData, setFormData] = useState({
        title: '',
        author: '',
        isbn: '',
        quantity: 1
    });
    const [issueData, setIssueData] = useState({
        book_id: '',
        student_id: '', // Optional
        teacher_id: '', // Optional
        due_date: ''
    });

    const { enqueueSnackbar } = useSnackbar();

    const fetchBooks = async () => {
        setLoading(true);
        try {
            const response = await api.get('/library/books');
            setBooks(response.data);
        } catch (error) {
            enqueueSnackbar('Failed to fetch books', { variant: 'error' });
        } finally {
            setLoading(false);
        }
    };
    
    // We would need an endpoint to fetch all issued books for admin view
    // For now, let's just focus on books management

    useEffect(() => {
        fetchBooks();
    }, []);

    const handleOpen = () => {
        setFormData({ title: '', author: '', isbn: '', quantity: 1 });
        setOpen(true);
    };

    const handleClose = () => setOpen(false);
    const handleIssueClose = () => setIssueOpen(false);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async () => {
        try {
            await api.post('/library/books', formData);
            enqueueSnackbar('Book added successfully', { variant: 'success' });
            fetchBooks();
            handleClose();
        } catch (error) {
            enqueueSnackbar(error.response?.data?.detail || 'Failed to add book', { variant: 'error' });
        }
    };

    const columns = [
        { field: 'title', headerName: 'Title', width: 250 },
        { field: 'author', headerName: 'Author', width: 200 },
        { field: 'isbn', headerName: 'ISBN', width: 150 },
        { field: 'quantity', headerName: 'Total Qty', width: 100 },
        { field: 'available_quantity', headerName: 'Available', width: 100 },
    ];

    return (
        <Box sx={{ height: 600, width: '100%' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h5" fontWeight="bold">Library Management</Typography>
                <Box>
                    <Button 
                        startIcon={<RefreshIcon />} 
                        onClick={fetchBooks} 
                        sx={{ mr: 1 }}
                    >
                        Refresh
                    </Button>
                    <Button 
                        variant="contained" 
                        startIcon={<AddIcon />} 
                        onClick={handleOpen}
                    >
                        Add Book
                    </Button>
                </Box>
            </Box>

            <Paper sx={{ height: '100%', width: '100%' }}>
                <DataGrid
                    rows={books}
                    columns={columns}
                    pageSize={10}
                    rowsPerPageOptions={[10]}
                    disableSelectionOnClick
                    loading={loading}
                />
            </Paper>

            <Dialog open={open} onClose={handleClose}>
                <DialogTitle>Add New Book</DialogTitle>
                <DialogContent>
                    <TextField
                        autoFocus
                        margin="dense"
                        name="title"
                        label="Title"
                        fullWidth
                        value={formData.title}
                        onChange={handleChange}
                    />
                    <TextField
                        margin="dense"
                        name="author"
                        label="Author"
                        fullWidth
                        value={formData.author}
                        onChange={handleChange}
                    />
                    <TextField
                        margin="dense"
                        name="isbn"
                        label="ISBN"
                        fullWidth
                        value={formData.isbn}
                        onChange={handleChange}
                    />
                    <TextField
                        margin="dense"
                        name="quantity"
                        label="Quantity"
                        type="number"
                        fullWidth
                        value={formData.quantity}
                        onChange={handleChange}
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleClose}>Cancel</Button>
                    <Button onClick={handleSubmit} variant="contained">Add</Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default Library;
