import React, { useState, useEffect } from 'react';
import {
    Box,
    Paper,
    Typography,
    Grid,
    Card,
    CardContent,
    Button,
    Chip,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField
} from '@mui/material';
import api from '../../api/axios';
import { useAuth } from '../../context/AuthContext';
import { useSnackbar } from 'notistack';

const Assignments = () => {
    const { user } = useAuth(); // Assume user has class_id if properly fetched or we fetch profile
    const [assignments, setAssignments] = useState([]);
    const [submissions, setSubmissions] = useState([]);
    const [myClassId, setMyClassId] = useState(null);
    
    const [open, setOpen] = useState(false);
    const [selectedAssignment, setSelectedAssignment] = useState(null);
    const [file, setFile] = useState(null);
    
    const { enqueueSnackbar } = useSnackbar();

    useEffect(() => {
        // First fetch student profile to get class_id
        const fetchProfile = async () => {
            try {
                const res = await api.get(`/students/${user.sub}`);
                setMyClassId(res.data.class_id);
            } catch (error) {
                console.error("Failed to fetch profile");
            }
        };
        if (user?.sub) fetchProfile();
    }, [user]);

    const fetchData = async () => {
        if (!myClassId) return;
        try {
            const [assignRes, subRes] = await Promise.all([
                api.get(`/assignments/class/${myClassId}`),
                api.get('/assignments/my-submissions')
            ]);
            setAssignments(assignRes.data);
            setSubmissions(subRes.data);
        } catch (error) {
            console.error("Failed to fetch data");
        }
    };

    useEffect(() => {
        fetchData();
    }, [myClassId]);

    const handleSubmit = async () => {
        if (!file) {
            enqueueSnackbar('Please select a file to submit', { variant: 'warning' });
            return;
        }

        const formData = new FormData();
        formData.append('assignment_id', selectedAssignment.id);
        formData.append('file', file);

        try {
            await api.post('/assignments/submissions', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            enqueueSnackbar('Assignment submitted successfully', { variant: 'success' });
            setOpen(false);
            setFile(null);
            fetchData(); // Refresh to show submission
        } catch (error) {
            enqueueSnackbar(error.response?.data?.detail || 'Failed to submit', { variant: 'error' });
        }
    };

    const handleOpenSubmit = (assignment) => {
        setSelectedAssignment(assignment);
        setFile(null);
        setOpen(true);
    };

    const getSubmission = (assignmentId) => {
        return submissions.find(s => s.assignment_id === assignmentId);
    };

    return (
        <Box>
            <Typography variant="h4" fontWeight="bold" sx={{ mb: 3 }}>
                My Assignments
            </Typography>

            <Grid container spacing={3}>
                {assignments.map((assign) => {
                    const submission = getSubmission(assign.id);
                    return (
                        <Grid item xs={12} md={6} key={assign.id}>
                            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                                <CardContent sx={{ flexGrow: 1 }}>
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1, alignItems: 'start' }}>
                                        <Typography variant="h6">{assign.title}</Typography>
                                        <Box sx={{ textAlign: 'right' }}>
                                            <Chip 
                                                label={submission ? "Submitted" : "Pending"} 
                                                color={submission ? "success" : "warning"} 
                                                size="small" 
                                                sx={{ mb: 1, display: 'block' }}
                                            />
                                            <Typography variant="caption" color="text.secondary">
                                                Due: {assign.due_date}
                                            </Typography>
                                        </Box>
                                    </Box>
                                    <Typography color="text.secondary" paragraph variant="body2">
                                        {assign.description}
                                    </Typography>
                                    
                                    {submission && (
                                        <Box sx={{ mt: 1, mb: 2, p: 1, bgcolor: 'action.hover', borderRadius: 1 }}>
                                            <Typography variant="caption" fontWeight="bold">Submitted on: {submission.submission_date}</Typography>
                                            {submission.grade !== null && (
                                                <Typography variant="body2" color="primary.main" fontWeight="bold">
                                                    Grade: {submission.grade}
                                                </Typography>
                                            )}
                                        </Box>
                                    )}

                                    <Box sx={{ mt: 'auto', display: 'flex', gap: 1 }}>
                                        {!submission || submission.grade === null ? (
                                            <Button 
                                                variant="contained" 
                                                size="small" 
                                                onClick={() => handleOpenSubmit(assign)}
                                            >
                                                {submission ? "Edit Submission" : "Submit Work"}
                                            </Button>
                                        ) : (
                                            <Button variant="contained" size="small" disabled>
                                                Finalized
                                            </Button>
                                        )}
                                        
                                        {submission && (
                                            <Button 
                                                variant="outlined" 
                                                size="small" 
                                                component="a" 
                                                href={`http://localhost:8000${submission.content}`} 
                                                target="_blank"
                                            >
                                                View Uploaded
                                            </Button>
                                        )}
                                    </Box>
                                </CardContent>
                            </Card>
                        </Grid>
                    );
                })}
                {assignments.length === 0 && (
                    <Grid item xs={12}>
                        <Typography color="text.secondary">No assignments found.</Typography>
                    </Grid>
                )}
            </Grid>

            <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
                <DialogTitle>
                    {getSubmission(selectedAssignment?.id) ? "Edit Submission" : "Submit Work"}: {selectedAssignment?.title}
                </DialogTitle>
                <DialogContent>
                    <Box sx={{ mt: 2 }}>
                        {getSubmission(selectedAssignment?.id) && (
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                Re-uploading a file will replace your current submission.
                            </Typography>
                        )}
                        <Button
                            variant="outlined"
                            component="label"
                            fullWidth
                            sx={{ p: 4, borderStyle: 'dashed' }}
                        >
                            {file ? file.name : "Click to select any file"}
                            <input
                                type="file"
                                hidden
                                onChange={(e) => setFile(e.target.files[0])}
                            />
                        </Button>
                        {file && (
                            <Typography variant="caption" display="block" sx={{ mt: 1, textAlign: 'center' }}>
                                Selected: {file.name} ({(file.size / 1024).toFixed(2)} KB)
                            </Typography>
                        )}
                    </Box>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setOpen(false)}>Cancel</Button>
                    <Button onClick={handleSubmit} variant="contained" disabled={!file}>
                        {getSubmission(selectedAssignment?.id) ? "Update Submission" : "Submit"}
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default Assignments;
