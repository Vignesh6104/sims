import React, { useState } from 'react';
import {
    Box,
    Button,
    Container,
    TextField,
    Typography,
    Paper,
    Avatar,
    CircularProgress
} from '@mui/material';
import VpnKeyIcon from '@mui/icons-material/VpnKey';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import api from '../api/axios';
import { useSnackbar } from 'notistack';

const ResetPassword = () => {
    const [form, setForm] = useState({ token: '', new_password: '', confirm_password: '' });
    const [loading, setLoading] = useState(false);
    const { enqueueSnackbar } = useSnackbar();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (form.new_password !== form.confirm_password) {
            return enqueueSnackbar("Passwords do not match", { variant: 'error' });
        }
        setLoading(true);
        try {
            const res = await api.post('/auth/reset-password', {
                token: form.token,
                new_password: form.new_password
            });
            enqueueSnackbar(res.data.msg, { variant: 'success' });
            navigate('/login');
        } catch (error) {
            enqueueSnackbar(error.response?.data?.detail || "Something went wrong", { variant: 'error' });
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container component="main" maxWidth="xs">
            <Box sx={{ mt: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <Paper elevation={3} sx={{ p: 4, width: '100%', borderRadius: 2 }}>
                    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 3 }}>
                        <Avatar sx={{ m: 1, bgcolor: 'primary.main' }}>
                            <VpnKeyIcon />
                        </Avatar>
                        <Typography component="h1" variant="h5">
                            Reset Password
                        </Typography>
                    </Box>
                    <Box component="form" onSubmit={handleSubmit} noValidate>
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            id="token"
                            label="Reset Token"
                            name="token"
                            autoFocus
                            value={form.token}
                            onChange={(e) => setForm({...form, token: e.target.value})}
                        />
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            name="new_password"
                            label="New Password"
                            type="password"
                            id="new_password"
                            value={form.new_password}
                            onChange={(e) => setForm({...form, new_password: e.target.value})}
                        />
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            name="confirm_password"
                            label="Confirm New Password"
                            type="password"
                            id="confirm_password"
                            value={form.confirm_password}
                            onChange={(e) => setForm({...form, confirm_password: e.target.value})}
                        />
                        <Button
                            type="submit"
                            fullWidth
                            variant="contained"
                            sx={{ mt: 3, mb: 2 }}
                            disabled={loading}
                        >
                            {loading ? <CircularProgress size={24} color="inherit" /> : 'Reset Password'}
                        </Button>

                    </Box>
                </Paper>
            </Box>
        </Container>
    );
};

export default ResetPassword;
