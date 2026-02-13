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
    Tooltip
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { Add as AddIcon, Refresh as RefreshIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import api from '../../api/axios';
import { useSnackbar } from 'notistack';

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
    const { enqueueSnackbar } = useSnackbar();

    const fetchExams = async () => {
        setLoading(true);
        try {
            const response = await api.get('/exams/');
            setExams(response.data);
        } catch (error) {
            enqueueSnackbar('Failed to fetch exams', { variant: 'error' });
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
                enqueueSnackbar('Exam deleted successfully', { variant: 'success' });
                fetchExams();
            } catch (error) {
                enqueueSnackbar('Failed to delete exam', { variant: 'error' });
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
                enqueueSnackbar('Exam updated successfully', { variant: 'success' });
            } else {
                await api.post('/exams/', formData);
                enqueueSnackbar('Exam added successfully', { variant: 'success' });
            }
            fetchExams();
            handleClose();
        } catch (error) {
            enqueueSnackbar(error.response?.data?.detail || 'Operation failed', { variant: 'error' });
        }
    };

    const columns = [
        { field: 'name', headerName: 'Exam Name', width: 250 },
        { field: 'date', headerName: 'Date', width: 150 },
        {
            field: 'actions',
            headerName: 'Actions',
            width: 150,
            sortable: false,
            filterable: false,
            renderCell: (params) => (
                <Box onClick={(e) => e.stopPropagation()}>
                    <Tooltip title="Edit">
                        <IconButton size="small" color="primary" onClick={() => handleEdit(params.row)}>
                            <EditIcon />
                        </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                        <IconButton size="small" color="error" onClick={() => handleDelete(params.row.id)}>
                            <DeleteIcon />
                        </IconButton>
                    </Tooltip>
                </Box>
            )
        }
    ];

    return (
        <Box sx={{ height: 600, width: '100%' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h5" fontWeight="bold">Exams Management</Typography>
                <Box>
                    <Button 
                        startIcon={<RefreshIcon />} 
                        onClick={fetchExams} 
                        sx={{ mr: 1 }}
                    >
                        Refresh
                    </Button>
                    <Button 
                        variant="contained" 
                        startIcon={<AddIcon />} 
                        onClick={handleOpen}
                    >
                        Add Exam
                    </Button>
                </Box>
            </Box>

            <Paper sx={{ height: '100%', width: '100%' }}>
                <DataGrid
                    rows={exams}
                    columns={columns}
                    initialState={{
                        pagination: {
                            paginationModel: { pageSize: 10 },
                        },
                    }}
                    pageSizeOptions={[10]}
                    checkboxSelection
                    disableRowSelectionOnClick
                    loading={loading}
                />
            </Paper>

            <Dialog open={open} onClose={handleClose}>
                <DialogTitle>{editMode ? 'Edit Exam' : 'Add New Exam'}</DialogTitle>
                <DialogContent>
                    <TextField
                        autoFocus
                        margin="dense"
                        name="name"
                        label="Exam Name"
                        type="text"
                        fullWidth
                        variant="outlined"
                        value={formData.name}
                        onChange={handleChange}
                    />
                    <TextField
                        margin="dense"
                        name="date"
                        label="Exam Date"
                        type="date"
                        fullWidth
                        variant="outlined"
                        value={formData.date}
                        onChange={handleChange}
                        InputLabelProps={{ shrink: true }}
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleClose}>Cancel</Button>
                    <Button onClick={handleSubmit} variant="contained">
                        {editMode ? 'Update' : 'Add'}
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default Exams;
