import React, { createContext, useState, useEffect, useContext } from 'react';
import { jwtDecode } from 'jwt-decode';
import api from '../api/axios';
import { useNavigate } from 'react-router-dom';
import { useSnackbar } from 'notistack';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [role, setRole] = useState(null); // 'admin', 'teacher', 'student'
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();
    const { enqueueSnackbar } = useSnackbar();

    useEffect(() => {
        if (token) {
            try {
                const decoded = jwtDecode(token);
                // Check expiry
                if (decoded.exp * 1000 < Date.now()) {
                    // We don't logout immediately, let axios interceptor try to refresh
                    // But for initial load, if it's expired and refresh fails, then logout
                    setUser(decoded);
                    setRole(decoded.role);
                } else {
                    setUser(decoded);
                    setRole(decoded.role);
                }
            } catch (error) {
                logout();
            }
        }
        setLoading(false);
    }, [token]);

    const login = async (email, password) => {
        try {
            // Note: Our backend endpoint is /auth/login
            const response = await api.post('/auth/login', new URLSearchParams({
                username: email,
                password: password,
            }), {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            });

            const { access_token, refresh_token } = response.data;
            localStorage.setItem('token', access_token);
            localStorage.setItem('refresh_token', refresh_token);
            setToken(access_token);
            
            const decoded = jwtDecode(access_token);
            setUser(decoded);
            setRole(decoded.role);
            
            enqueueSnackbar('Login successful!', { variant: 'success' });
            
            // Navigate based on role
            if (decoded.role === 'admin') navigate('/admin');
            else if (decoded.role === 'teacher') navigate('/teacher');
            else if (decoded.role === 'student') navigate('/student');
            
            return true;
        } catch (error) {
            console.error(error);
            enqueueSnackbar(error.response?.data?.detail || 'Login failed', { variant: 'error' });
            return false;
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('refresh_token');
        setToken(null);
        setUser(null);
        setRole(null);
        navigate('/login');
    };

    return (
        <AuthContext.Provider value={{ user, role, token, login, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
