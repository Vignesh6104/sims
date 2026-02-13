import React, { useState, useEffect } from 'react';
import { Calendar as BigCalendar, dateFnsLocalizer } from 'react-big-calendar';
import format from 'date-fns/format';
import parse from 'date-fns/parse';
import startOfWeek from 'date-fns/startOfWeek';
import getDay from 'date-fns/getDay';
import enUS from 'date-fns/locale/en-US';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import { Box, Paper, Typography, CircularProgress, Button, Dialog, DialogTitle, DialogContent, TextField, DialogActions, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { useSnackbar } from 'notistack';

const locales = {
  'en-US': enUS,
};

const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek,
  getDay,
  locales,
});

const Calendar = () => {
    const { user } = useAuth();
    const { enqueueSnackbar } = useSnackbar();
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [open, setOpen] = useState(false);
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        start_date: '',
        end_date: '',
        type: 'event'
    });

    const fetchEvents = async () => {
        try {
            const response = await api.get('/events/');
            const mappedEvents = response.data.map(e => ({
                id: e.id,
                title: e.title,
                start: new Date(e.start_date),
                end: new Date(e.end_date),
                desc: e.description,
                type: e.type
            }));
            setEvents(mappedEvents);
        } catch (error) {
            console.error("Failed to fetch events");
            enqueueSnackbar("Failed to fetch events", { variant: 'error' });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchEvents();
    }, []);

    const handleOpen = () => {
        setFormData({
            title: '',
            description: '',
            start_date: '',
            end_date: '',
            type: 'event'
        });
        setOpen(true);
    };

    const handleClose = () => setOpen(false);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async () => {
        try {
            if (!formData.title || !formData.start_date || !formData.end_date) {
                enqueueSnackbar("Please fill required fields", { variant: 'warning' });
                return;
            }

            await api.post('/events/', formData);
            enqueueSnackbar("Event added successfully", { variant: 'success' });
            fetchEvents();
            handleClose();
        } catch (error) {
            enqueueSnackbar(error.response?.data?.detail || "Failed to add event", { variant: 'error' });
        }
    };

    const eventStyleGetter = (event) => {
        let backgroundColor = '#3174ad';
        if (event.type === 'holiday') backgroundColor = '#e57373';
        if (event.type === 'exam') backgroundColor = '#ffb74d';
        return {
            style: {
                backgroundColor
            }
        };
    };

    // Assume admin role is 'admin' or 'superuser'
    const isAdmin = user?.role === 'admin' || user?.is_superuser === true;

    if (loading) return <CircularProgress />;

    return (
        <Box sx={{ height: '80vh' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h4" fontWeight="bold">Academic Calendar</Typography>
                {isAdmin && (
                    <Button variant="contained" startIcon={<AddIcon />} onClick={handleOpen}>
                        Add Event
                    </Button>
                )}
            </Box>
            <Paper sx={{ height: '100%', p: 2 }}>
                <BigCalendar
                    localizer={localizer}
                    events={events}
                    startAccessor="start"
                    endAccessor="end"
                    style={{ height: '100%' }}
                    eventPropGetter={eventStyleGetter}
                    onSelectEvent={(event) => alert(`${event.title}\n${event.desc || ''}`)}
                />
            </Paper>

            <Dialog open={open} onClose={handleClose}>
                <DialogTitle>Add New Event</DialogTitle>
                <DialogContent>
                    <TextField
                        autoFocus
                        margin="dense"
                        name="title"
                        label="Event Title"
                        fullWidth
                        value={formData.title}
                        onChange={handleChange}
                    />
                    <TextField
                        margin="dense"
                        name="description"
                        label="Description"
                        fullWidth
                        multiline
                        rows={2}
                        value={formData.description}
                        onChange={handleChange}
                    />
                    <TextField
                        margin="dense"
                        name="start_date"
                        label="Start Date & Time"
                        type="datetime-local"
                        fullWidth
                        InputLabelProps={{ shrink: true }}
                        value={formData.start_date}
                        onChange={handleChange}
                    />
                    <TextField
                        margin="dense"
                        name="end_date"
                        label="End Date & Time"
                        type="datetime-local"
                        fullWidth
                        InputLabelProps={{ shrink: true }}
                        value={formData.end_date}
                        onChange={handleChange}
                    />
                    <FormControl fullWidth margin="dense">
                        <InputLabel>Type</InputLabel>
                        <Select
                            name="type"
                            value={formData.type}
                            label="Type"
                            onChange={handleChange}
                        >
                            <MenuItem value="event">Event</MenuItem>
                            <MenuItem value="holiday">Holiday</MenuItem>
                            <MenuItem value="exam">Exam</MenuItem>
                        </Select>
                    </FormControl>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleClose}>Cancel</Button>
                    <Button onClick={handleSubmit} variant="contained">Add</Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default Calendar;
