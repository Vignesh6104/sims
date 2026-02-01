import React, { useEffect, useState } from 'react';
import { 
    Grid, 
    Paper, 
    Typography, 
    Box, 
    CircularProgress, 
    Table, 
    TableBody, 
    TableCell, 
    TableContainer, 
    TableHead, 
    TableRow,
    Card,
    CardContent,
    Avatar,
    Button,
    Chip,
    List,
    ListItem,
    ListItemText,
    ListItemAvatar,
    Divider,
    Tooltip
} from '@mui/material';
import { 
    Class, 
    People, 
    EventAvailable, 
    EventBusy, 
    AssignmentLate, 
    CalendarToday,
    History,
    TrendingUp,
    Warning
} from '@mui/icons-material';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({ error, errorInfo });
    console.error("Dashboard Error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <Box sx={{ p: 3 }}>
          <Typography variant="h5" color="error">Something went wrong in the Dashboard.</Typography>
          <pre style={{ color: 'red' }}>{this.state.error && this.state.error.toString()}</pre>
        </Box>
      );
    }

    return this.props.children; 
  }
}

const StatCard = ({ title, value, icon, color, subtext }) => (
    <Card sx={{ height: '100%', position: 'relative', overflow: 'hidden' }}>
        <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <Box>
                    <Typography color="text.secondary" gutterBottom variant="caption" textTransform="uppercase">
                        {title}
                    </Typography>
                    <Typography variant="h4" fontWeight="bold" sx={{ color: `${color}.main` }}>
                        {value}
                    </Typography>
                    {subtext && <Typography variant="body2" color="text.secondary">{subtext}</Typography>}
                </Box>
                <Avatar sx={{ bgcolor: `${color}.light`, color: `${color}.main`, width: 48, height: 48 }}>
                    {icon}
                </Avatar>
            </Box>
        </CardContent>
    </Card>
);

const TeacherDashboardContent = () => {
    const { user } = useAuth();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState(null);

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                const response = await api.get('/dashboard/teacher/stats');
                setData(response.data);
            } catch (error) {
                console.error("Failed to fetch dashboard data", error);
            } finally {
                setLoading(false);
            }
        };

        if (user?.sub) {
            fetchDashboardData(); 
            const intervalId = setInterval(fetchDashboardData, 30000); 
            return () => clearInterval(intervalId); 
        }
    }, [user]);

    if (loading) return (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
            <CircularProgress />
        </Box>
    );

    if (!data) return (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
            <Typography color="error">Failed to load dashboard data. Please try again later.</Typography>
        </Box>
    );

    return (
        <Box>
            <Box sx={{ mb: 4 }}>
                <Typography variant="h4" fontWeight="bold">
                    Welcome, {user?.full_name || 'Teacher'}
                </Typography>
                <Typography variant="subtitle1" color="text.secondary">
                    Here's what's happening in your classes today.
                </Typography>
            </Box>

            {/* 1. Today's Overview */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard 
                        title="Today's Date" 
                        value={data?.date} 
                        icon={<CalendarToday />} 
                        color="info" 
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard 
                        title="Present Today" 
                        value={data?.overview?.present} 
                        icon={<EventAvailable />} 
                        color="success" 
                        subtext="Students in class"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard 
                        title="Absent Today" 
                        value={data?.overview?.absent} 
                        icon={<EventBusy />} 
                        color="error" 
                        subtext="Students missing"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard 
                        title="Pending Marks" 
                        value={data?.overview?.pending_marks} 
                        icon={<AssignmentLate />} 
                        color="warning" 
                        subtext="Classes pending entry"
                    />
                </Grid>
            </Grid>

            {/* 2. Middle Section: Classes & Marks Status */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                {/* Left: My Classes */}
                <Grid item xs={12} md={7}>
                    <Paper sx={{ p: 3, height: '100%' }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                            <Typography variant="h6" fontWeight="bold">My Classes</Typography>
                        </Box>
                        <TableContainer>
                            <Table size="small">
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Class Name</TableCell>
                                        <TableCell align="right">Quick Actions</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {data?.classes?.map((cls) => (
                                        <TableRow key={cls.id}>
                                            <TableCell sx={{ fontWeight: 'medium' }}>{cls.name}</TableCell>
                                            <TableCell align="right">
                                                <Button 
                                                    size="small" 
                                                    variant="outlined" 
                                                    color="primary"
                                                    sx={{ mr: 1 }}
                                                    onClick={() => navigate('/teacher/attendance')}
                                                >
                                                    Attendance
                                                </Button>
                                                <Button 
                                                    size="small" 
                                                    variant="text" 
                                                    onClick={() => navigate('/teacher/attendance')}
                                                >
                                                    Report
                                                </Button>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                    {(!data?.classes || data.classes.length === 0) && (
                                        <TableRow><TableCell colSpan={2} align="center">No classes assigned.</TableCell></TableRow>
                                    )}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </Paper>
                </Grid>

                {/* Right: Marks Status */}
                <Grid item xs={12} md={5}>
                    <Paper sx={{ p: 3, height: '100%' }}>
                        <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>Marks Entry Status</Typography>
                        <List dense>
                            {data?.marks_status?.map((status, index) => (
                                <React.Fragment key={index}>
                                    <ListItem>
                                        <ListItemAvatar>
                                            <Avatar sx={{ bgcolor: status.status === 'Completed' ? 'success.light' : 'warning.light' }}>
                                                {status.status === 'Completed' ? <EventAvailable /> : <AssignmentLate />}
                                            </Avatar>
                                        </ListItemAvatar>
                                        <ListItemText 
                                            primary={status.exam_name}
                                            secondary={`${status.class_name} • ${status.progress} Entered`}
                                        />
                                        <Chip 
                                            label={status.status} 
                                            color={status.status === 'Completed' ? 'success' : 'warning'} 
                                            size="small" 
                                        />
                                    </ListItem>
                                    {index < data.marks_status.length - 1 && <Divider variant="inset" component="li" />}
                                </React.Fragment>
                            ))}
                            {(!data?.marks_status || data.marks_status.length === 0) && (
                                <Typography variant="body2" color="text.secondary" align="center">No active exams.</Typography>
                            )}
                        </List>
                        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
                            <Button size="small" onClick={() => navigate('/teacher/marks')}>
                                Go to Marks Manager
                            </Button>
                        </Box>
                    </Paper>
                </Grid>
            </Grid>

            {/* 3. Bottom Section: Recent Activity & Students List */}
            <Grid container spacing={3}>
                {/* Left: Recent Activity */}
                <Grid item xs={12} md={4}>
                    <Paper sx={{ p: 3, height: '100%' }}>
                        <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>Recent Activity</Typography>
                        <List>
                            {data?.recent_activity?.map((activity, index) => (
                                <ListItem key={index}>
                                    <ListItemAvatar>
                                        <Avatar sx={{ bgcolor: 'primary.light' }}>
                                            <History />
                                        </Avatar>
                                    </ListItemAvatar>
                                    <ListItemText 
                                        primary={activity.title}
                                        secondary={
                                            <React.Fragment>
                                                <Typography component="span" variant="body2" color="text.primary">
                                                    {activity.desc}
                                                </Typography>
                                                <br />
                                                {activity.time}
                                            </React.Fragment>
                                        }
                                    />
                                </ListItem>
                            ))}
                            {(!data?.recent_activity || data.recent_activity.length === 0) && (
                                <Typography variant="body2" color="text.secondary" align="center">No recent activity.</Typography>
                            )}
                        </List>
                    </Paper>
                </Grid>

                {/* Right: All Students List (Enhanced) */}
                <Grid item xs={12} md={8}>
                    <Paper sx={{ p: 3, height: '100%' }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2, alignItems: 'center' }}>
                            <Typography variant="h6" fontWeight="bold">Student Performance</Typography>
                            <Box>
                                <Button size="small" variant="outlined" sx={{ mr: 1 }}>Export CSV</Button>
                                <Button size="small" variant="outlined">Export PDF</Button>
                            </Box>
                        </Box>
                        <TableContainer sx={{ maxHeight: 400 }}>
                            <Table stickyHeader size="small">
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Roll No</TableCell>
                                        <TableCell>Name</TableCell>
                                        <TableCell>Class</TableCell>
                                        <TableCell align="center">Attendance</TableCell>
                                        <TableCell align="center">Avg Marks</TableCell>
                                        <TableCell align="center">Status</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {data?.students?.map((student) => (
                                        <TableRow key={student.id}>
                                            <TableCell>{student.roll_number}</TableCell>
                                            <TableCell>{student.full_name}</TableCell>
                                            <TableCell>{student.class_name}</TableCell>
                                            <TableCell align="center">
                                                <Chip 
                                                    label={`${student.attendance_pct}%`} 
                                                    color={student.attendance_pct < 75 ? 'error' : 'success'} 
                                                    size="small" 
                                                    variant="outlined"
                                                />
                                            </TableCell>
                                            <TableCell align="center">
                                                {student.avg_marks > 0 ? student.avg_marks : '-'}
                                            </TableCell>
                                            <TableCell align="center">
                                                {student.attendance_pct < 75 ? (
                                                    <Tooltip title="Low Attendance">
                                                        <Warning color="error" fontSize="small" />
                                                    </Tooltip>
                                                ) : (
                                                    <TrendingUp color="success" fontSize="small" />
                                                )}
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </Paper>
                </Grid>
            </Grid>
        </Box>
    );
};

const TeacherDashboard = () => (
    <ErrorBoundary>
        <TeacherDashboardContent />
    </ErrorBoundary>
);

export default TeacherDashboard;
