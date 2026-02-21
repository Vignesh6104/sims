import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useForm } from 'react-hook-form';
import { Link as RouterLink } from 'react-router-dom';
import {
    Eye,
    EyeOff,
    Lock,
    School,
    Loader2
} from 'lucide-react';
import { motion } from 'framer-motion';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

const Login = () => {
    const { login, loginWebAuthn } = useAuth();
    const { register, handleSubmit, formState: { errors }, watch } = useForm();
    const [loading, setLoading] = useState(false);
    const [loadingWebAuthn, setLoadingWebAuthn] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const emailValue = watch("email");

    const onSubmit = async (data) => {
        setLoading(true);
        await login(data.email, data.password);
        setLoading(false);
    };

    const togglePasswordVisibility = () => setShowPassword(!showPassword);

    return (
        <div className="flex min-h-screen bg-white">
            {/* Left side - Branding */}
            <div className="hidden lg:flex lg:w-7/12 relative overflow-hidden bg-blue-600">
                <div
                    className="absolute inset-0 bg-cover bg-center mix-blend-overlay opacity-40"
                    style={{ backgroundImage: 'url(https://images.unsplash.com/photo-1523050853064-8521a3a24143?q=80&w=2070&auto=format&fit=crop)' }}
                />
                <div className="absolute inset-0 bg-gradient-to-br from-blue-700/80 to-blue-900/80" />

                <div className="relative z-10 flex flex-col items-center justify-center w-full p-12 text-center text-white">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8 }}
                    >
                        <div className="inline-flex items-center justify-center p-4 bg-white/10 backdrop-blur-md rounded-3xl mb-8 border border-white/20">
                            <School size={80} className="text-white" />
                        </div>
                        <h1 className="text-6xl font-extrabold tracking-tight mb-4">
                            School IMS
                        </h1>
                        <p className="text-xl font-medium opacity-90 max-w-lg mx-auto">
                            A complete solution for modern education management and student success.
                        </p>
                    </motion.div>
                </div>
            </div>

            {/* Right side - Login Form */}
            <div className="flex flex-col justify-center w-full lg:w-5/12 p-8 sm:p-12 lg:p-16">
                <div className="w-full max-w-md mx-auto space-y-8">
                    <div className="text-center">
                        <Avatar className="h-16 w-16 mx-auto mb-4 bg-purple-100 text-purple-600 border-none">
                            <AvatarFallback className="bg-transparent">
                                <Lock size={32} />
                            </AvatarFallback>
                        </Avatar>
                        <h2 className="text-3xl font-bold text-gray-900 tracking-tight">
                            Welcome Back
                        </h2>
                        <p className="text-sm text-gray-500 mt-2">
                            Please enter your credentials to access your dashboard.
                        </p>
                    </div>

                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                        <div className="space-y-2">
                            <Label htmlFor="email">Email Address</Label>
                            <Input
                                id="email"
                                type="email"
                                placeholder="name@school.com"
                                className={errors.email ? "border-red-500" : ""}
                                {...register("email", {
                                    required: "Email is required",
                                    pattern: {
                                        value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                                        message: "Invalid email address"
                                    }
                                })}
                            />
                            {errors.email && (
                                <p className="text-xs text-red-500 font-medium">{errors.email.message}</p>
                            )}
                        </div>

                        <div className="space-y-2">
                            <div className="flex items-center justify-between">
                                <Label htmlFor="password">Password</Label>
                                <RouterLink
                                    to="/forgot-password"
                                    className="text-xs font-medium text-blue-600 hover:text-blue-500"
                                >
                                    Forgot password?
                                </RouterLink>
                            </div>
                            <div className="relative">
                                <Input
                                    id="password"
                                    type={showPassword ? 'text' : 'password'}
                                    className={errors.password ? "border-red-500 pr-10" : "pr-10"}
                                    {...register("password", { required: "Password is required" })}
                                />
                                <button
                                    type="button"
                                    onClick={togglePasswordVisibility}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                                >
                                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                                </button>
                            </div>
                            {errors.password && (
                                <p className="text-xs text-red-500 font-medium">{errors.password.message}</p>
                            )}
                        </div>

                        <Button
                            type="submit"
                            className="w-full h-11 bg-blue-600 hover:bg-blue-700 text-base font-semibold"
                            disabled={loading || loadingWebAuthn}
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Signing in...
                                </>
                            ) : (
                                "Sign In"
                            )}
                        </Button>

                        <div className="relative my-4">
                            <div className="absolute inset-0 flex items-center">
                                <span className="w-full border-t" />
                            </div>
                            <div className="relative flex justify-center text-xs uppercase">
                                <span className="bg-white px-2 text-gray-500">Or continue with</span>
                            </div>
                        </div>

                        <Button
                            type="button"
                            variant="outline"
                            className="w-full h-11 text-base font-semibold border-gray-300"
                            onClick={async () => {
                                if (!emailValue) {
                                    alert("Please enter your email address first");
                                    return;
                                }
                                setLoadingWebAuthn(true);
                                await loginWebAuthn(emailValue);
                                setLoadingWebAuthn(false);
                            }}
                            disabled={loading || loadingWebAuthn}
                        >
                            {loadingWebAuthn ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Authenticating...
                                </>
                            ) : (
                                "Passkey / Fingerprint"
                            )}
                        </Button>
                    </form>

                    <div className="text-center text-sm">
                        <span className="text-gray-500">Need help? </span>
                        <RouterLink to="/about" className="font-semibold text-blue-600 hover:text-blue-500">
                            Contact Support
                        </RouterLink>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;
