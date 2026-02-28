import React, { useState, useEffect } from 'react';
import {
    User,
    Mail,
    Lock,
    Camera,
    Loader2,
    Save,
    CheckCircle2,
    Shield,
    Briefcase,
    GraduationCap,
    Hash,
    MapPin,
    Calendar
} from 'lucide-react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { useToast } from "@/components/ui/use-toast";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogFooter
} from "@/components/ui/dialog";
import { Slider } from "@/components/ui/slider";
import Cropper from 'react-easy-crop';
import { getCroppedImgBlob } from '../utils/imageUtils';
import { cn } from '@/lib/utils';

const Profile = () => {
    const { user, role, refreshProfile, registerWebAuthn } = useAuth();
    const { toast } = useToast();
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    // Cropping State
    const [imageSrc, setImageSrc] = useState(null);
    const [crop, setCrop] = useState({ x: 0, y: 0 });
    const [zoom, setZoom] = useState(1);
    const [croppedAreaPixels, setCroppedAreaPixels] = useState(null);
    const [openCrop, setOpenCrop] = useState(false);

    // Form States
    const [infoForm, setInfoForm] = useState({
        full_name: '',
        email: '',
        // Role specific
        department: '',
        position: '',
        qualification: '',
        subject_specialization: '',
        roll_number: '',
        address: ''
    });

    const [passwordForm, setPasswordForm] = useState({
        current_password: '',
        new_password: '',
        confirm_password: ''
    });

    useEffect(() => {
        fetchProfile();
    }, []);

    const fetchProfile = async () => {
        try {
            const res = await api.get('/auth/me');
            setProfile(res.data);
            setInfoForm({
                full_name: res.data.full_name || '',
                email: res.data.email || '',
                department: res.data.department || '',
                position: res.data.position || '',
                qualification: res.data.qualification || '',
                subject_specialization: res.data.subject_specialization || '',
                roll_number: res.data.roll_number || '',
                address: res.data.address || ''
            });
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to load profile data",
                variant: "destructive",
            });
        } finally {
            setLoading(false);
        }
    };

    const handleImageSelection = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.addEventListener('load', () => {
            setImageSrc(reader.result);
            setOpenCrop(true);
        });
        reader.readAsDataURL(file);
    };

    const onCropComplete = (croppedArea, croppedAreaPixels) => {
        setCroppedAreaPixels(croppedAreaPixels);
    };

    const handleSaveCroppedImage = async () => {
        setSaving(true);
        try {
            const croppedBlob = await getCroppedImgBlob(imageSrc, croppedAreaPixels);
            const formData = new FormData();
            formData.append('file', croppedBlob, 'profile.jpg');

            await api.put('/auth/me/profile-image', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            toast({ title: "Success", description: "Profile image updated" });
            await refreshProfile();
            fetchProfile();
            setOpenCrop(false);
        } catch (error) {
            console.error(error);
            toast({ title: "Error", description: "Failed to crop or upload image", variant: "destructive" });
        } finally {
            setSaving(false);
        }
    };

    const handleInfoUpdate = async (e) => {
        e.preventDefault();
        setSaving(true);
        try {
            await api.put('/auth/me', infoForm);
            toast({
                title: "Profile Updated",
                description: "Your information has been saved successfully.",
            });
            await refreshProfile();
            fetchProfile();
        } catch (error) {
            toast({
                title: "Update Failed",
                description: error.response?.data?.detail || "Something went wrong",
                variant: "destructive",
            });
        } finally {
            setSaving(false);
        }
    };

    const handlePasswordUpdate = async (e) => {
        e.preventDefault();
        if (passwordForm.new_password !== passwordForm.confirm_password) {
            toast({ title: "Error", description: "Passwords do not match", variant: "destructive" });
            return;
        }

        setSaving(true);
        try {
            await api.put('/auth/me', { password: passwordForm.new_password });
            toast({
                title: "Password Changed",
                description: "Your password has been updated.",
            });
            setPasswordForm({ current_password: '', new_password: '', confirm_password: '' });
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to update password",
                variant: "destructive",
            });
        } finally {
            setSaving(false);
        }
    };

    if (loading) return (
        <div className="flex items-center justify-center h-[80vh]">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
    );

    return (
        <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in duration-500">
            <div className="flex flex-col space-y-2">
                <h2 className="text-3xl font-bold tracking-tight uppercase">Profile Settings</h2>
                <p className="text-muted-foreground">Manage your account information and preferences.</p>
            </div>

            <div className="grid gap-8 md:grid-cols-12">
                {/* Left Column: Avatar & Quick Info */}
                <div className="md:col-span-4 space-y-6">
                    <Card className="border-none shadow-xl overflow-hidden bg-card">
                        <div className="h-32 bg-primary/80" />
                        <CardContent className="relative pt-0 flex flex-col items-center">
                            <div className="relative -mt-16 mb-4">
                                <Avatar className="h-32 w-32 border-4 border-card shadow-2xl">
                                    <AvatarImage src={profile?.profile_image} />
                                    <AvatarFallback className="text-3xl bg-primary/10 text-primary">
                                        {profile?.full_name?.charAt(0) || 'U'}
                                    </AvatarFallback>
                                </Avatar>
                                <label className="absolute bottom-0 right-0 p-2 bg-primary rounded-full text-primary-foreground cursor-pointer hover:bg-primary/90 transition-colors shadow-lg">
                                    <Camera size={18} />
                                    <input type="file" className="hidden" onChange={handleImageSelection} accept="image/*" />
                                </label>
                            </div>
                            <h3 className="text-xl font-bold text-foreground">{profile?.full_name}</h3>
                            <p className="text-sm text-muted-foreground uppercase tracking-widest font-semibold mt-1">
                                {role}
                            </p>

                            <div className="w-full mt-8 space-y-4">
                                <div className="flex items-center gap-3 text-sm text-muted-foreground">
                                    <div className="p-2 bg-muted rounded-lg"><Mail size={16} className="text-primary" /></div>
                                    {profile?.email}
                                </div>
                                {profile?.department && (
                                    <div className="flex items-center gap-3 text-sm text-muted-foreground">
                                        <div className="p-2 bg-muted rounded-lg"><Shield size={16} className="text-primary" /></div>
                                        {profile.department}
                                    </div>
                                )}
                                {profile?.roll_number && (
                                    <div className="flex items-center gap-3 text-sm text-muted-foreground">
                                        <div className="p-2 bg-muted rounded-lg"><Hash size={16} className="text-primary" /></div>
                                        Roll No: {profile.roll_number}
                                    </div>
                                )}
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Right Column: Forms */}
                <div className="md:col-span-8">
                    <Tabs defaultValue="general" className="w-full">
                        <TabsList className="grid w-full grid-cols-2 mb-8 bg-muted/50 p-1 rounded-xl">
                            <TabsTrigger value="general" className="rounded-lg">General Info</TabsTrigger>
                            <TabsTrigger value="security" className="rounded-lg">Security</TabsTrigger>
                        </TabsList>

                        <TabsContent value="general" className="mt-0">
                            <Card className="border-none shadow-xl bg-card">
                                <CardHeader>
                                    <CardTitle className="text-foreground">Personal Information</CardTitle>
                                    <CardDescription>Update your basic profile details.</CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <form onSubmit={handleInfoUpdate} className="space-y-6">
                                        <div className="grid gap-4 sm:grid-cols-2">
                                            <div className="space-y-2">
                                                <Label htmlFor="name" className="text-foreground font-semibold">Full Name</Label>
                                                <Input
                                                    id="name"
                                                    value={infoForm.full_name}
                                                    onChange={(e) => setInfoForm({ ...infoForm, full_name: e.target.value })}
                                                    className="bg-background/50 border-border"
                                                />
                                            </div>
                                            <div className="space-y-2">
                                                <Label htmlFor="email" className="text-foreground font-semibold">Email Address</Label>
                                                <Input
                                                    id="email"
                                                    type="email"
                                                    value={infoForm.email}
                                                    onChange={(e) => setInfoForm({ ...infoForm, email: e.target.value })}
                                                    className="bg-background/50 border-border"
                                                />
                                            </div>

                                            {role === 'admin' && (
                                                <>
                                                    <div className="space-y-2">
                                                        <Label className="text-foreground font-semibold">Department</Label>
                                                        <Input value={infoForm.department} onChange={(e) => setInfoForm({ ...infoForm, department: e.target.value })} className="bg-background/50 border-border" />
                                                    </div>
                                                    <div className="space-y-2">
                                                        <Label className="text-foreground font-semibold">Position</Label>
                                                        <Input value={infoForm.position} onChange={(e) => setInfoForm({ ...infoForm, position: e.target.value })} className="bg-background/50 border-border" />
                                                    </div>
                                                </>
                                            )}

                                            {role === 'teacher' && (
                                                <>
                                                    <div className="space-y-2">
                                                        <Label className="text-foreground font-semibold">Qualification</Label>
                                                        <Input value={infoForm.qualification} onChange={(e) => setInfoForm({ ...infoForm, qualification: e.target.value })} className="bg-background/50 border-border" />
                                                    </div>
                                                    <div className="space-y-2">
                                                        <Label className="text-foreground font-semibold">Specialization</Label>
                                                        <Input value={infoForm.subject_specialization} onChange={(e) => setInfoForm({ ...infoForm, subject_specialization: e.target.value })} className="bg-background/50 border-border" />
                                                    </div>
                                                </>
                                            )}

                                            {role === 'student' && (
                                                <>
                                                    <div className="space-y-2">
                                                        <Label className="text-foreground font-semibold">Roll Number</Label>
                                                        <Input value={infoForm.roll_number} readOnly className="bg-muted border-border font-bold" />
                                                    </div>
                                                    <div className="space-y-2">
                                                        <Label className="text-foreground font-semibold">Address</Label>
                                                        <Input value={infoForm.address} onChange={(e) => setInfoForm({ ...infoForm, address: e.target.value })} className="bg-background/50 border-border" />
                                                    </div>
                                                </>
                                            )}
                                        </div>

                                        <div className="pt-4 border-t border-border flex justify-end">
                                            <Button type="submit" className="bg-primary hover:bg-primary/90 text-primary-foreground font-bold shadow-lg h-11 px-8" disabled={saving}>
                                                {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
                                                Save Changes
                                            </Button>
                                        </div>
                                    </form>
                                </CardContent>
                            </Card>
                        </TabsContent>

                        <TabsContent value="security" className="mt-0">
                            <Card className="border-none shadow-xl bg-card">
                                <CardHeader>
                                    <CardTitle className="text-foreground">Change Password</CardTitle>
                                    <CardDescription>Ensure your account is using a long, random password to stay secure.</CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <form onSubmit={handlePasswordUpdate} className="space-y-6">
                                        <div className="space-y-4 max-w-md">
                                            <div className="space-y-2">
                                                <Label htmlFor="new-password text-foreground font-semibold">New Password</Label>
                                                <Input
                                                    id="new-password"
                                                    type="password"
                                                    value={passwordForm.new_password}
                                                    onChange={(e) => setPasswordForm({ ...passwordForm, new_password: e.target.value })}
                                                    className="bg-background/50 border-border"
                                                />
                                            </div>
                                            <div className="space-y-2">
                                                <Label htmlFor="confirm-password text-foreground font-semibold">Confirm New Password</Label>
                                                <Input
                                                    id="confirm-password"
                                                    type="password"
                                                    value={passwordForm.confirm_password}
                                                    onChange={(e) => setPasswordForm({ ...passwordForm, confirm_password: e.target.value })}
                                                    className="bg-background/50 border-border"
                                                />
                                            </div>
                                        </div>

                                        <div className="pt-4 border-t border-border flex justify-end">
                                            <Button type="submit" className="bg-primary hover:bg-primary/90 text-primary-foreground font-bold shadow-lg h-11 px-8" disabled={saving}>
                                                {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Lock className="mr-2 h-4 w-4" />}
                                                Update Password
                                            </Button>
                                        </div>
                                    </form>
                                </CardContent>
                            </Card>

                            <Card className="border-none shadow-xl bg-card mt-6">
                                <CardHeader>
                                    <CardTitle className="text-foreground">Passkey / Fingerprint</CardTitle>
                                    <CardDescription>Register your device's biometric sensor for faster, secure logins.</CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <div className="flex items-center justify-between">
                                        <div className="space-y-1">
                                            <p className="text-sm font-bold leading-none text-foreground">Add a Passkey</p>
                                            <p className="text-sm text-muted-foreground">
                                                Use TouchID, FaceID, or Windows Hello.
                                            </p>
                                        </div>
                                        <Button
                                            type="button"
                                            variant="outline"
                                            className="border-primary text-primary hover:bg-primary/10 font-bold"
                                            onClick={async () => {
                                                setSaving(true);
                                                await registerWebAuthn();
                                                setSaving(false);
                                            }}
                                            disabled={saving}
                                        >
                                            {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                                            Register Passkey
                                        </Button>
                                    </div>
                                </CardContent>
                            </Card>
                        </TabsContent>
                    </Tabs>
                </div>
            </div>

            {/* Image Cropping Dialog */}
            <Dialog open={openCrop} onOpenChange={setOpenCrop}>
                <DialogContent className="sm:max-w-[500px] bg-card border-border">
                    <DialogHeader>
                        <DialogTitle className="text-foreground">Crop Profile Image</DialogTitle>
                        <DialogDescription>Adjust your profile picture before uploading.</DialogDescription>
                    </DialogHeader>
                    <div className="relative w-full h-80 bg-muted rounded-lg overflow-hidden">
                        {imageSrc && (
                            <Cropper
                                image={imageSrc}
                                crop={crop}
                                zoom={zoom}
                                aspect={1}
                                onCropChange={setCrop}
                                onCropComplete={onCropComplete}
                                onZoomChange={setZoom}
                            />
                        )}
                    </div>
                    <div className="py-4 space-y-2">
                        <Label className="text-foreground font-semibold">Zoom</Label>
                        <Slider
                            value={[zoom]}
                            min={1}
                            max={3}
                            step={0.1}
                            onValueChange={([val]) => setZoom(val)}
                        />
                    </div>
                    <DialogFooter>
                        <Button variant="outline" className="border-border text-foreground hover:bg-muted" onClick={() => setOpenCrop(false)}>Cancel</Button>
                        <Button className="bg-primary hover:bg-primary/90 text-primary-foreground font-bold shadow-lg" onClick={handleSaveCroppedImage} disabled={saving}>
                            {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
                            Apply & Save
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
};

export default Profile;
