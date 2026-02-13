import React, { useState, useEffect } from 'react';
import {
    Box,
    Paper,
    Typography,
    Grid,
    Card,
    CardContent,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    CircularProgress,
    Tab,
    Tabs,
    Divider,
    Chip
} from '@mui/material';
import { Person, School, AttachMoney, EventAvailable, Assignment as AssignmentIcon } from '@mui/icons-material';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';

const ParentDashboard = () => {
    const { user } = useAuth();
    const [children, setChildren] = useState([]);
    const [selectedChildId, setSelectedChildId] = useState('');
    const [childData, setChildData] = useState({
        attendance: [],
        marks: [],
        assignments: [],
        fees: []
    });
    const [loading, setLoading] = useState(true);
    const [tabValue, setTabValue] = useState(0);

    useEffect(() => {
        const fetchChildren = async () => {
            try {
                const response = await api.get('/parents/my-children/');
                setChildren(response.data);
                if (response.data.length > 0) {
                    setSelectedChildId(response.data[0].id);
                }
            } catch (error) {
                console.error("Failed to fetch children");
            } finally {
                setLoading(false);
            }
        };
        fetchChildren();
    }, []);

    useEffect(() => {
        if (!selectedChildId) return;

        const fetchChildDetails = async () => {
            setLoading(true);
            try {
                const selectedChild = children.find(c => c.id === selectedChildId);
                
                const [attendanceRes, marksRes, feesRes, assignmentsRes] = await Promise.all([
                   api.get(`/attendance/?student_id=${selectedChildId}`),
                   api.get(`/marks/student/${selectedChildId}/`),
                   api.get(`/fees/payments/student/${selectedChildId}/`),
                   selectedChild?.class_id ? api.get(`/assignments/class/${selectedChild.class_id}/`) : Promise.resolve({ data: [] })
                ]);

                setChildData({
                    attendance: attendanceRes.data,
                    marks: marksRes.data,
                    fees: feesRes.data,
                    assignments: assignmentsRes.data
                });

            } catch (error) {
                console.error("Failed to fetch child data", error);
            } finally {
                setLoading(false);
            }
        };

        fetchChildDetails();
    }, [selectedChildId, children]);

    const handleChildChange = (event) => {
        setSelectedChildId(event.target.value);
    };

    const selectedChild = children.find(c => c.id === selectedChildId);

    if (loading && children.length === 0) return <CircularProgress />;

    return (
        <Box>
             <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h4" fontWeight="bold">Parent Dashboard</Typography>
                
                {children.length > 0 && (
                    <FormControl sx={{ minWidth: 200 }}>
                        <InputLabel>Select Child</InputLabel>
                        <Select
                            value={selectedChildId}
                            label="Select Child"
                            onChange={handleChildChange}
                        >
                            {children.map((child) => (
                                <MenuItem key={child.id} value={child.id}>
                                    {child.full_name} ({child.roll_number})
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                )}
            </Box>

            {!selectedChild ? (
                <Typography>No students linked to your account.</Typography>
            ) : (
                <>
                     <Grid container spacing={3} sx={{ mb: 4 }}>
                        <Grid item xs={12} sm={4}>
                            <Card>
                                <CardContent sx={{ display: 'flex', alignItems: 'center' }}>
                                    <Person color="primary" sx={{ fontSize: 40, mr: 2 }} />
                                    <Box>
                                        <Typography color="text.secondary">Student Name</Typography>
                                        <Typography variant="h6">{selectedChild.full_name}</Typography>
                                    </Box>
                                </CardContent>
                            </Card>
                        </Grid>
                         <Grid item xs={12} sm={4}>
                            <Card>
                                <CardContent sx={{ display: 'flex', alignItems: 'center' }}>
                                    <School color="secondary" sx={{ fontSize: 40, mr: 2 }} />
                                    <Box>
                                        <Typography color="text.secondary">Class</Typography>
                                        <Typography variant="h6">{selectedChild.class_id || 'N/A'}</Typography>
                                    </Box>
                                </CardContent>
                            </Card>
                        </Grid>
                    </Grid>

                    <Paper sx={{ width: '100%' }}>
                        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} sx={{ borderBottom: 1, borderColor: 'divider' }}>
                            <Tab label="Attendance" icon={<EventAvailable />} iconPosition="start" />
                            <Tab label="Marks" icon={<School />} iconPosition="start" />
                            <Tab label="Fees" icon={<AttachMoney />} iconPosition="start" />
                            <Tab label="Assignments" icon={<AssignmentIcon />} iconPosition="start" />
                        </Tabs>
                        
                        <Box sx={{ p: 3 }}>
                            {tabValue === 0 && (
                                <Box>
                                    <Typography variant="h6" gutterBottom>Attendance History</Typography>
                                    {childData.attendance.length > 0 ? (
                                        childData.attendance.slice(0, 10).map((att) => (
                                            <Box key={att.id} sx={{ mb: 1, p: 1, border: '1px solid #eee', borderRadius: 1 }}>
                                                <Typography variant="subtitle2">{att.date}</Typography>
                                                <Typography color={att.status === 'present' ? 'success.main' : 'error.main'}>
                                                    {att.status.toUpperCase()}
                                                </Typography>
                                            </Box>
                                        ))
                                    ) : <Typography>No attendance records found.</Typography>}
                                </Box>
                            )}

                            {tabValue === 1 && (
                                <Box>
                                    <Typography variant="h6" gutterBottom>Recent Marks</Typography>
                                    {childData.marks.length > 0 ? (
                                        <Grid container spacing={2}>
                                            {childData.marks.map((mark) => (
                                                 <Grid item xs={12} sm={6} md={4} key={mark.id}>
                                                    <Card variant="outlined">
                                                        <CardContent>
                                                            <Typography variant="subtitle1" fontWeight="bold">{mark.subject}</Typography>
                                                            <Typography variant="h5" color="primary">
                                                                {mark.score} / {mark.max_score}
                                                            </Typography>
                                                        </CardContent>
                                                    </Card>
                                                 </Grid>
                                            ))}
                                        </Grid>
                                    ) : <Typography>No marks recorded.</Typography>}
                                </Box>
                            )}
                            
                            {tabValue === 2 && (
                                <Box>
                                    <Typography variant="h6" gutterBottom>Fee Status</Typography>
                                     {childData.fees.length > 0 ? (
                                        childData.fees.map((fee) => (
                                            <Box key={fee.id} sx={{ mb: 2, p: 2, border: '1px solid #eee', borderRadius: 1, display: 'flex', justifyContent: 'space-between' }}>
                                                <Box>
                                                    <Typography fontWeight="bold">Amount: ${fee.amount}</Typography>
                                                    <Typography variant="caption">Due: {fee.due_date}</Typography>
                                                </Box>
                                                <Chip 
                                                    label={fee.status} 
                                                    color={fee.status === 'paid' ? 'success' : 'warning'} 
                                                />
                                            </Box>
                                        ))
                                    ) : <Typography>No fee records found.</Typography>}
                                </Box>
                            )}

                            {tabValue === 3 && (
                                <Box>
                                    <Typography variant="h6" gutterBottom>Class Assignments</Typography>
                                    {childData.assignments.length > 0 ? (
                                        childData.assignments.map((assignment) => (
                                            <Box key={assignment.id} sx={{ mb: 2, p: 2, border: '1px solid #eee', borderRadius: 1 }}>
                                                <Typography variant="subtitle1" fontWeight="bold">{assignment.title}</Typography>
                                                <Typography variant="body2">{assignment.description}</Typography>
                                                <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                                                    Due Date: {assignment.due_date}
                                                </Typography>
                                            </Box>
                                        ))
                                    ) : <Typography>No assignments found for this class.</Typography>}
                                </Box>
                            )}
                        </Box>
                    </Paper>
                </>
            )}
        </Box>
    );
};

export default ParentDashboard;
