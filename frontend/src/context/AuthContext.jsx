import React, { createContext, useState, useEffect, useContext } from 'react';
import { jwtDecode } from 'jwt-decode';
import api from '../api/axios';
import { useNavigate } from 'react-router-dom';
import { toast } from '@/components/ui/use-toast';

import { startRegistration, startAuthentication } from '@simplewebauthn/browser';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [role, setRole] = useState(null); // 'admin', 'teacher', 'student'
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [loading, setLoading] = useState(true);
    const [profileLoading, setProfileLoading] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        if (token) {
            try {
                const decoded = jwtDecode(token);
                setUser(decoded);
                setRole(decoded.role);
                // Fetch full profile only once or when needed
                if (!profileLoading) {
                    refreshProfile();
                }
            } catch (error) {
                logout();
            }
        }
        setLoading(false);
    }, [token]);

    const refreshProfile = async () => {
        if (profileLoading) return;
        setProfileLoading(true);
        try {
            const res = await api.get('/auth/me');
            setUser(prev => ({ ...prev, ...res.data }));
        } catch (error) {
            console.error("Failed to refresh profile", error);
        } finally {
            setProfileLoading(false);
        }
    };

    const login = async (email, password) => {
        try {
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

            toast({
                title: "Login Successful",
                description: `Welcome back, ${decoded.full_name || email}!`,
            });

            if (decoded.role === 'admin') navigate('/admin');
            else if (decoded.role === 'teacher') navigate('/teacher');
            else if (decoded.role === 'student') navigate('/student');
            else if (decoded.role === 'parent') navigate('/parent');

            return true;
        } catch (error) {
            console.error(error);
            toast({
                title: "Login Failed",
                description: error.response?.data?.detail || 'Invalid credentials',
                variant: "destructive",
            });
            return false;
        }
    };

    const registerWebAuthn = async () => {
        try {
            const optionsResp = await api.post('/auth/webauthn/register/generate');
            const options = optionsResp.data;
            const attResp = await startRegistration(options);
            const verificationResp = await api.post('/auth/webauthn/register/verify', { credential: attResp });
            toast({ title: 'Success', description: verificationResp.data.msg });
            return true;
        } catch (err) {
            console.error(err);
            toast({ title: 'Error', description: err.response?.data?.detail || 'Failed to register passkey', variant: 'destructive' });
            return false;
        }
    };

    const loginWebAuthn = async (email) => {
        try {
            const optionsResp = await api.post('/auth/webauthn/login/generate', { email });
            const options = optionsResp.data;
            const asseResp = await startAuthentication(options);
            const verificationResp = await api.post('/auth/webauthn/login/verify', { email, credential: asseResp });

            const { access_token, refresh_token } = verificationResp.data;
            localStorage.setItem('token', access_token);
            localStorage.setItem('refresh_token', refresh_token);
            setToken(access_token);

            const decoded = jwtDecode(access_token);
            setUser(decoded);
            setRole(decoded.role);

            toast({ title: "Login Successful", description: `Welcome back via Passkey!` });

            if (decoded.role === 'admin') navigate('/admin');
            else if (decoded.role === 'teacher') navigate('/teacher');
            else if (decoded.role === 'student') navigate('/student');
            else if (decoded.role === 'parent') navigate('/parent');

            return true;
        } catch (err) {
            console.error(err);
            toast({ title: 'Login Failed', description: err.response?.data?.detail || 'Failed to authenticate with passkey', variant: 'destructive' });
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
        <AuthContext.Provider value={{ user, role, token, login, loginWebAuthn, registerWebAuthn, logout, refreshProfile, loading }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
