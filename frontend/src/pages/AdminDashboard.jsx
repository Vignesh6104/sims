import React, { useEffect, useState } from 'react';
import { Grid, Paper, Typography, Box, CircularProgress, List, ListItem, ListItemText, ListItemAvatar, Avatar } from '@mui/material';
import api from '../api/axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as ChartTooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { School, People, Class, EventNote, PersonAdd } from '@mui/icons-material';

const StatCard = ({ title, value, icon, color }) => (
    <Paper
        sx={{
            p: 3,
            display: 'flex',
            flexDirection: 'column',
            height: 140,
            justifyContent: 'space-between',
            position: 'relative',
            overflow: 'hidden'
        }}
    >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <Box>
                <Typography color="text.secondary" variant="subtitle2" textTransform="uppercase">
                    {title}
                </Typography>
                <Typography variant="h3" fontWeight="bold" sx={{ mt: 1 }}>
                    {value}
                </Typography>
            </Box>
            <Box
                sx={{
                    backgroundColor: `${color}.light`,
                    color: `${color}.main`,
                    borderRadius: '50%',
                    p: 1,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                }}
            >
                {icon}
            </Box>
        </Box>
        {/* Decorative circle */}
        <Box
            sx={{
                position: 'absolute',
                bottom: -20,
                right: -20,
                width: 100,
                height: 100,
                borderRadius: '50%',
                backgroundColor: `${color}.main`,
                opacity: 0.1
            }}
        />
    </Paper>
);

const AdminDashboard = () => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await api.get('/dashboard/stats/');
                setStats(response.data);
            } catch (error) {
                console.error("Failed to fetch dashboard stats", error);
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
    }, []);

    if (loading) return (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
            <CircularProgress />
        </Box>
    );

    const pieData = [
        { name: 'Students', value: stats?.total_students || 0 },
        { name: 'Teachers', value: stats?.total_teachers || 0 },
    ];
    const COLORS = ['#0088FE', '#00C49F'];

    return (
        <Box>
            <Typography variant="h4" sx={{ mb: 4, fontWeight: 'bold' }}>
                Dashboard Overview
            </Typography>

            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard 
                        title="Total Students" 
                        value={stats?.total_students || 0} 
                        icon={<School />} 
                        color="primary" 
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard 
                        title="Total Teachers" 
                        value={stats?.total_teachers || 0} 
                        icon={<People />} 
                        color="secondary" 
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard 
                        title="Total Classes" 
                        value={stats?.total_classes || 0} 
                        icon={<Class />} 
                        color="warning" 
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard 
                        title="Attendance (Total)" 
                        value={stats?.total_attendance_records || 0} 
                        icon={<EventNote />} 
                        color="success" 
                    />
                </Grid>
            </Grid>

            <Grid container spacing={3}>
                <Grid item xs={12} md={8}>
                    <Paper sx={{ p: 3, height: 400, display: 'flex', flexDirection: 'column' }}>
                        <Typography variant="h6" sx={{ mb: 2 }}>Attendance Trends (This Year)</Typography>
                        <Box sx={{ flexGrow: 1, width: '100%', minHeight: 0 }}>
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={stats?.chart_data || []} margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="name" interval={0} angle={-30} textAnchor="end" height={60} />
                                    <YAxis />
                                    <ChartTooltip />
                                    <Legend verticalAlign="top" height={36}/>
                                    <Bar dataKey="students" name="Total Students" fill="#8884d8" />
                                    <Bar dataKey="attendance" name="Attendance Count" fill="#82ca9d" />
                                </BarChart>
                            </ResponsiveContainer>
                        </Box>
                    </Paper>
                </Grid>
                <Grid item xs={12} md={4}>
                     <Grid container spacing={3} direction="column">
                        <Grid item xs={12}>
                            <Paper sx={{ p: 3, height: 300, display: 'flex', flexDirection: 'column' }}>
                                <Typography variant="h6" sx={{ mb: 2 }}>User Distribution</Typography>
                                <Box sx={{ flexGrow: 1, width: '100%', minHeight: 0 }}>
                                    <ResponsiveContainer width="100%" height="100%">
                                        <PieChart>
                                            <Pie
                                                data={pieData}
                                                cx="50%"
                                                cy="50%"
                                                innerRadius={45}
                                                outerRadius={60}
                                                fill="#8884d8"
                                                paddingAngle={5}
                                                dataKey="value"
                                            >
                                                {pieData.map((entry, index) => (
                                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                                ))}
                                            </Pie>
                                            <ChartTooltip />
                                            <Legend verticalAlign="bottom" height={36}/>
                                        </PieChart>
                                    </ResponsiveContainer>
                                </Box>
                            </Paper>
                        </Grid>
                        <Grid item xs={12}>
                             <Paper sx={{ p: 3, height: 125, overflow: 'auto' }}>
                                <Typography variant="h6" sx={{ mb: 1 }}>Recent Activities</Typography>
                                <List dense>
                                    {stats?.recent_activities?.length > 0 ? (
                                        stats.recent_activities.map((activity, index) => (
                                            <ListItem key={index} disablePadding>
                                                <ListItemText 
                                                    primary={activity.text} 
                                                    secondary={activity.time} 
                                                />
                                            </ListItem>
                                        ))
                                    ) : (
                                        <Typography color="text.secondary" variant="body2">No recent activities.</Typography>
                                    )}
                                </List>
                            </Paper>
                        </Grid>
                     </Grid>
                </Grid>
            </Grid>
        </Box>
    );
};

export default AdminDashboard;