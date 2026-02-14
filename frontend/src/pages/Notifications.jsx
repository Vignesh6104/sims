import React, { useState, useEffect } from 'react';
import {
    Send,
    CheckCircle2,
    RefreshCw,
    Bell,
    Megaphone,
    Mail
} from 'lucide-react';
import api from '../api/axios';
import { useToast } from "@/components/ui/use-toast";
import { useAuth } from '../context/AuthContext';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { cn } from '@/lib/utils';

const Notifications = () => {
    const { role } = useAuth();
    const [notifications, setNotifications] = useState([]);
    const [loading, setLoading] = useState(false);
    const [form, setForm] = useState({
        title: '',
        message: '',
        recipient_role: 'all',
        recipient_id: ''
    });
    const { toast } = useToast();

    const fetchNotifications = async () => {
        setLoading(true);
        try {
            const res = await api.get('/notifications/');
            setNotifications(res.data);
        } catch (error) {
            console.error("Failed to fetch notifications");
        } finally {
            setLoading(false);
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
            toast({
                title: "Success",
                description: "Notification sent successfully",
            });
            setForm({ title: '', message: '', recipient_role: 'all', recipient_id: '' });
            fetchNotifications();
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to send notification",
                variant: "destructive",
            });
        }
    };

    const handleMarkRead = async (id) => {
        try {
            await api.put(`/notifications/${id}/read/`);
            fetchNotifications();
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to mark as read",
                variant: "destructive",
            });
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Notifications</h2>
                    <p className="text-muted-foreground">Broadcast announcements and stay updated with school alerts.</p>
                </div>
                <Button variant="outline" size="sm" onClick={fetchNotifications} disabled={loading}>
                    <RefreshCw className={cn("mr-2 h-4 w-4", loading && "animate-spin")} />
                    Refresh
                </Button>
            </div>

            <div className="grid gap-6 md:grid-cols-12">
                {/* Admin/Teacher Send Form */}
                {(role === 'admin' || role === 'teacher') && (
                    <div className="md:col-span-5 lg:col-span-4">
                        <Card className="glass sticky top-24">
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Megaphone size={20} className="text-blue-600" />
                                    New Broadcast
                                </CardTitle>
                                <CardDescription>Send a message to specific user roles.</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="space-y-2">
                                    <Label htmlFor="title">Title</Label>
                                    <Input
                                        id="title"
                                        placeholder="Announcement Title"
                                        value={form.title}
                                        onChange={(e) => setForm({...form, title: e.target.value})}
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="message">Message</Label>
                                    <Textarea
                                        id="message"
                                        placeholder="Type your message here..."
                                        rows={4}
                                        value={form.message}
                                        onChange={(e) => setForm({...form, message: e.target.value})}
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="recipient">Recipient Group</Label>
                                    <Select 
                                        value={form.recipient_role} 
                                        onValueChange={(v) => setForm({...form, recipient_role: v})}
                                    >
                                        <SelectTrigger id="recipient">
                                            <SelectValue placeholder="Select Recipient" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="all">All Users</SelectItem>
                                            <SelectItem value="student">All Students</SelectItem>
                                            <SelectItem value="teacher">All Teachers</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>
                                <Button 
                                    className="w-full bg-blue-600 hover:bg-blue-700 mt-4" 
                                    onClick={handleSubmit}
                                    disabled={!form.title || !form.message}
                                >
                                    <Send size={18} className="mr-2" />
                                    Broadcast Now
                                </Button>
                            </CardContent>
                        </Card>
                    </div>
                )}

                {/* Notifications List */}
                <div className={cn(
                    "md:col-span-7 lg:col-span-8",
                    (role !== 'admin' && role !== 'teacher') && "md:col-span-12"
                )}>
                    <Card className="border-none shadow-none bg-transparent">
                        <CardHeader className="px-0 pt-0">
                            <CardTitle>Recent Notifications</CardTitle>
                        </CardHeader>
                        <CardContent className="px-0">
                            <div className="space-y-4">
                                {notifications.length === 0 ? (
                                    <div className="flex flex-col items-center justify-center py-24 bg-white/50 rounded-2xl border-2 border-dashed">
                                        <Bell size={48} className="text-muted-foreground opacity-20 mb-4" />
                                        <p className="text-muted-foreground font-medium text-lg">Your inbox is empty.</p>
                                    </div>
                                ) : (
                                    notifications.map((n) => (
                                        <Card 
                                            key={n.id} 
                                            className={cn(
                                                "transition-all duration-200 border-none shadow-sm",
                                                n.is_read ? "bg-white/40 opacity-80" : "bg-white border-l-4 border-l-blue-600"
                                            )}
                                        >
                                            <CardContent className="p-4 sm:p-6">
                                                <div className="flex items-start justify-between gap-4">
                                                    <div className="flex items-start gap-4 flex-1">
                                                        <div className={cn(
                                                            "p-2 rounded-full",
                                                            n.is_read ? "bg-gray-100 text-gray-500" : "bg-blue-100 text-blue-600"
                                                        )}>
                                                            <Mail size={18} />
                                                        </div>
                                                        <div className="space-y-1 flex-1">
                                                            <div className="flex items-center flex-wrap gap-2">
                                                                <h4 className={cn(
                                                                    "text-base font-semibold",
                                                                    !n.is_read && "text-blue-900"
                                                                )}>
                                                                    {n.title}
                                                                </h4>
                                                                {n.recipient_role === 'all' && (
                                                                    <Badge variant="outline" className="text-[10px] h-5 bg-gray-50 uppercase tracking-tighter">Public</Badge>
                                                                )}
                                                                {!n.is_read && n.recipient_id && (
                                                                    <Badge variant="destructive" className="text-[10px] h-5 uppercase animate-pulse">New</Badge>
                                                                )}
                                                            </div>
                                                            <p className="text-sm text-gray-600 leading-relaxed">
                                                                {n.message}
                                                            </p>
                                                            <p className="text-[11px] text-muted-foreground pt-2">
                                                                {new Date(n.created_at).toLocaleString()}
                                                            </p>
                                                        </div>
                                                    </div>
                                                    
                                                    {!n.is_read && n.recipient_id && (
                                                        <Button 
                                                            variant="ghost" 
                                                            size="icon" 
                                                            className="text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                                                            onClick={() => handleMarkRead(n.id)}
                                                        >
                                                            <CheckCircle2 size={20} />
                                                        </Button>
                                                    )}
                                                </div>
                                            </CardContent>
                                        </Card>
                                    ))
                                )}
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
};

export default Notifications;
