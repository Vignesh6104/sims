import React, { useState } from 'react';
import { 
    Lock, 
    Mail, 
    Loader2, 
    ArrowLeft 
} from 'lucide-react';
import { Link as RouterLink } from 'react-router-dom';
import api from '../api/axios';
import { useToast } from "@/components/ui/use-toast";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

const ForgotPassword = () => {
    const [email, setEmail] = useState('');
    const [loading, setLoading] = useState(false);
    const { toast } = useToast();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const res = await api.post('/auth/forgot-password', { email });
            toast({
                title: "Request Sent",
                description: res.data.msg,
            });
            if (res.data.token) {
                console.log("Reset Token (Dev):", res.data.token);
                toast({
                    title: "Dev Mode Info",
                    description: "Reset token printed to console.",
                });
            }
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
                    <Avatar className="h-16 w-16 mx-auto mb-4 bg-purple-100 text-purple-600 border-none">
                        <AvatarFallback className="bg-transparent">
                            <Lock size={32} />
                        </AvatarFallback>
                    </Avatar>
                    <CardTitle className="text-2xl font-bold tracking-tight">Forgot Password</CardTitle>
                    <CardDescription className="px-4">
                        Enter your email address and we'll send you a token to reset your password.
                    </CardDescription>
                </CardHeader>
                <CardContent className="p-8">
                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div className="space-y-2">
                            <Label htmlFor="email">Email Address</Label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                <Input
                                    id="email"
                                    type="email"
                                    placeholder="name@school.com"
                                    className="pl-10 h-11"
                                    required
                                    autoFocus
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                />
                            </div>
                        </div>

                        <Button 
                            type="submit" 
                            className="w-full h-11 bg-blue-600 hover:bg-blue-700 font-bold"
                            disabled={loading}
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Processing...
                                </>
                            ) : (
                                "Send Reset Token"
                            )}
                        </Button>

                        <div className="text-center">
                            <Button variant="link" asChild className="text-blue-600 hover:text-blue-700 p-0 font-bold">
                                <RouterLink to="/login" className="inline-flex items-center gap-2">
                                    <ArrowLeft size={16} />
                                    Back to login
                                </RouterLink>
                            </Button>
                        </div>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
};

export default ForgotPassword;
