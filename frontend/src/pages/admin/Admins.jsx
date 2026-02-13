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
    const { enqueueSnackbar } = useSnackbar();

    const fetchAdmins = async () => {
        setLoading(true);
        try {
            const response = await api.get('/admins/');
            setAdmins(response.data);
        } catch (error) {
            enqueueSnackbar('Failed to fetch admins', { variant: 'error' });
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
                enqueueSnackbar('Admin deleted successfully', { variant: 'success' });
                fetchAdmins();
            } catch (error) {
                enqueueSnackbar(error.response?.data?.detail || 'Failed to delete admin', { variant: 'error' });
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
                enqueueSnackbar('Admin updated successfully', { variant: 'success' });
            } else {
                await api.post('/admins/', formData);
                enqueueSnackbar('Admin added successfully', { variant: 'success' });
            }
            fetchAdmins();
            handleClose();
        } catch (error) {
            enqueueSnackbar(error.response?.data?.detail || 'Operation failed', { variant: 'error' });
        }
    };

    const columns = [
        { field: 'full_name', headerName: 'Name', width: 200 },
        { field: 'email', headerName: 'Email', width: 250 },
        { field: 'department', headerName: 'Department', width: 150 },
        { field: 'position', headerName: 'Position', width: 180 },
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
                <Typography variant="h5" fontWeight="bold">Admins Management</Typography>
                <Box>
                    <Button 
                        startIcon={<RefreshIcon />} 
                        onClick={fetchAdmins} 
                        sx={{ mr: 1 }}
                    >
                        Refresh
                    </Button>
                    <Button 
                        variant="contained" 
                        startIcon={<AddIcon />} 
                        onClick={handleOpen}
                    >
                        Add Admin
                    </Button>
                </Box>
            </Box>

            <Paper sx={{ height: '100%', width: '100%' }}>
                <DataGrid
                    rows={admins}
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
                <DialogTitle>{editMode ? 'Edit Admin' : 'Add New Admin'}</DialogTitle>
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
                        name="department"
                        label="Department"
                        type="text"
                        fullWidth
                        variant="outlined"
                        value={formData.department}
                        onChange={handleChange}
                    />
                    <TextField
                        margin="dense"
                        name="position"
                        label="Position"
                        type="text"
                        fullWidth
                        variant="outlined"
                        value={formData.position}
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

export default Admins;
