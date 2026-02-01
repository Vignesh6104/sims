import React, { useEffect, useState } from 'react';
import { 
    Grid, 
    Paper, 
    Typography, 
    Box, 
    CircularProgress, 
    Card, 
    CardContent, 
    Avatar, 
    Alert,
    Stack
} from '@mui/material';
import { 
    EventAvailable, 
    School, 
    Assignment, 
    TrendingUp, 
    Warning, 
    CheckCircle,
    ErrorOutline
} from '@mui/icons-material';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';

const StatCard = ({ title, value, icon, color, status }) => (
    <Card sx={{ height: '100%' }}>
        <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ bgcolor: `${color}.light`, color: `${color}.main`, width: 56, height: 56 }}>
                    {icon}
                </Avatar>
                {status && (
                    <Typography 
                        variant="caption" 
                        sx={{ 
                            color: status === 'Good' ? 'success.main' : status === 'Warning' ? 'warning.main' : 'error.main',
                            fontWeight: 'bold',
                            border: 1,
                            borderColor: 'divider',
                            px: 1,
                            borderRadius: 1
                        }}
                    >
                        {status}
                    </Typography>
                )}
            </Box>
            <Typography color="text.secondary" variant="overline">
                {title}
            </Typography>
            <Typography variant="h4" fontWeight="bold">
                {value}
            </Typography>
        </CardContent>
    </Card>
);

const StudentDashboard = () => {
    const { user } = useAuth();
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState(null);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await api.get('/dashboard/student/stats');
                setData(response.data);
            } catch (error) {
                console.error("Failed to fetch student stats", error);
            } finally {
                setLoading(false);
            }
        };

        if (user?.sub) fetchStats();
    }, [user]);

    if (loading) return (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
            <CircularProgress />
        </Box>
    );

    if (!data) return <Typography color="error">Failed to load data.</Typography>;

    return (
        <Box>
            <Box sx={{ mb: 4 }}>
                <Typography variant="h4" fontWeight="bold">
                    Welcome back, {user?.full_name}
                </Typography>
                <Typography variant="subtitle1" color="text.secondary">
                    Class: {data.classroom.name}
                </Typography>
            </Box>

            {/* Alerts Section */}
            <Stack sx={{ mb: 4 }} spacing={2}>
                {data.alerts.map((alert, index) => (
                    alert && (
                        <Alert severity={alert.type} key={index} icon={alert.type === 'warning' ? <Warning /> : <CheckCircle />}>
                            {alert.msg}
                        </Alert>
                    )
                ))}
            </Stack>

            {/* Overview Cards */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard 
                        title="Attendance" 
                        value={`${data.attendance.percentage}%`} 
                        icon={<EventAvailable />} 
                        color="primary"
                        status={data.attendance.status}
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard 
                        title="Avg Marks" 
                        value={`${data.marks.average}`} 
                        icon={<TrendingUp />} 
                        color="secondary"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard 
                        title="Exams Taken" 
                        value={data.marks.total_exams} 
                        icon={<Assignment />} 
                        color="info"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard 
                        title="Latest Result" 
                        value={data.marks.latest_result ? data.marks.latest_result.split(' ')[0] : 'N/A'} // Just score
                        icon={<School />} 
                        color="success"
                        status={data.marks.latest_result || 'N/A'}
                    />
                </Grid>
            </Grid>

            {/* Quick Summary Panel */}
            <Paper sx={{ p: 3 }}>
                <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>Quick Summary</Typography>
                <Grid container spacing={2}>
                    <Grid item xs={12} sm={4}>
                        <Box sx={{ p: 2, bgcolor: 'background.default', borderRadius: 2 }}>
                            <Typography variant="caption" color="text.secondary">Last Attendance</Typography>
                            <Typography variant="body1" fontWeight="medium">
                                {data.attendance.last_marked ? new Date(data.attendance.last_marked).toLocaleDateString() : 'N/A'}
                            </Typography>
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={4}>
                        <Box sx={{ p: 2, bgcolor: 'background.default', borderRadius: 2 }}>
                            <Typography variant="caption" color="text.secondary">Latest Exam</Typography>
                            <Typography variant="body1" fontWeight="medium">
                                {data.marks.latest_result || 'N/A'}
                            </Typography>
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={4}>
                        <Box sx={{ p: 2, bgcolor: 'background.default', borderRadius: 2 }}>
                            <Typography variant="caption" color="text.secondary">Class Teacher</Typography>
                            <Typography variant="body1" fontWeight="medium">
                                Assigned
                            </Typography>
                        </Box>
                    </Grid>
                </Grid>
            </Paper>
        </Box>
    );
};

export default StudentDashboard;