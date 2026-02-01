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
    IconButton,
    Tooltip
} from '@mui/material';
import { Add as AddIcon, Assignment as AssignIcon, Check as CheckIcon } from '@mui/icons-material';
import api from '../../api/axios';
import { useAuth } from '../../context/AuthContext';
import { useSnackbar } from 'notistack';

const Assignments = () => {
    const { user } = useAuth();
    const [assignments, setAssignments] = useState([]);
    const [classes, setClasses] = useState([]);
    const [subjects, setSubjects] = useState([]);
    
    // Create/Edit State
    const [open, setOpen] = useState(false);
    const [form, setForm] = useState({
        title: '',
        description: '',
        class_id: '',
        subject_id: '',
        due_date: ''
    });

    // Grading State
    const [submissions, setSubmissions] = useState([]);
    const [openGrade, setOpenGrade] = useState(false);
    const [selectedAssignment, setSelectedAssignment] = useState(null);
    const [gradeForm, setGradeForm] = useState({ grade: '', feedback: '' });
    const [selectedSubmissionId, setSelectedSubmissionId] = useState(null);

    const { enqueueSnackbar } = useSnackbar();

    useEffect(() => {
        fetchInitialData();
        fetchAssignments();
    }, []);

    const fetchInitialData = async () => {
        try {
            const [clsRes, subRes] = await Promise.all([
                api.get(`/class_rooms?teacher_id=${user.sub}`),
                api.get('/subjects')
            ]);
            setClasses(clsRes.data);
            setSubjects(subRes.data);
        } catch (error) {
            console.error("Failed to fetch metadata");
        }
    };

    const fetchAssignments = async () => {
        try {
            const res = await api.get('/assignments/teacher');
            setAssignments(res.data);
        } catch (error) {
            console.error("Failed to fetch assignments");
        }
    };

    const handleCreate = async () => {
        try {
            await api.post('/assignments', { ...form, teacher_id: user.sub });
            enqueueSnackbar('Assignment created', { variant: 'success' });
            setOpen(false);
            fetchAssignments();
        } catch (error) {
            enqueueSnackbar('Failed to create assignment', { variant: 'error' });
        }
    };

    const handleViewSubmissions = async (assignment) => {
        setSelectedAssignment(assignment);
        try {
            const res = await api.get(`/assignments/submissions/${assignment.id}`);
            setSubmissions(res.data);
            setOpenGrade(true);
        } catch (error) {
            enqueueSnackbar('Failed to fetch submissions', { variant: 'error' });
        }
    };

    const handleGrade = async () => {
        try {
            await api.put(`/assignments/submissions/${selectedSubmissionId}`, {
                grade: parseFloat(gradeForm.grade),
                feedback: gradeForm.feedback
            });
            enqueueSnackbar('Graded successfully', { variant: 'success' });
            // Refresh submissions list
            handleViewSubmissions(selectedAssignment);
            setGradeForm({ grade: '', feedback: '' });
            setSelectedSubmissionId(null);
        } catch (error) {
            enqueueSnackbar('Failed to grade', { variant: 'error' });
        }
    };

    const getClassName = (id) => classes.find(c => c.id === id)?.name || id;
    const getSubjectName = (id) => subjects.find(s => s.id === id)?.name || id;

    return (
        <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
                <Typography variant="h4" fontWeight="bold">Assignments</Typography>
                <Button variant="contained" startIcon={<AddIcon />} onClick={() => setOpen(true)}>
                    Create Assignment
                </Button>
            </Box>

            <Paper sx={{ width: '100%', overflow: 'hidden' }}>
                <TableContainer>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>Title</TableCell>
                                <TableCell>Class</TableCell>
                                <TableCell>Subject</TableCell>
                                <TableCell>Due Date</TableCell>
                                <TableCell align="right">Actions</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {assignments.map((row) => (
                                <TableRow key={row.id}>
                                    <TableCell>{row.title}</TableCell>
                                    <TableCell>{getClassName(row.class_id)}</TableCell>
                                    <TableCell>{getSubjectName(row.subject_id)}</TableCell>
                                    <TableCell>{row.due_date}</TableCell>
                                    <TableCell align="right">
                                        <Tooltip title="View Submissions">
                                            <IconButton color="primary" onClick={() => handleViewSubmissions(row)}>
                                                <AssignIcon />
                                            </IconButton>
                                        </Tooltip>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Paper>

            {/* Create Dialog */}
            <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
                <DialogTitle>Create Assignment</DialogTitle>
                <DialogContent>
                    <TextField
                        autoFocus
                        margin="dense"
                        label="Title"
                        fullWidth
                        value={form.title}
                        onChange={(e) => setForm({...form, title: e.target.value})}
                    />
                    <TextField
                        margin="dense"
                        label="Description"
                        fullWidth
                        multiline
                        rows={3}
                        value={form.description}
                        onChange={(e) => setForm({...form, description: e.target.value})}
                    />
                    <FormControl fullWidth margin="dense">
                        <InputLabel>Class</InputLabel>
                        <Select
                            value={form.class_id}
                            label="Class"
                            onChange={(e) => setForm({...form, class_id: e.target.value})}
                        >
                            {classes.map(c => <MenuItem key={c.id} value={c.id}>{c.name}</MenuItem>)}
                        </Select>
                    </FormControl>
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
                    <TextField
                        margin="dense"
                        label="Due Date"
                        type="date"
                        fullWidth
                        InputLabelProps={{ shrink: true }}
                        value={form.due_date}
                        onChange={(e) => setForm({...form, due_date: e.target.value})}
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setOpen(false)}>Cancel</Button>
                    <Button onClick={handleCreate} variant="contained">Create</Button>
                </DialogActions>
            </Dialog>

            {/* Grading Dialog */}
            <Dialog open={openGrade} onClose={() => setOpenGrade(false)} maxWidth="md" fullWidth>
                <DialogTitle>Submissions: {selectedAssignment?.title}</DialogTitle>
                <DialogContent dividers>
                    <TableContainer>
                        <Table size="small">
                            <TableHead>
                                <TableRow>
                                    <TableCell>Student ID</TableCell>
                                    <TableCell>Date</TableCell>
                                    <TableCell>Content</TableCell>
                                    <TableCell>Grade</TableCell>
                                    <TableCell>Action</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {submissions.map((sub) => (
                                    <TableRow key={sub.id}>
                                        <TableCell>{sub.student_id}</TableCell>
                                        <TableCell>{sub.submission_date}</TableCell>
                                        <TableCell>
                                            {sub.content?.startsWith('/uploads') ? (
                                                <Button 
                                                    component="a" 
                                                    href={`http://localhost:8000${sub.content}`} 
                                                    target="_blank" 
                                                    variant="outlined" 
                                                    size="small"
                                                >
                                                    View File
                                                </Button>
                                            ) : (
                                                sub.content
                                            )}
                                        </TableCell>
                                        <TableCell>{sub.grade || '-'}</TableCell>
                                        <TableCell>
                                            {selectedSubmissionId === sub.id ? (
                                                <Box sx={{ display: 'flex', gap: 1 }}>
                                                    <TextField 
                                                        size="small" 
                                                        placeholder="Grade" 
                                                        value={gradeForm.grade}
                                                        onChange={(e) => setGradeForm({...gradeForm, grade: e.target.value})}
                                                        sx={{ width: 80 }}
                                                    />
                                                    <IconButton color="success" onClick={handleGrade}><CheckIcon /></IconButton>
                                                </Box>
                                            ) : (
                                                <Button size="small" onClick={() => setSelectedSubmissionId(sub.id)}>Grade</Button>
                                            )}
                                        </TableCell>
                                    </TableRow>
                                ))}
                                {submissions.length === 0 && <TableRow><TableCell colSpan={5} align="center">No submissions yet.</TableCell></TableRow>}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setOpenGrade(false)}>Close</Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default Assignments;
