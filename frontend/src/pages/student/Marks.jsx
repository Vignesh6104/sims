import React, { useState, useEffect } from 'react';
import {
    Box,
    Paper,
    Typography,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Chip,
    Grid,
    Card,
    CardContent,
    CircularProgress,
    Avatar,
    Button
} from '@mui/material';
import { Assignment, EmojiEvents, TrendingUp, Download as DownloadIcon } from '@mui/icons-material';
import api from '../../api/axios';
import { useAuth } from '../../context/AuthContext';
import { useSnackbar } from 'notistack';

const StatCard = ({ title, value, icon, color }) => (
    <Card sx={{ height: '100%' }}>
        <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box>
                    <Typography color="text.secondary" gutterBottom variant="overline">
                        {title}
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                        {value}
                    </Typography>
                </Box>
                <Avatar sx={{ bgcolor: `${color}.light`, color: `${color}.main`, width: 56, height: 56 }}>
                    {icon}
                </Avatar>
            </Box>
        </CardContent>
    </Card>
);

const Marks = () => {
    const { user } = useAuth();
    const { enqueueSnackbar } = useSnackbar();
    const [marks, setMarks] = useState([]);
    const [submissions, setSubmissions] = useState([]);
    const [assignments, setAssignments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({ total_exams: 0, highest: 0, average: 0 });

    useEffect(() => {
        const fetchAllData = async () => {
            try {
                const [marksRes, submissionsRes, assignmentsRes] = await Promise.all([
                    api.get(`/marks/student/${user.sub}`),
                    api.get('/assignments/my-submissions'),
                    // We need assignment titles, we can fetch all or specific ones. 
                    // To keep it simple, let's assume we can map them if we had an endpoint or just show IDs/names.
                    // For now, let's fetch assignments for the class if we have class_id
                ]);
                
                const data = marksRes.data;
                const subs = submissionsRes.data.filter(s => s.grade !== null); // Only show graded ones
                
                // Calculate stats based on Exams
                const total_exams = data.length;
                const scores = data.map(m => (m.score / m.max_score) * 100);
                const highest = scores.length > 0 ? Math.max(...scores).toFixed(1) : 0;
                const sum = scores.reduce((a, b) => a + b, 0);
                const average = scores.length > 0 ? (sum / scores.length).toFixed(1) : 0;
                
                setMarks(data);
                setSubmissions(subs);
                setStats({ total_exams, highest, average });

                // Try to fetch assignments to get titles
                const studentRes = await api.get(`/students/${user.sub}`);
                const classId = studentRes.data.class_id;
                if (classId) {
                    const assignRes = await api.get(`/assignments/class/${classId}`);
                    setAssignments(assignRes.data);
                }

            } catch (error) {
                console.error("Failed to fetch marks data", error);
            } finally {
                setLoading(false);
            }
        };

        if (user?.sub) fetchAllData();
    }, [user]);

    const getAssignmentTitle = (id) => assignments.find(a => a.id === id)?.title || 'Assignment';

    const getGrade = (percentage) => {
        if (percentage >= 90) return 'A+';
        if (percentage >= 80) return 'A';
        if (percentage >= 70) return 'B';
        if (percentage >= 60) return 'C';
        if (percentage >= 50) return 'D';
        return 'F';
    };

    const handleDownloadReport = async () => {
        try {
            const response = await api.get(`/marks/report-card/${user.sub}`, {
                responseType: 'blob',
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `Report_Card.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
            enqueueSnackbar("Report card downloaded successfully", { variant: 'success' });
        } catch (error) {
            console.error("Download failed", error);
            enqueueSnackbar("Failed to download report card", { variant: 'error' });
        }
    };

    const getResultColor = (percentage) => percentage >= 50 ? 'success' : 'error';

    if (loading) return <CircularProgress />;

    return (
        <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h4" fontWeight="bold">
                    My Performance
                </Typography>
                <Button 
                    variant="contained" 
                    color="secondary" 
                    startIcon={<DownloadIcon />}
                    onClick={handleDownloadReport}
                >
                    Download Report Card
                </Button>
            </Box>

            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} sm={4}>
                    <StatCard 
                        title="Exams Attempted" 
                        value={stats.total_exams} 
                        icon={<Assignment />} 
                        color="info" 
                    />
                </Grid>
                <Grid item xs={12} sm={4}>
                    <StatCard 
                        title="Highest Score %" 
                        value={`${stats.highest}%`} 
                        icon={<EmojiEvents />} 
                        color="warning" 
                    />
                </Grid>
                <Grid item xs={12} sm={4}>
                    <StatCard 
                        title="Average Score %" 
                        value={`${stats.average}%`} 
                        icon={<TrendingUp />} 
                        color="success" 
                    />
                </Grid>
            </Grid>

            <Paper sx={{ width: '100%', overflow: 'hidden' }}>
                <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
                    <Typography variant="h6" fontWeight="bold">Detailed Report</Typography>
                </Box>
                <TableContainer sx={{ maxHeight: 440 }}>
                    <Table stickyHeader>
                        <TableHead>
                            <TableRow>
                                <TableCell>Subject</TableCell>
                                <TableCell align="center">Score</TableCell>
                                <TableCell align="center">Total</TableCell>
                                <TableCell align="center">Percentage</TableCell>
                                <TableCell align="center">Grade</TableCell>
                                <TableCell align="center">Result</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {marks.length > 0 ? marks.map((mark) => {
                                const percentage = (mark.score / mark.max_score) * 100;
                                return (
                                    <TableRow key={mark.id} hover>
                                        <TableCell sx={{ fontWeight: 'bold' }}>{mark.subject}</TableCell>
                                        <TableCell align="center">{mark.score}</TableCell>
                                        <TableCell align="center">{mark.max_score}</TableCell>
                                        <TableCell align="center">{percentage.toFixed(1)}%</TableCell>
                                        <TableCell align="center">
                                            <Chip label={getGrade(percentage)} size="small" color="primary" variant="outlined" />
                                        </TableCell>
                                        <TableCell align="center">
                                            <Chip 
                                                label={percentage >= 50 ? "PASS" : "FAIL"} 
                                                color={getResultColor(percentage)} 
                                                size="small" 
                                            />
                                        </TableCell>
                                    </TableRow>
                                );
                            }) : (
                                <TableRow>
                                    <TableCell colSpan={6} align="center">No marks recorded</TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Paper>

            <Typography variant="h5" fontWeight="bold" sx={{ mt: 5, mb: 2 }}>
                Assignment Grades
            </Typography>
            <Paper sx={{ width: '100%', overflow: 'hidden', mb: 4 }}>
                <TableContainer>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>Assignment</TableCell>
                                <TableCell align="center">Submission Date</TableCell>
                                <TableCell align="center">Grade</TableCell>
                                <TableCell>Feedback</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {submissions.length > 0 ? submissions.map((sub) => (
                                <TableRow key={sub.id} hover>
                                    <TableCell sx={{ fontWeight: 'bold' }}>{getAssignmentTitle(sub.assignment_id)}</TableCell>
                                    <TableCell align="center">{sub.submission_date}</TableCell>
                                    <TableCell align="center">
                                        <Chip 
                                            label={sub.grade} 
                                            color="primary" 
                                            size="small" 
                                            variant="filled"
                                            sx={{ fontWeight: 'bold' }}
                                        />
                                    </TableCell>
                                    <TableCell color="text.secondary italic">
                                        {sub.feedback || "No feedback provided"}
                                    </TableCell>
                                </TableRow>
                            )) : (
                                <TableRow>
                                    <TableCell colSpan={4} align="center">No graded assignments found</TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Paper>
        </Box>
    );
};

export default Marks;
