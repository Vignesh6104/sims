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
    Select,
    MenuItem,
    FormControl,
    InputLabel
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { Add as AddIcon, Refresh as RefreshIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import api from '../../api/axios';
import { useSnackbar } from 'notistack';

const Classes = () => {
    const [classes, setClasses] = useState([]);
    const [teachers, setTeachers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [open, setOpen] = useState(false);
    const [editMode, setEditMode] = useState(false);
    const [selectedId, setSelectedId] = useState(null);
    const [formData, setFormData] = useState({
        name: '',
        teacher_id: ''
    });
    const { enqueueSnackbar } = useSnackbar();

    const fetchData = async () => {
        setLoading(true);
        try {
            const [classesRes, teachersRes] = await Promise.all([
                api.get('/class_rooms/'),
                api.get('/teachers/')
            ]);
            setClasses(classesRes.data);
            setTeachers(teachersRes.data);
        } catch (error) {
            enqueueSnackbar('Failed to fetch data', { variant: 'error' });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const handleOpen = () => {
        setEditMode(false);
        setFormData({ name: '', teacher_id: '' });
        setOpen(true);
    };

    const handleEdit = (cls) => {
        setEditMode(true);
        setSelectedId(cls.id);
        setFormData({
            name: cls.name,
            teacher_id: cls.teacher_id || ''
        });
        setOpen(true);
    };

    const handleDelete = async (id) => {
        if (window.confirm('Are you sure you want to delete this class?')) {
            try {
                await api.delete(`/class_rooms/${id}/`);
                enqueueSnackbar('Class deleted successfully', { variant: 'success' });
                fetchData();
            } catch (error) {
                enqueueSnackbar('Failed to delete class', { variant: 'error' });
            }
        }
    };

    const handleClose = () => setOpen(false);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async () => {
        try {
            const payload = { ...formData };
            if (payload.teacher_id === '') payload.teacher_id = null;

            if (editMode) {
                await api.put(`/class_rooms/${selectedId}/`, payload);
                enqueueSnackbar('Class updated successfully', { variant: 'success' });
            } else {
                await api.post('/class_rooms/', payload);
                enqueueSnackbar('Class added successfully', { variant: 'success' });
            }
            fetchData();
            handleClose();
        } catch (error) {
            enqueueSnackbar(error.response?.data?.detail || 'Operation failed', { variant: 'error' });
        }
    };

    const columns = [
        { field: 'name', headerName: 'Class Name', width: 200 },
        { 
            field: 'teacher_id', 
            headerName: 'Class Teacher', 
            width: 250,
            valueGetter: (params) => {
                const teacher = teachers.find(t => t.id === params.row.teacher_id);
                return teacher ? teacher.full_name : 'Not Assigned';
            }
        },
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
                <Typography variant="h5" fontWeight="bold">Classes Management</Typography>
                <Box>
                    <Button 
                        startIcon={<RefreshIcon />} 
                        onClick={fetchData} 
                        sx={{ mr: 1 }}
                    >
                        Refresh
                    </Button>
                    <Button 
                        variant="contained" 
                        startIcon={<AddIcon />} 
                        onClick={handleOpen}
                    >
                        Add Class
                    </Button>
                </Box>
            </Box>

            <Paper sx={{ height: '100%', width: '100%' }}>
                <DataGrid
                    rows={classes}
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
                <DialogTitle>{editMode ? 'Edit Class' : 'Add New Class'}</DialogTitle>
                <DialogContent>
                    <TextField
                        autoFocus
                        margin="dense"
                        name="name"
                        label="Class Name"
                        type="text"
                        fullWidth
                        variant="outlined"
                        value={formData.name}
                        onChange={handleChange}
                    />
                    <FormControl fullWidth margin="dense">
                        <InputLabel>Class Teacher</InputLabel>
                        <Select
                            name="teacher_id"
                            value={formData.teacher_id}
                            label="Class Teacher"
                            onChange={handleChange}
                        >
                            <MenuItem value=""><em>None</em></MenuItem>
                            {teachers.map((teacher) => (
                                <MenuItem key={teacher.id} value={teacher.id}>
                                    {teacher.full_name}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
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

export default Classes;
