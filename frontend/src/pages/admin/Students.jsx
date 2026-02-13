import React, { useState, useEffect, useRef } from 'react';
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
    MenuItem,
    Select,
    FormControl,
    InputLabel
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { Add as AddIcon, Refresh as RefreshIcon, Edit as EditIcon, Delete as DeleteIcon, CloudUpload as CloudUploadIcon } from '@mui/icons-material';
import api from '../../api/axios';
import { useSnackbar } from 'notistack';

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
    const { enqueueSnackbar } = useSnackbar();
    const fileInputRef = useRef(null);

    const fetchStudents = async () => {
        setLoading(true);
        try {
            const response = await api.get('/students/');
            setStudents(response.data);
        } catch (error) {
            enqueueSnackbar('Failed to fetch students', { variant: 'error' });
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
            class_id: student.class_id || ''
        });
        setOpen(true);
    };

    const handleDelete = async (id) => {
        if (window.confirm('Are you sure you want to delete this student?')) {
            try {
                await api.delete(`/students/${id}/`);
                enqueueSnackbar('Student deleted successfully', { variant: 'success' });
                fetchStudents();
            } catch (error) {
                enqueueSnackbar('Failed to delete student', { variant: 'error' });
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
            
            enqueueSnackbar(response.data.message, { variant: 'success' });
            if (response.data.errors && response.data.errors.length > 0) {
                response.data.errors.forEach(err => {
                    enqueueSnackbar(err, { variant: 'warning' });
                });
            }
            fetchStudents();
        } catch (error) {
            enqueueSnackbar(error.response?.data?.detail || 'Import failed', { variant: 'error' });
        } finally {
            setLoading(false);
            event.target.value = null; // Reset input
        }
    };

    const handleClose = () => setOpen(false);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async () => {
        try {
            const payload = { ...formData };
            // Ensure class_id is null if empty string
            if (payload.class_id === '') payload.class_id = null;
            
            if (editMode) {
                if (!payload.password) delete payload.password;
                await api.put(`/students/${selectedId}/`, payload);
                enqueueSnackbar('Student updated successfully', { variant: 'success' });
            } else {
                await api.post('/auth/register/student', payload);
                enqueueSnackbar('Student added successfully', { variant: 'success' });
            }
            fetchStudents();
            handleClose();
        } catch (error) {
            enqueueSnackbar(error.response?.data?.detail || 'Operation failed', { variant: 'error' });
        }
    };

    const columns = [
        { field: 'roll_number', headerName: 'Roll No', width: 130 },
        { field: 'full_name', headerName: 'Name', width: 200 },
        { field: 'email', headerName: 'Email', width: 250 },
        { 
            field: 'class_id', 
            headerName: 'Class', 
            width: 150,
            valueGetter: (params) => {
                const cls = classes.find(c => c.id === params.row.class_id);
                return cls ? cls.name : 'N/A';
            }
        },
        { field: 'address', headerName: 'Address', width: 200 },
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
                <Typography variant="h5" fontWeight="bold">Students Management</Typography>
                <Box>
                    <input
                        type="file"
                        ref={fileInputRef}
                        style={{ display: 'none' }}
                        onChange={handleFileChange}
                        accept=".csv"
                    />
                    <Button 
                        startIcon={<CloudUploadIcon />} 
                        onClick={handleImportClick} 
                        sx={{ mr: 1 }}
                        variant="outlined"
                    >
                        Import CSV
                    </Button>
                    <Button 
                        startIcon={<RefreshIcon />} 
                        onClick={fetchStudents} 
                        sx={{ mr: 1 }}
                    >
                        Refresh
                    </Button>
                    <Button 
                        variant="contained" 
                        startIcon={<AddIcon />} 
                        onClick={handleOpen}
                    >
                        Add Student
                    </Button>
                </Box>
            </Box>

            <Paper sx={{ height: '100%', width: '100%' }}>
                <DataGrid
                    rows={students}
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
                <DialogTitle>{editMode ? 'Edit Student' : 'Add New Student'}</DialogTitle>
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
                        label={editMode ? "Password (leave blank to keep)" : "Password"}
                        type="password"
                        fullWidth
                        variant="outlined"
                        value={formData.password}
                        onChange={handleChange}
                    />
                    <TextField
                        margin="dense"
                        name="roll_number"
                        label="Roll Number"
                        type="text"
                        fullWidth
                        variant="outlined"
                        value={formData.roll_number}
                        onChange={handleChange}
                    />
                    <TextField
                        margin="dense"
                        name="date_of_birth"
                        label="Date of Birth"
                        type="date"
                        fullWidth
                        variant="outlined"
                        value={formData.date_of_birth}
                        onChange={handleChange}
                        InputLabelProps={{ shrink: true }}
                    />
                    <FormControl fullWidth margin="dense">
                        <InputLabel>Class</InputLabel>
                        <Select
                            name="class_id"
                            value={formData.class_id}
                            label="Class"
                            onChange={handleChange}
                        >
                            <MenuItem value=""><em>None</em></MenuItem>
                            {classes.map((cls) => (
                                <MenuItem key={cls.id} value={cls.id}>
                                    {cls.name}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                    <TextField
                        margin="dense"
                        name="address"
                        label="Address"
                        type="text"
                        fullWidth
                        variant="outlined"
                        multiline
                        rows={2}
                        value={formData.address}
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

export default Students;
