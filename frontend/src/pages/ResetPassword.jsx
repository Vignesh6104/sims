import React, { useState } from 'react';
import { 
    Key, 
    Lock, 
    CheckCircle2, 
    Loader2, 
    ShieldCheck 
} from 'lucide-react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import api from '../api/axios';
import { useToast } from "@/components/ui/use-toast";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

const ResetPassword = () => {
    const [form, setForm] = useState({ token: '', new_password: '', confirm_password: '' });
    const [loading, setLoading] = useState(false);
    const { toast } = useToast();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (form.new_password !== form.confirm_password) {
            return toast({
                title: "Mismatch",
                description: "Passwords do not match.",
                variant: "destructive",
            });
        }
        setLoading(true);
        try {
            const res = await api.post('/auth/reset-password', {
                token: form.token,
                new_password: form.new_password
            });
            toast({
                title: "Success",
                description: res.data.msg,
            });
            navigate('/login');
        } catch (error) {
            toast({
                title: "Error",
                description: error.response?.data?.detail || "Something went wrong",
                variant: "destructive",
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-4 bg-gray-50/50">
            <Card className="w-full max-w-md glass border-none shadow-xl">
                <CardHeader className="text-center pt-8">
                    <Avatar className="h-16 w-16 mx-auto mb-4 bg-blue-100 text-blue-600 border-none">
                        <AvatarFallback className="bg-transparent">
                            <ShieldCheck size={32} />
                        </AvatarFallback>
                    </Avatar>
                    <CardTitle className="text-2xl font-bold tracking-tight">Create New Password</CardTitle>
                    <CardDescription>
                        Please enter the reset token and your new password.
                    </CardDescription>
                </CardHeader>
                <CardContent className="p-8">
                    <form onSubmit={handleSubmit} className="space-y-5">
                        <div className="space-y-2">
                            <Label htmlFor="token">Reset Token</Label>
                            <div className="relative">
                                <Key className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                <Input
                                    id="token"
                                    placeholder="Enter your token"
                                    className="pl-10 h-11"
                                    required
                                    autoFocus
                                    value={form.token}
                                    onChange={(e) => setForm({...form, token: e.target.value})}
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="new_password">New Password</Label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                <Input
                                    id="new_password"
                                    type="password"
                                    className="pl-10 h-11"
                                    placeholder="••••••••"
                                    required
                                    value={form.new_password}
                                    onChange={(e) => setForm({...form, new_password: e.target.value})}
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="confirm_password">Confirm New Password</Label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                <Input
                                    id="confirm_password"
                                    type="password"
                                    className="pl-10 h-11"
                                    placeholder="••••••••"
                                    required
                                    value={form.confirm_password}
                                    onChange={(e) => setForm({...form, confirm_password: e.target.value})}
                                />
                            </div>
                        </div>

                        <Button 
                            type="submit" 
                            className="w-full h-11 bg-blue-600 hover:bg-blue-700 font-bold mt-4"
                            disabled={loading}
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Updating Password...
                                </>
                            ) : (
                                "Update Password"
                            )}
                        </Button>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
};

export default ResetPassword;
