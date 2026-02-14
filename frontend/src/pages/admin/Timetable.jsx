import React, { useState, useEffect } from 'react';
import {
    Plus,
    Trash2,
    Calendar,
} from 'lucide-react';
import api from '../../api/axios';
import { useToast } from "@/components/ui/use-toast";
import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogFooter,
} from "@/components/ui/dialog";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Card, CardContent } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { cn } from '@/lib/utils';

const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
const periods = [1, 2, 3, 4, 5, 6, 7, 8];

const Timetable = () => {
    const [classes, setClasses] = useState([]);
    const [subjects, setSubjects] = useState([]);
    const [teachers, setTeachers] = useState([]);
    const [selectedClass, setSelectedClass] = useState('');
    const [timetable, setTimetable] = useState([]);
    const [open, setOpen] = useState(false);
    const [selectedSlot, setSelectedSlot] = useState({ day: '', period: '' });
    const [form, setForm] = useState({ subject_id: '', teacher_id: '' });
    const { toast } = useToast();

    useEffect(() => {
        const fetchInitialData = async () => {
            try {
                const [clsRes, subRes, tchRes] = await Promise.all([
                    api.get('/class_rooms/'),
                    api.get('/subjects/'),
                    api.get('/teachers/')
                ]);
                setClasses(clsRes.data);
                setSubjects(subRes.data);
                setTeachers(tchRes.data);
            } catch (error) {
                console.error("Failed to fetch data");
            }
        };
        fetchInitialData();
    }, []);

    useEffect(() => {
        if (selectedClass && selectedClass !== 'none') {
            fetchTimetable();
        } else {
            setTimetable([]);
        }
    }, [selectedClass]);

    const fetchTimetable = async () => {
        try {
            const res = await api.get(`/timetable/class/${selectedClass}/`);
            setTimetable(res.data);
        } catch (error) {
            console.error("Failed to fetch timetable");
        }
    };

    const handleCellClick = (day, period) => {
        setSelectedSlot({ day, period });
        setForm({ subject_id: '', teacher_id: '' });
        setOpen(true);
    };

    const handleSubmit = async () => {
        try {
            await api.post('/timetable/', {
                class_id: selectedClass,
                day: selectedSlot.day,
                period: selectedSlot.period,
                subject_id: form.subject_id,
                teacher_id: form.teacher_id
            });
            toast({
                title: "Success",
                description: "Entry added to timetable",
            });
            setOpen(false);
            fetchTimetable();
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to add entry",
                variant: "destructive",
            });
        }
    };

    const handleDelete = async (e, id) => {
        e.stopPropagation();
        if (window.confirm('Delete this entry?')) {
            try {
                await api.delete(`/timetable/${id}/`);
                toast({
                    title: "Success",
                    description: "Entry deleted",
                });
                fetchTimetable();
            } catch (error) {
                toast({
                    title: "Error",
                    description: "Failed to delete",
                    variant: "destructive",
                });
            }
        }
    };

    const getEntry = (day, period) => {
        return timetable.find(t => t.day === day && t.period === period);
    };

    const getSubjectName = (id) => subjects.find(s => String(s.id) === String(id))?.name;
    const getTeacherName = (id) => teachers.find(t => String(t.id) === String(id))?.full_name;

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Timetable Management</h2>
                    <p className="text-muted-foreground">Plan and organize weekly class schedules.</p>
                </div>
                <div className="w-full sm:w-[250px]">
                    <Select value={selectedClass} onValueChange={setSelectedClass}>
                        <SelectTrigger className="glass">
                            <SelectValue placeholder="Select Class" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="none">Select Class</SelectItem>
                            {classes.map(c => (
                                <SelectItem key={c.id} value={String(c.id)}>{c.name}</SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>
            </div>

            {selectedClass && selectedClass !== 'none' ? (
                <div className="overflow-x-auto rounded-xl border bg-white shadow-sm">
                    <Table>
                        <TableHeader>
                            <TableRow className="bg-muted/50">
                                <TableHead className="w-[120px] font-bold">Day / Period</TableHead>
                                {periods.map(p => (
                                    <TableHead key={p} className="text-center font-bold">Period {p}</TableHead>
                                ))}
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {days.map(day => (
                                <TableRow key={day} className="h-32">
                                    <TableCell className="font-bold bg-muted/20">{day}</TableCell>
                                    {periods.map(period => {
                                        const entry = getEntry(day, period);
                                        return (
                                            <TableCell key={`${day}-${period}`} className="p-1 align-top min-w-[140px]">
                                                <div 
                                                    onClick={() => handleCellClick(day, period)}
                                                    className={cn(
                                                        "group relative h-full w-full rounded-lg p-3 transition-all cursor-pointer border-2 border-transparent",
                                                        entry 
                                                            ? "bg-blue-50/80 hover:bg-blue-100 hover:border-blue-200" 
                                                            : "bg-gray-50/50 hover:bg-gray-100 border-dashed border-gray-200"
                                                    )}
                                                >
                                                    {entry ? (
                                                        <div className="flex flex-col h-full space-y-1">
                                                            <p className="text-sm font-bold text-blue-900 leading-tight">
                                                                {getSubjectName(entry.subject_id)}
                                                            </p>
                                                            <p className="text-xs text-blue-700 font-medium">
                                                                {getTeacherName(entry.teacher_id)}
                                                            </p>
                                                            <button 
                                                                onClick={(e) => handleDelete(e, entry.id)}
                                                                className="absolute top-1 right-1 p-1 text-red-400 opacity-0 group-hover:opacity-100 transition-opacity hover:text-red-600"
                                                            >
                                                                <Trash2 size={14} />
                                                            </button>
                                                        </div>
                                                    ) : (
                                                        <div className="flex items-center justify-center h-full opacity-0 group-hover:opacity-40 transition-opacity">
                                                            <Plus size={20} className="text-gray-600" />
                                                        </div>
                                                    )}
                                                </div>
                                            </TableCell>
                                        );
                                    })}
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </div>
            ) : (
                <Card className="flex flex-col items-center justify-center py-24 bg-gray-50/50 border-dashed">
                    <Calendar size={48} className="text-muted-foreground mb-4 opacity-20" />
                    <p className="text-muted-foreground font-medium text-lg">
                        Please select a class to view or edit the timetable.
                    </p>
                </Card>
            )}

            <Dialog open={open} onOpenChange={setOpen}>
                <DialogContent className="sm:max-w-[400px]">
                    <DialogHeader>
                        <DialogTitle>Assign Period</DialogTitle>
                        <p className="text-sm text-muted-foreground">
                            {selectedSlot.day} — Period {selectedSlot.period}
                        </p>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                        <div className="grid gap-2">
                            <Label>Subject</Label>
                            <Select 
                                value={String(form.subject_id)} 
                                onValueChange={(v) => setForm({...form, subject_id: v})}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder="Select Subject" />
                                </SelectTrigger>
                                <SelectContent>
                                    {subjects.map(s => (
                                        <SelectItem key={s.id} value={String(s.id)}>{s.name}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="grid gap-2">
                            <Label>Teacher</Label>
                            <Select 
                                value={String(form.teacher_id)} 
                                onValueChange={(v) => setForm({...form, teacher_id: v})}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder="Select Teacher" />
                                </SelectTrigger>
                                <SelectContent>
                                    {teachers.map(t => (
                                        <SelectItem key={t.id} value={String(t.id)}>{t.full_name}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
                        <Button onClick={handleSubmit}>Save Entry</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
};

export default Timetable;
