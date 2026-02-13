import React, { useState, useEffect } from 'react';
import {
    Box,
    Paper,
    Typography,
    TextField,
    Button,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    Grid,
    List,
    ListItem,
    ListItemText,
    Divider,
    Chip,
    IconButton
} from '@mui/material';
import { Send as SendIcon, MarkEmailRead as ReadIcon, Delete as DeleteIcon } from '@mui/icons-material';
import api from '../api/axios';
import { useSnackbar } from 'notistack';
import { useAuth } from '../context/AuthContext';

const Notifications = () => {
    const { role } = useAuth();
    const [notifications, setNotifications] = useState([]);
    const [form, setForm] = useState({
        title: '',
        message: '',
        recipient_role: 'all',
        recipient_id: ''
    });
    const { enqueueSnackbar } = useSnackbar();

    const fetchNotifications = async () => {
        try {
            const res = await api.get('/notifications/');
            setNotifications(res.data);
        } catch (error) {
            console.error("Failed to fetch notifications");
        }
    };

    useEffect(() => {
        fetchNotifications();
    }, []);

    const handleSubmit = async () => {
        try {
            const data = { ...form };
            if (!data.recipient_id) data.recipient_id = null;
            await api.post('/notifications/', data);
            enqueueSnackbar('Notification sent successfully', { variant: 'success' });
            setForm({ title: '', message: '', recipient_role: 'all', recipient_id: '' });
            fetchNotifications();
        } catch (error) {
            enqueueSnackbar('Failed to send notification', { variant: 'error' });
        }
    };

    const handleMarkRead = async (id) => {
        try {
            await api.put(`/notifications/${id}/read/`);
            fetchNotifications();
        } catch (error) {
            enqueueSnackbar('Failed to mark as read', { variant: 'error' });
        }
    };

    return (
        <Box>
            <Typography variant="h4" fontWeight="bold" sx={{ mb: 3 }}>
                Notifications
            </Typography>

            <Grid container spacing={3}>
                {/* Admin/Teacher Send Form */}
                {(role === 'admin' || role === 'teacher') && (
                    <Grid item xs={12} md={5}>
                        <Paper sx={{ p: 3 }}>
                            <Typography variant="h6" sx={{ mb: 2 }}>Create New Notification</Typography>
                            <Grid container spacing={2}>
                                <Grid item xs={12}>
                                    <TextField
                                        label="Title"
                                        fullWidth
                                        value={form.title}
                                        onChange={(e) => setForm({...form, title: e.target.value})}
                                    />
                                </Grid>
                                <Grid item xs={12}>
                                    <TextField
                                        label="Message"
                                        fullWidth
                                        multiline
                                        rows={4}
                                        value={form.message}
                                        onChange={(e) => setForm({...form, message: e.target.value})}
                                    />
                                </Grid>
                                <Grid item xs={12}>
                                    <FormControl fullWidth>
                                        <InputLabel>Recipient</InputLabel>
                                        <Select
                                            value={form.recipient_role}
                                            label="Recipient"
                                            onChange={(e) => setForm({...form, recipient_role: e.target.value})}
                                        >
                                            <MenuItem value="all">All Users</MenuItem>
                                            <MenuItem value="student">All Students</MenuItem>
                                            <MenuItem value="teacher">All Teachers</MenuItem>
                                        </Select>
                                    </FormControl>
                                </Grid>
                                <Grid item xs={12}>
                                    <Button 
                                        variant="contained" 
                                        startIcon={<SendIcon />} 
                                        fullWidth 
                                        size="large"
                                        onClick={handleSubmit}
                                        disabled={!form.title || !form.message}
                                    >
                                        Send Notification
                                    </Button>
                                </Grid>
                            </Grid>
                        </Paper>
                    </Grid>
                )}

                {/* Notifications List */}
                <Grid item xs={12} md={(role === 'admin' || role === 'teacher') ? 7 : 12}>
                    <Paper sx={{ p: 0 }}>
                        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Typography variant="h6">Recent Notifications</Typography>
                            <Button size="small" onClick={fetchNotifications}>Refresh</Button>
                        </Box>
                        <List sx={{ width: '100%', bgcolor: 'background.paper' }}>
                            {notifications.length === 0 ? (
                                <Box sx={{ p: 4, textAlign: 'center' }}>
                                    <Typography color="text.secondary">No notifications found.</Typography>
                                </Box>
                            ) : (
                                notifications.map((n, index) => (
                                    <React.Fragment key={n.id}>
                                        <ListItem 
                                            alignItems="flex-start"
                                            secondaryAction={
                                                (!n.is_read && n.recipient_id) && (
                                                    <IconButton edge="end" onClick={() => handleMarkRead(n.id)}>
                                                        <ReadIcon color="primary" />
                                                    </IconButton>
                                                )
                                            }
                                            sx={{ 
                                                bgcolor: n.is_read ? 'transparent' : 'action.hover',
                                                '&:hover': { bgcolor: 'action.selected' }
                                            }}
                                        >
                                            <ListItemText
                                                primary={
                                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                        <Typography variant="subtitle1" fontWeight={n.is_read ? 'normal' : 'bold'}>
                                                            {n.title}
                                                        </Typography>
                                                        {n.recipient_role === 'all' && <Chip label="Public" size="small" variant="outlined" />}
                                                        {(!n.is_read && n.recipient_id) && <Chip label="New" color="error" size="small" />}
                                                    </Box>
                                                }
                                                secondary={
                                                    <Box component="span">
                                                        <Typography
                                                            sx={{ display: 'inline', my: 1 }}
                                                            component="span"
                                                            variant="body2"
                                                            color="text.primary"
                                                        >
                                                            {n.message}
                                                        </Typography>
                                                        <Typography variant="caption" display="block" color="text.secondary" sx={{ mt: 1 }}>
                                                            {new Date(n.created_at).toLocaleString()}
                                                        </Typography>
                                                    </Box>
                                                }
                                            />
                                        </ListItem>
                                        {index < notifications.length - 1 && <Divider variant="inset" component="li" />}
                                    </React.Fragment>
                                ))
                            )}
                        </List>
                    </Paper>
                </Grid>
            </Grid>
        </Box>
    );
};

export default Notifications;
