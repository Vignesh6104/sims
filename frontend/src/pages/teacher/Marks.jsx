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

const Marks = () => {
    const { user } = useAuth();
    const [tabValue, setTabValue] = useState(0);
    
    // Data State
    const [classes, setClasses] = useState([]);
    const [exams, setExams] = useState([]);
    const [subjects, setSubjects] = useState([]);
    const [assignments, setAssignments] = useState([]);
    
    // Selection State
    const [selectedClass, setSelectedIdClass] = useState('');
    const [selectedExam, setSelectedExam] = useState('');
    const [selectedSubject, setSelectedSubject] = useState('');
    
    // Entry State
    const [students, setStudents] = useState([]);
    const [marksData, setMarksData] = useState({});
    
    // Report State
    const [reportData, setReportData] = useState([]);
    const [assignmentSubmissions, setAssignmentSubmissions] = useState([]);
    
    const [loading, setLoading] = useState(false);
    const { enqueueSnackbar } = useSnackbar();

    useEffect(() => {
        const fetchInitialData = async () => {
            try {
                const [classesRes, examsRes, subjectsRes] = await Promise.all([
                    api.get(`/class_rooms?teacher_id=${user.sub}`),
                    api.get('/exams'),
                    api.get('/subjects')
                ]);
                setClasses(classesRes.data);
                setExams(examsRes.data);
                setSubjects(subjectsRes.data);
            } catch (error) {
                console.error("Failed to fetch initial data", error);
            }
        };
        if (user?.sub) fetchInitialData();
    }, [user]);

    // Handle Entry Logic
    useEffect(() => {
        if (tabValue === 0 && selectedClass && selectedExam && selectedSubject) {
            fetchStudentsAndMarks();
        }
    }, [selectedClass, selectedExam, selectedSubject, tabValue]);

    // Handle Report Logic
    useEffect(() => {
        if (tabValue === 1 && selectedClass) {
            fetchReport(selectedClass);
        }
    }, [selectedClass, tabValue]);

    // Handle Assignment Grades Logic
    useEffect(() => {
        if (tabValue === 2 && selectedClass) {
            fetchAssignmentGrades(selectedClass);
        }
    }, [selectedClass, tabValue]);

    const fetchAssignmentGrades = async (classId) => {
        setLoading(true);
        try {
            const [assignRes, studentsRes] = await Promise.all([
                api.get(`/assignments/class/${classId}`),
                api.get(`/students?class_id=${classId}`)
            ]);
            
            const assignmentsList = assignRes.data;
            const studentsList = studentsRes.data;
            setAssignments(assignmentsList);
            setStudents(studentsList);

            // Fetch all submissions for these assignments
            const submissionsPromises = assignmentsList.map(a => 
                api.get(`/assignments/submissions/${a.id}`)
            );
            const submissionsResponses = await Promise.all(submissionsPromises);
            const allSubmissions = submissionsResponses.flatMap(r => r.data);
            setAssignmentSubmissions(allSubmissions);

        } catch (error) {
            enqueueSnackbar('Failed to fetch assignment grades', { variant: 'error' });
        } finally {
            setLoading(false);
        }
    };

    const fetchStudentsAndMarks = async () => {
        setLoading(true);
        try {
            const studentsRes = await api.get(`/students?class_id=${selectedClass}`);
            const studentsList = studentsRes.data;
            setStudents(studentsList);

            if (studentsList.length > 0) {
                const studentIds = studentsList.map(s => s.id);
                const subjObj = subjects.find(s => s.id === selectedSubject);
                const subjName = subjObj ? subjObj.name : '';
                
                const params = new URLSearchParams();
                params.append('exam_id', selectedExam);
                params.append('subject', subjName);
                studentIds.forEach(id => params.append('student_ids', id));

                const marksRes = await api.get(`/marks/batch?${params.toString()}`);
                
                const newMarksData = {};
                studentsList.forEach(s => {
                    newMarksData[s.id] = { score: '', max_score: 100, id: null };
                });

                marksRes.data.forEach(mark => {
                    newMarksData[mark.student_id] = {
                        score: mark.score,
                        max_score: mark.max_score,
                        id: mark.id
                    };
                });
                
                setMarksData(newMarksData);
            }
        } catch (error) {
            enqueueSnackbar('Failed to fetch marks', { variant: 'error' });
        } finally {
            setLoading(false);
        }
    };

    const fetchReport = async (classId) => {
        setLoading(true);
        try {
            const response = await api.get(`/marks/report?class_id=${classId}`);
            setReportData(response.data);
        } catch (error) {
            enqueueSnackbar('Failed to fetch report', { variant: 'error' });
        } finally {
            setLoading(false);
        }
    };

    const handleScoreChange = (studentId, field, value) => {
        setMarksData(prev => ({
            ...prev,
            [studentId]: {
                ...prev[studentId],
                [field]: value
            }
        }));
    };

    const handleSubmit = async () => {
        setLoading(true);
        try {
            const subjObj = subjects.find(s => s.id === selectedSubject);
            const subjName = subjObj ? subjObj.name : '';

            const promises = students.map(student => {
                const data = marksData[student.id];
                if (data.score === '') return null;

                const payload = {
                    student_id: student.id,
                    subject: subjName,
                    score: parseFloat(data.score),
                    max_score: parseFloat(data.max_score),
                    exam_id: selectedExam
                };

                if (data.id) {
                    return api.put(`/marks/${data.id}`, payload);
                } else {
                    return api.post('/marks', payload);
                }
            }).filter(p => p !== null);
            
            await Promise.all(promises);
            enqueueSnackbar('Marks saved successfully!', { variant: 'success' });
            fetchStudentsAndMarks();
        } catch (error) {
            enqueueSnackbar('Failed to save marks', { variant: 'error' });
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
                Marks Management
            </Typography>

            <Paper sx={{ mb: 3 }}>
                <Tabs value={tabValue} onChange={handleTabChange} indicatorColor="primary" textColor="primary" centered>
                    <Tab label="Enter Marks (Exams)" />
                    <Tab label="Exam Report" />
                    <Tab label="Assignment Grades" />
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
                        <>
                            <Grid item xs={12} md={4}>
                                <FormControl fullWidth>
                                    <InputLabel>Select Exam</InputLabel>
                                    <Select
                                        value={selectedExam}
                                        label="Select Exam"
                                        onChange={(e) => setSelectedExam(e.target.value)}
                                    >
                                        {exams.map((exam) => (
                                            <MenuItem key={exam.id} value={exam.id}>
                                                {exam.name}
                                            </MenuItem>
                                        ))}
                                    </Select>
                                </FormControl>
                            </Grid>
                            <Grid item xs={12} md={4}>
                                <FormControl fullWidth>
                                    <InputLabel>Select Subject</InputLabel>
                                    <Select
                                        value={selectedSubject}
                                        label="Select Subject"
                                        onChange={(e) => setSelectedSubject(e.target.value)}
                                    >
                                        {subjects.map((subj) => (
                                            <MenuItem key={subj.id} value={subj.id}>
                                                {subj.name} ({subj.code})
                                            </MenuItem>
                                        ))}
                                    </Select>
                                </FormControl>
                            </Grid>
                        </>
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
                                // ENTER MARKS VIEW
                                <>
                                    {selectedExam && selectedSubject ? (
                                        <>
                                            <TableContainer>
                                                <Table>
                                                    <TableHead>
                                                        <TableRow>
                                                            <TableCell>Roll No</TableCell>
                                                            <TableCell>Student Name</TableCell>
                                                            <TableCell align="center">Score</TableCell>
                                                            <TableCell align="center">Max Score</TableCell>
                                                        </TableRow>
                                                    </TableHead>
                                                    <TableBody>
                                                        {students.map((student) => (
                                                            <TableRow key={student.id}>
                                                                <TableCell>{student.roll_number}</TableCell>
                                                                <TableCell>{student.full_name}</TableCell>
                                                                <TableCell align="center">
                                                                    <TextField 
                                                                        type="number" 
                                                                        size="small"
                                                                        value={marksData[student.id]?.score || ''}
                                                                        onChange={(e) => handleScoreChange(student.id, 'score', e.target.value)}
                                                                        sx={{ width: 100 }}
                                                                    />
                                                                </TableCell>
                                                                <TableCell align="center">
                                                                    <TextField 
                                                                        type="number" 
                                                                        size="small"
                                                                        value={marksData[student.id]?.max_score || 100}
                                                                        onChange={(e) => handleScoreChange(student.id, 'max_score', e.target.value)}
                                                                        sx={{ width: 100 }}
                                                                    />
                                                                </TableCell>
                                                            </TableRow>
                                                        ))}
                                                    </TableBody>
                                                </Table>
                                            </TableContainer>
                                            <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
                                                <Button variant="contained" size="large" onClick={handleSubmit}>
                                                    Save Marks
                                                </Button>
                                            </Box>
                                        </>
                                    ) : (
                                        <Typography align="center" color="text.secondary">
                                            Please select an Exam and Subject to enter marks.
                                        </Typography>
                                    )}
                                </>
                            ) : tabValue === 1 ? (
                                // VIEW REPORT VIEW
                                <TableContainer>
                                    <Table>
                                        <TableHead>
                                            <TableRow>
                                                <TableCell>Roll No</TableCell>
                                                <TableCell>Student Name</TableCell>
                                                <TableCell>Exam</TableCell>
                                                <TableCell>Subject</TableCell>
                                                <TableCell align="center">Score</TableCell>
                                                <TableCell align="center">Percentage</TableCell>
                                            </TableRow>
                                        </TableHead>
                                        <TableBody>
                                            {reportData.map((row, index) => (
                                                <TableRow key={index} hover>
                                                    <TableCell>{row.roll_number}</TableCell>
                                                    <TableCell>{row.student_name}</TableCell>
                                                    <TableCell>{row.exam_name}</TableCell>
                                                    <TableCell>{row.subject}</TableCell>
                                                    <TableCell align="center">
                                                        {row.score} / {row.max_score}
                                                    </TableCell>
                                                    <TableCell align="center" sx={{ fontWeight: 'bold' }}>
                                                        {row.percentage}%
                                                    </TableCell>
                                                </TableRow>
                                            ))}
                                            {reportData.length === 0 && (
                                                <TableRow>
                                                    <TableCell colSpan={6} align="center">No marks recorded for this class.</TableCell>
                                                </TableRow>
                                            )}
                                        </TableBody>
                                    </Table>
                                </TableContainer>
                            ) : (
                                // ASSIGNMENT GRADES VIEW
                                <TableContainer>
                                    <Table>
                                        <TableHead>
                                            <TableRow>
                                                <TableCell>Student Name</TableCell>
                                                {assignments.map(a => (
                                                    <TableCell key={a.id} align="center" sx={{ minWidth: 120 }}>
                                                        {a.title}
                                                    </TableCell>
                                                ))}
                                            </TableRow>
                                        </TableHead>
                                        <TableBody>
                                            {students.map(student => (
                                                <TableRow key={student.id} hover>
                                                    <TableCell>{student.full_name}</TableCell>
                                                    {assignments.map(a => {
                                                        const sub = assignmentSubmissions.find(s => s.assignment_id === a.id && s.student_id === student.id);
                                                        return (
                                                            <TableCell key={a.id} align="center">
                                                                {sub ? (
                                                                    <Box>
                                                                        <Typography variant="body2" fontWeight="bold" color="primary">
                                                                            {sub.grade !== null ? sub.grade : 'Ungraded'}
                                                                        </Typography>
                                                                        {sub.feedback && (
                                                                            <Typography variant="caption" display="block" color="text.secondary">
                                                                                {sub.feedback}
                                                                            </Typography>
                                                                        )}
                                                                    </Box>
                                                                ) : (
                                                                    <Typography variant="caption" color="text.disabled">No Submission</Typography>
                                                                )}
                                                            </TableCell>
                                                        );
                                                    })}
                                                </TableRow>
                                            ))}
                                            {students.length === 0 && (
                                                <TableRow>
                                                    <TableCell colSpan={assignments.length + 1} align="center">No students found.</TableCell>
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

export default Marks;