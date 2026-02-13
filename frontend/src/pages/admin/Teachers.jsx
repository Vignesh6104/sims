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
    const { enqueueSnackbar } = useSnackbar();

    const fetchTeachers = async () => {
        setLoading(true);
        try {
            const response = await api.get('/teachers/');
            setTeachers(response.data);
        } catch (error) {
            enqueueSnackbar('Failed to fetch teachers', { variant: 'error' });
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
                enqueueSnackbar('Teacher deleted successfully', { variant: 'success' });
                fetchTeachers();
            } catch (error) {
                enqueueSnackbar('Failed to delete teacher', { variant: 'error' });
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
                // Remove password if empty (so it doesn't update to empty string)
                const updateData = { ...formData };
                if (!updateData.password) delete updateData.password;
                
                await api.put(`/teachers/${selectedId}/`, updateData);
                enqueueSnackbar('Teacher updated successfully', { variant: 'success' });
            } else {
                await api.post('/auth/register/teacher', formData);
                enqueueSnackbar('Teacher added successfully', { variant: 'success' });
            }
            fetchTeachers();
            handleClose();
        } catch (error) {
            enqueueSnackbar(error.response?.data?.detail || 'Operation failed', { variant: 'error' });
        }
    };

    const columns = [
        { field: 'id', headerName: 'ID', width: 220 },
        { field: 'full_name', headerName: 'Name', width: 200 },
        { field: 'email', headerName: 'Email', width: 250 },
        { field: 'qualification', headerName: 'Qualification', width: 150 },
        { field: 'subject_specialization', headerName: 'Specialization', width: 180 },
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
                <Typography variant="h5" fontWeight="bold">Teachers Management</Typography>
                <Box>
                    <Button 
                        startIcon={<RefreshIcon />} 
                        onClick={fetchTeachers} 
                        sx={{ mr: 1 }}
                    >
                        Refresh
                    </Button>
                    <Button 
                        variant="contained" 
                        startIcon={<AddIcon />} 
                        onClick={handleOpen}
                    >
                        Add Teacher
                    </Button>
                </Box>
            </Box>

            <Paper sx={{ height: '100%', width: '100%' }}>
                <DataGrid
                    rows={teachers}
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

            <Dialog 
                open={open} 
                onClose={handleClose}
                disableEnforceFocus
                disableAutoFocus
            >
                <DialogTitle>{editMode ? 'Edit Teacher' : 'Add New Teacher'}</DialogTitle>
                <DialogContent>
                    <TextField
                        autoFocus
                        margin="dense"
                        name="full_name"
                        label="Full Name"
                        type="text"
                        fullWidth
                        variant="outlined"
                        value={formData.full_name}
                        onChange={handleChange}
                    />
                    <TextField
                        margin="dense"
                        name="email"
                        label="Email Address"
                        type="email"
                        fullWidth
                        variant="outlined"
                        value={formData.email}
                        onChange={handleChange}
                    />
                    <TextField
                        margin="dense"
                        name="password"
                        label={editMode ? "Password (leave blank to keep current)" : "Password"}
                        type="password"
                        fullWidth
                        variant="outlined"
                        value={formData.password}
                        onChange={handleChange}
                    />
                    <TextField
                        margin="dense"
                        name="qualification"
                        label="Qualification"
                        type="text"
                        fullWidth
                        variant="outlined"
                        value={formData.qualification}
                        onChange={handleChange}
                    />
                    <TextField
                        margin="dense"
                        name="subject_specialization"
                        label="Specialization"
                        type="text"
                        fullWidth
                        variant="outlined"
                        value={formData.subject_specialization}
                        onChange={handleChange}
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

export default Teachers;