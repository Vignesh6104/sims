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
    Stack,
    LinearProgress
} from '@mui/material';
import api from '../../api/axios';
import { useAuth } from '../../context/AuthContext';

const Attendance = () => {
    const { user } = useAuth();
    const [attendance, setAttendance] = useState([]);
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({ present: 0, absent: 0, late: 0, total: 0, percentage: 0 });

    useEffect(() => {
        const fetchAttendance = async () => {
            try {
                const response = await api.get(`/attendance?student_id=${user.sub}`);
                setAttendance(response.data);
                
                const total = response.data.length;
                const present = response.data.filter(r => r.status === 'present').length;
                const absent = response.data.filter(r => r.status === 'absent').length;
                const late = response.data.filter(r => r.status === 'late').length;
                
                const percentage = total > 0 ? Math.round(((present + (late * 0.5)) / total) * 100) : 0;
                
                setStats({ present, absent, late, total, percentage });
            } catch (error) {
                console.error("Failed to fetch attendance", error);
            } finally {
                setLoading(false);
            }
        };

        if (user?.sub) fetchAttendance();
    }, [user]);

    const getStatusChip = (status) => {
        switch (status) {
            case 'present': return <Chip label="Present" color="success" size="small" variant="outlined" />;
            case 'absent': return <Chip label="Absent" color="error" size="small" variant="outlined" />;
            case 'late': return <Chip label="Late" color="warning" size="small" variant="outlined" />;
            default: return <Chip label={status} size="small" />;
        }
    };

    if (loading) return <CircularProgress />;

    return (
        <Box>
            <Typography variant="h4" fontWeight="bold" sx={{ mb: 3 }}>
                My Attendance
            </Typography>

            <Grid container spacing={3} sx={{ mb: 4 }}>
                {/* Percentage Card */}
                <Grid item xs={12} md={4}>
                    <Card sx={{ height: '100%', bgcolor: 'primary.main', color: 'white' }}>
                        <CardContent sx={{ textAlign: 'center', pt: 4 }}>
                            <Typography variant="h2" fontWeight="bold">
                                {stats.percentage}%
                            </Typography>
                            <Typography variant="subtitle1" sx={{ opacity: 0.8 }}>
                                Overall Attendance
                            </Typography>
                            <Box sx={{ mt: 2 }}>
                                <Chip 
                                    label={stats.percentage >= 75 ? "Good Standing" : "Attendance Shortage"} 
                                    color={stats.percentage >= 75 ? "success" : "error"}
                                    sx={{ bgcolor: 'white', color: stats.percentage >= 75 ? 'success.main' : 'error.main' }}
                                />
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Summary Details */}
                <Grid item xs={12} md={8}>
                    <Card sx={{ height: '100%' }}>
                        <CardContent>
                            <Typography variant="h6" fontWeight="bold" sx={{ mb: 3 }}>Summary</Typography>
                            <Grid container spacing={2}>
                                <Grid item xs={4}>
                                    <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'grey.50' }}>
                                        <Typography variant="h4" color="primary.main">{stats.total}</Typography>
                                        <Typography variant="caption" color="text.secondary">Working Days</Typography>
                                    </Paper>
                                </Grid>
                                <Grid item xs={4}>
                                    <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'success.50' }}>
                                        <Typography variant="h4" color="success.main">{stats.present}</Typography>
                                        <Typography variant="caption" color="text.secondary">Days Present</Typography>
                                    </Paper>
                                </Grid>
                                <Grid item xs={4}>
                                    <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'error.50' }}>
                                        <Typography variant="h4" color="error.main">{stats.absent}</Typography>
                                        <Typography variant="caption" color="text.secondary">Days Absent</Typography>
                                    </Paper>
                                </Grid>
                            </Grid>
                            
                            <Box sx={{ mt: 4 }}>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                    <Typography variant="body2">Attendance Progress</Typography>
                                    <Typography variant="body2">{stats.percentage}%</Typography>
                                </Box>
                                <LinearProgress variant="determinate" value={stats.percentage} color={stats.percentage < 75 ? "error" : "primary"} sx={{ height: 10, borderRadius: 5 }} />
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Detailed Table */}
            <Paper sx={{ width: '100%', overflow: 'hidden' }}>
                <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
                    <Typography variant="h6" fontWeight="bold">Monthly Log</Typography>
                </Box>
                <TableContainer sx={{ maxHeight: 440 }}>
                    <Table stickyHeader>
                        <TableHead>
                            <TableRow>
                                <TableCell>Date</TableCell>
                                <TableCell>Day</TableCell>
                                <TableCell>Status</TableCell>
                                <TableCell>Class</TableCell>
                                <TableCell>Remarks</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {attendance.length > 0 ? attendance.map((record) => (
                                <TableRow key={record.id} hover>
                                    <TableCell>{new Date(record.date).toLocaleDateString()}</TableCell>
                                    <TableCell>{new Date(record.date).toLocaleDateString('en-US', { weekday: 'long' })}</TableCell>
                                    <TableCell>{getStatusChip(record.status)}</TableCell>
                                    <TableCell>Class A</TableCell> {/* Placeholder, backend response doesn't join Class yet */}
                                    <TableCell>{record.remarks || '-'}</TableCell>
                                </TableRow>
                            )) : (
                                <TableRow>
                                    <TableCell colSpan={5} align="center">No records found</TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Paper>
        </Box>
    );
};

export default Attendance;