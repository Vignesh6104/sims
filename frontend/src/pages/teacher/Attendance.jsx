import React, { useState, useEffect } from 'react';
import {
    Box,
    Paper,
    Typography,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    TextField,
    Button,
    Grid,
    Radio,
    RadioGroup,
    FormControlLabel,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    CircularProgress,
    Tabs,
    Tab
} from '@mui/material';
import api from '../../api/axios';
import { useAuth } from '../../context/AuthContext';
import { useSnackbar } from 'notistack';

const Attendance = () => {
    const { user } = useAuth();
    const [tabValue, setTabValue] = useState(0);
    const [classes, setClasses] = useState([]);
    const [selectedClass, setSelectedIdClass] = useState('');
    
    // Mark Attendance State
    const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
    const [students, setStudents] = useState([]);
    const [attendanceData, setAttendanceData] = useState({});
    
    // Report State
    const [reportData, setReportData] = useState([]);

    const [loading, setLoading] = useState(false);
    const { enqueueSnackbar } = useSnackbar();

    useEffect(() => {
        const fetchClasses = async () => {
            try {
                const response = await api.get(`/class_rooms/?teacher_id=${user.sub}`);
                setClasses(response.data);
            } catch (error) {
                console.error("Failed to fetch classes", error);
            }
        };
        if (user?.sub) fetchClasses();
    }, [user]);

    // Fetch students/report when class or tab changes
    useEffect(() => {
        if (selectedClass) {
            if (tabValue === 0) {
                fetchStudents(selectedClass);
            } else {
                fetchReport(selectedClass);
            }
        }
    }, [selectedClass, tabValue]);

    const fetchStudents = async (classId) => {
        setLoading(true);
        try {
            const response = await api.get(`/students/?class_id=${classId}`);
            setStudents(response.data);
            const initialData = {};
            response.data.forEach(student => {
                initialData[student.id] = 'present';
            });
            setAttendanceData(initialData);
        } catch (error) {
            enqueueSnackbar('Failed to fetch students', { variant: 'error' });
        } finally {
            setLoading(false);
        }
    };

    const fetchReport = async (classId) => {
        setLoading(true);
        try {
            const response = await api.get(`/attendance/report/?class_id=${classId}`);
            setReportData(response.data);
        } catch (error) {
            enqueueSnackbar('Failed to fetch report', { variant: 'error' });
        } finally {
            setLoading(false);
        }
    };

    const handleAttendanceChange = (studentId, status) => {
        setAttendanceData(prev => ({
            ...prev,
            [studentId]: status
        }));
    };

    const handleSubmit = async () => {
        setLoading(true);
        try {
            const promises = students.map(student => {
                return api.post('/attendance/', {
                    student_id: student.id,
                    date: selectedDate,
                    status: attendanceData[student.id]
                });
            });
            
            await Promise.all(promises);
            enqueueSnackbar('Attendance marked successfully!', { variant: 'success' });
        } catch (error) {
            enqueueSnackbar('Failed to save attendance', { variant: 'error' });
        } finally {
            setLoading(false);
        }
    };

    const handleTabChange = (event, newValue) => {
        setTabValue(newValue);
    };

    return (
        <Box>
            <Typography variant="h4" fontWeight="bold" sx={{ mb: 3 }}>
                Attendance Tracker
            </Typography>

            <Paper sx={{ mb: 3 }}>
                <Tabs value={tabValue} onChange={handleTabChange} indicatorColor="primary" textColor="primary" centered>
                    <Tab label="Mark Attendance" />
                    <Tab label="View Report" />
                </Tabs>
            </Paper>

            <Paper sx={{ p: 3, mb: 3 }}>
                <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} md={4}>
                        <FormControl fullWidth>
                            <InputLabel>Select Class</InputLabel>
                            <Select
                                value={selectedClass}
                                label="Select Class"
                                onChange={(e) => setSelectedIdClass(e.target.value)}
                            >
                                {classes.map((cls) => (
                                    <MenuItem key={cls.id} value={cls.id}>
                                        {cls.name}
                                    </MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                    </Grid>
                    {tabValue === 0 && (
                        <Grid item xs={12} md={4}>
                            <TextField
                                type="date"
                                label="Date"
                                fullWidth
                                value={selectedDate}
                                onChange={(e) => setSelectedDate(e.target.value)}
                                InputLabelProps={{ shrink: true }}
                            />
                        </Grid>
                    )}
                </Grid>
            </Paper>

            {selectedClass && (
                <Paper sx={{ p: 3 }}>
                    {loading ? (
                        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                            <CircularProgress />
                        </Box>
                    ) : (
                        <>
                            {tabValue === 0 ? (
                                // MARK ATTENDANCE VIEW
                                <>
                                    <TableContainer>
                                        <Table>
                                            <TableHead>
                                                <TableRow>
                                                    <TableCell>Roll No</TableCell>
                                                    <TableCell>Student Name</TableCell>
                                                    <TableCell align="center">Status</TableCell>
                                                </TableRow>
                                            </TableHead>
                                            <TableBody>
                                                {students.map((student) => (
                                                    <TableRow key={student.id}>
                                                        <TableCell>{student.roll_number}</TableCell>
                                                        <TableCell>{student.full_name}</TableCell>
                                                        <TableCell align="center">
                                                            <RadioGroup
                                                                row
                                                                value={attendanceData[student.id] || 'present'}
                                                                onChange={(e) => handleAttendanceChange(student.id, e.target.value)}
                                                                sx={{ justifyContent: 'center' }}
                                                            >
                                                                <FormControlLabel value="present" control={<Radio color="success" />} label="Present" />
                                                                <FormControlLabel value="absent" control={<Radio color="error" />} label="Absent" />
                                                                <FormControlLabel value="late" control={<Radio color="warning" />} label="Late" />
                                                            </RadioGroup>
                                                        </TableCell>
                                                    </TableRow>
                                                ))}
                                            </TableBody>
                                        </Table>
                                    </TableContainer>
                                    <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
                                        <Button variant="contained" size="large" onClick={handleSubmit}>
                                            Save Attendance
                                        </Button>
                                    </Box>
                                </>
                            ) : (
                                // VIEW REPORT VIEW
                                <TableContainer>
                                    <Table>
                                        <TableHead>
                                            <TableRow>
                                                <TableCell>Roll No</TableCell>
                                                <TableCell>Student Name</TableCell>
                                                <TableCell align="center">Total Days</TableCell>
                                                <TableCell align="center">Present</TableCell>
                                                <TableCell align="center">Absent</TableCell>
                                                <TableCell align="center">Late</TableCell>
                                                <TableCell align="center">Percentage</TableCell>
                                            </TableRow>
                                        </TableHead>
                                        <TableBody>
                                            {reportData.map((row) => {
                                                const percentage = row.total_days > 0 
                                                    ? Math.round(((row.present + (row.late * 0.5)) / row.total_days) * 100) 
                                                    : 0;
                                                return (
                                                    <TableRow key={row.student_id}>
                                                        <TableCell>{row.roll_number}</TableCell>
                                                        <TableCell>{row.student_name}</TableCell>
                                                        <TableCell align="center">{row.total_days}</TableCell>
                                                        <TableCell align="center" sx={{ color: 'success.main' }}>{row.present}</TableCell>
                                                        <TableCell align="center" sx={{ color: 'error.main' }}>{row.absent}</TableCell>
                                                        <TableCell align="center" sx={{ color: 'warning.main' }}>{row.late}</TableCell>
                                                        <TableCell align="center" sx={{ fontWeight: 'bold' }}>{percentage}%</TableCell>
                                                    </TableRow>
                                                );
                                            })}
                                            {reportData.length === 0 && (
                                                <TableRow>
                                                    <TableCell colSpan={7} align="center">No attendance data found for this class.</TableCell>
                                                </TableRow>
                                            )}
                                        </TableBody>
                                    </Table>
                                </TableContainer>
                            )}
                        </>
                    )}
                </Paper>
            )}
        </Box>
    );
};

export default Attendance;