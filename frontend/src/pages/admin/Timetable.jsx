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
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Card,
    CardContent,
    IconButton
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon } from '@mui/icons-material';
import api from '../../api/axios';
import { useSnackbar } from 'notistack';

const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
const periods = [1, 2, 3, 4, 5, 6, 7, 8];

const Timetable = () => {
    const [classes, setClasses] = useState([]);
    const [subjects, setSubjects] = useState([]);
    const [teachers, setTeachers] = useState([]);
    const [selectedClass, setSelectedClass] = useState('');
    const [timetable, setTimetable] = useState([]);
    const [open, setOpen] = useState(false);
    const [selectedSlot, setSelectedSlot] = useState({ day: '', period: '' });
    const [form, setForm] = useState({ subject_id: '', teacher_id: '' });
    const { enqueueSnackbar } = useSnackbar();

    useEffect(() => {
        const fetchInitialData = async () => {
            try {
                const [clsRes, subRes, tchRes] = await Promise.all([
                    api.get('/class_rooms'),
                    api.get('/subjects'),
                    api.get('/teachers')
                ]);
                setClasses(clsRes.data);
                setSubjects(subRes.data);
                setTeachers(tchRes.data);
            } catch (error) {
                console.error("Failed to fetch data");
            }
        };
        fetchInitialData();
    }, []);

    useEffect(() => {
        if (selectedClass) {
            fetchTimetable();
        }
    }, [selectedClass]);

    const fetchTimetable = async () => {
        try {
            const res = await api.get(`/timetable/class/${selectedClass}`);
            setTimetable(res.data);
        } catch (error) {
            console.error("Failed to fetch timetable");
        }
    };

    const handleCellClick = (day, period) => {
        setSelectedSlot({ day, period });
        setForm({ subject_id: '', teacher_id: '' });
        setOpen(true);
    };

    const handleSubmit = async () => {
        try {
            await api.post('/timetable', {
                class_id: selectedClass,
                day: selectedSlot.day,
                period: selectedSlot.period,
                subject_id: form.subject_id,
                teacher_id: form.teacher_id
            });
            enqueueSnackbar('Entry added', { variant: 'success' });
            setOpen(false);
            fetchTimetable();
        } catch (error) {
            enqueueSnackbar('Failed to add entry', { variant: 'error' });
        }
    };

    const handleDelete = async (e, id) => {
        e.stopPropagation();
        if (window.confirm('Delete this entry?')) {
            try {
                await api.delete(`/timetable/${id}`);
                fetchTimetable();
            } catch (error) {
                enqueueSnackbar('Failed to delete', { variant: 'error' });
            }
        }
    };

    const getEntry = (day, period) => {
        return timetable.find(t => t.day === day && t.period === period);
    };

    const getSubjectName = (id) => subjects.find(s => s.id === id)?.name;
    const getTeacherName = (id) => teachers.find(t => t.id === id)?.full_name;

    return (
        <Box sx={{ height: '100%', width: '100%' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
                <Typography variant="h5" fontWeight="bold">Timetable Management</Typography>
                <FormControl sx={{ minWidth: 200 }}>
                    <InputLabel>Select Class</InputLabel>
                    <Select
                        value={selectedClass}
                        label="Select Class"
                        onChange={(e) => setSelectedClass(e.target.value)}
                    >
                        {classes.map(c => <MenuItem key={c.id} value={c.id}>{c.name}</MenuItem>)}
                    </Select>
                </FormControl>
            </Box>

            {selectedClass ? (
                <TableContainer component={Paper} elevation={0}>
                    <Table sx={{ minWidth: 800 }}>
                        <TableHead>
                            <TableRow>
                                <TableCell sx={{ borderBottom: 'none', fontWeight: 'bold', width: '150px' }}>Day / Period</TableCell>
                                {periods.map(p => (
                                    <TableCell key={p} align="center" sx={{ borderBottom: 'none', fontWeight: 'bold' }}>{p}</TableCell>
                                ))}
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {days.map(day => (
                                <TableRow key={day}>
                                    <TableCell component="th" scope="row" sx={{ borderBottom: 'none', fontWeight: 'bold' }}>
                                        {day}
                                    </TableCell>
                                    {periods.map(period => {
                                        const entry = getEntry(day, period);
                                        return (
                                            <TableCell key={`${day}-${period}`} sx={{ borderBottom: 'none', p: 0.5 }}>
                                                <Card 
                                                    elevation={0}
                                                    sx={{ 
                                                        height: 80, 
                                                        cursor: 'pointer', 
                                                        bgcolor: entry ? 'primary.50' : 'background.default',
                                                        '&:hover': { bgcolor: 'action.hover' },
                                                        position: 'relative',
                                                        display: 'flex',
                                                        alignItems: 'center',
                                                        justifyContent: 'center'
                                                    }}
                                                    onClick={() => handleCellClick(day, period)}
                                                >
                                                    <CardContent sx={{ p: 1, width: '100%', '&:last-child': { pb: 1 } }}>
                                                        {entry ? (
                                                            <>
                                                                <Typography variant="subtitle2" fontWeight="bold" noWrap align="center">
                                                                    {getSubjectName(entry.subject_id)}
                                                                </Typography>
                                                                <Typography variant="caption" display="block" noWrap align="center">
                                                                    {getTeacherName(entry.teacher_id)}
                                                                </Typography>
                                                                <IconButton 
                                                                    size="small" 
                                                                    sx={{ position: 'absolute', top: 0, right: 0 }}
                                                                    onClick={(e) => handleDelete(e, entry.id)}
                                                                >
                                                                    <DeleteIcon fontSize="inherit" color="error" />
                                                                </IconButton>
                                                            </>
                                                        ) : (
                                                            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', opacity: 0.3 }}>
                                                                <AddIcon />
                                                            </Box>
                                                        )}
                                                    </CardContent>
                                                </Card>
                                            </TableCell>
                                        );
                                    })}
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            ) : (
                <Typography align="center" color="text.secondary" sx={{ mt: 10 }}>
                    Please select a class to view/edit timetable.
                </Typography>
            )}

            <Dialog open={open} onClose={() => setOpen(false)}>
                <DialogTitle>Assign Period ({selectedSlot.day} - Period {selectedSlot.period})</DialogTitle>
                <DialogContent sx={{ minWidth: 300 }}>
                    <FormControl fullWidth margin="dense">
                        <InputLabel>Subject</InputLabel>
                        <Select
                            value={form.subject_id}
                            label="Subject"
                            onChange={(e) => setForm({...form, subject_id: e.target.value})}
                        >
                            {subjects.map(s => <MenuItem key={s.id} value={s.id}>{s.name}</MenuItem>)}
                        </Select>
                    </FormControl>
                    <FormControl fullWidth margin="dense">
                        <InputLabel>Teacher</InputLabel>
                        <Select
                            value={form.teacher_id}
                            label="Teacher"
                            onChange={(e) => setForm({...form, teacher_id: e.target.value})}
                        >
                            {teachers.map(t => <MenuItem key={t.id} value={t.id}>{t.full_name}</MenuItem>)}
                        </Select>
                    </FormControl>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setOpen(false)}>Cancel</Button>
                    <Button onClick={handleSubmit} variant="contained">Save</Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default Timetable;
