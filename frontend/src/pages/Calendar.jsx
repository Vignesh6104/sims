import React, { useState, useEffect } from 'react';
import { Calendar as BigCalendar, dateFnsLocalizer } from 'react-big-calendar';
import format from 'date-fns/format';
import parse from 'date-fns/parse';
import startOfWeek from 'date-fns/startOfWeek';
import getDay from 'date-fns/getDay';
import enUS from 'date-fns/locale/en-US';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import { 
    Plus, 
    Calendar as CalendarIcon,
    Loader2
} from 'lucide-react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { useToast } from "@/components/ui/use-toast";
import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogFooter,
} from "@/components/ui/dialog";
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
import { Card, CardContent } from "@/components/ui/card";
import { cn } from '@/lib/utils';

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
    const { user, role } = useAuth();
    const { toast } = useToast();
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
            toast({
                title: "Error",
                description: "Failed to fetch calendar events",
                variant: "destructive",
            });
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

    const handleSelectChange = (value) => {
        setFormData({ ...formData, type: value });
    };

    const handleSubmit = async () => {
        try {
            if (!formData.title || !formData.start_date || !formData.end_date) {
                toast({
                    title: "Missing fields",
                    description: "Please fill in all required fields",
                    variant: "destructive",
                });
                return;
            }

            await api.post('/events/', formData);
            toast({
                title: "Success",
                description: "Event added to calendar",
            });
            fetchEvents();
            handleClose();
        } catch (error) {
            toast({
                title: "Error",
                description: error.response?.data?.detail || "Failed to add event",
                variant: "destructive",
            });
        }
    };

    const eventStyleGetter = (event) => {
        let backgroundColor = '#2563eb'; // blue-600
        if (event.type === 'holiday') backgroundColor = '#ef4444'; // red-500
        if (event.type === 'exam') backgroundColor = '#f59e0b'; // amber-500
        return {
            style: {
                backgroundColor,
                borderRadius: '6px',
                border: 'none',
                padding: '2px 6px'
            }
        };
    };

    const isAdmin = role === 'admin';

    if (loading) return (
        <div className="flex flex-col items-center justify-center h-[80vh] space-y-4">
            <Loader2 className="h-10 w-10 animate-spin text-blue-600" />
            <p className="text-muted-foreground font-medium">Loading calendar...</p>
        </div>
    );

    return (
        <div className="h-full space-y-4">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Academic Calendar</h2>
                    <p className="text-muted-foreground">Keep track of school events, holidays, and exams.</p>
                </div>
                {isAdmin && (
                    <Button onClick={handleOpen}>
                        <Plus size={18} className="mr-2" />
                        Add Event
                    </Button>
                )}
            </div>

            <Card className="glass h-[calc(100vh-250px)] min-h-[500px] border-none shadow-sm overflow-hidden">
                <CardContent className="p-4 h-full">
                    <BigCalendar
                        localizer={localizer}
                        events={events}
                        startAccessor="start"
                        endAccessor="end"
                        style={{ height: '100%' }}
                        eventPropGetter={eventStyleGetter}
                        onSelectEvent={(event) => alert(`${event.title}\n${event.desc || ''}`)}
                        className="rounded-lg overflow-hidden"
                    />
                </CardContent>
            </Card>

            <Dialog open={open} onOpenChange={setOpen}>
                <DialogContent className="sm:max-w-[425px]">
                    <DialogHeader>
                        <DialogTitle>Add New Event</DialogTitle>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                        <div className="grid gap-2">
                            <Label htmlFor="title">Event Title</Label>
                            <Input
                                id="title"
                                name="title"
                                value={formData.title}
                                onChange={handleChange}
                                placeholder="e.g. Science Fair"
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="description">Description</Label>
                            <Textarea
                                id="description"
                                name="description"
                                value={formData.description}
                                onChange={handleChange}
                                placeholder="Describe the event..."
                                rows={3}
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="start_date">Start Date & Time</Label>
                            <Input
                                id="start_date"
                                name="start_date"
                                type="datetime-local"
                                value={formData.start_date}
                                onChange={handleChange}
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="end_date">End Date & Time</Label>
                            <Input
                                id="end_date"
                                name="end_date"
                                type="datetime-local"
                                value={formData.end_date}
                                onChange={handleChange}
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="type">Event Type</Label>
                            <Select 
                                value={formData.type} 
                                onValueChange={handleSelectChange}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder="Select Type" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="event">Standard Event</SelectItem>
                                    <SelectItem value="holiday">Holiday</SelectItem>
                                    <SelectItem value="exam">Examination</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={handleClose}>Cancel</Button>
                        <Button onClick={handleSubmit}>Add to Calendar</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
};

export default Calendar;
