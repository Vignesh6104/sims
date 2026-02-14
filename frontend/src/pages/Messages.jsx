import React, { useState, useEffect, useRef } from 'react';
import {
    Send,
    Search,
    User as UserIcon,
    Circle,
    RefreshCw
} from 'lucide-react';
import api from '../api/axios';
import { useToast } from "@/components/ui/use-toast";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useAuth } from '../context/AuthContext';
import { cn } from '@/lib/utils';
import { format } from 'date-fns';

const Messages = () => {
    const { user, role } = useAuth();
    const { toast } = useToast();
    const [messages, setMessages] = useState([]);
    const [contacts, setContacts] = useState([]);
    const [selectedContact, setSelectedContact] = useState(null);
    const [newMessage, setNewMessage] = useState('');
    const [loading, setLoading] = useState(true);
    const [sending, setSending] = useState(false);
    const scrollRef = useRef(null);

    const fetchContacts = async () => {
        try {
            // In a real app, we might have a dedicated contacts endpoint.
            // For now, let's fetch a few recent users or roles based on who the user is.
            // Simplified: Fetch all teachers if student, all students if teacher, etc.
            let res;
            if (role === 'student') res = await api.get('/teachers');
            else res = await api.get('/students');
            
            setContacts(res.data.map(c => ({
                id: c.id,
                name: c.full_name,
                role: role === 'student' ? 'teacher' : 'student',
                image: c.profile_image
            })));
        } catch (error) {
            console.error("Failed to fetch contacts");
        }
    };

    const fetchConversation = async (contactId) => {
        setLoading(true);
        try {
            const res = await api.get(`/messages/conversation/${contactId}`);
            setMessages(res.data);
        } catch (error) {
            toast({ title: "Error", description: "Failed to load messages", variant: "destructive" });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchContacts();
    }, []);

    useEffect(() => {
        if (selectedContact) {
            fetchConversation(selectedContact.id);
        }
    }, [selectedContact]);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!newMessage.trim() || !selectedContact || sending) return;

        setSending(true);
        try {
            const res = await api.post('/messages', {
                receiver_id: selectedContact.id,
                receiver_role: selectedContact.role,
                receiver_name: selectedContact.name,
                content: newMessage
            });
            setMessages([...messages, res.data]);
            setNewMessage('');
        } catch (error) {
            toast({ title: "Error", description: "Failed to send message", variant: "destructive" });
        } finally {
            setSending(false);
        }
    };

    return (
        <div className="flex h-[calc(100vh-120px)] gap-4">
            {/* Contacts Sidebar */}
            <Card className="w-80 flex flex-col glass border-none">
                <CardHeader className="p-4 border-b">
                    <div className="relative">
                        <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                        <Input placeholder="Search contacts..." className="pl-8" />
                    </div>
                </CardHeader>
                <ScrollArea className="flex-1">
                    <div className="p-2 space-y-1">
                        {contacts.map((contact) => (
                            <button
                                key={contact.id}
                                onClick={() => setSelectedContact(contact)}
                                className={cn(
                                    "flex items-center w-full p-3 rounded-lg transition-colors",
                                    selectedContact?.id === contact.id ? "bg-blue-100" : "hover:bg-gray-100"
                                )}
                            >
                                <Avatar className="h-10 w-10 border">
                                    <AvatarImage src={contact.image} />
                                    <AvatarFallback>{contact.name.charAt(0)}</AvatarFallback>
                                </Avatar>
                                <div className="ml-3 text-left overflow-hidden">
                                    <p className="text-sm font-medium truncate">{contact.name}</p>
                                    <p className="text-xs text-muted-foreground capitalize">{contact.role}</p>
                                </div>
                            </button>
                        ))}
                    </div>
                </ScrollArea>
            </Card>

            {/* Chat Area */}
            <Card className="flex-1 flex flex-col glass border-none overflow-hidden">
                {selectedContact ? (
                    <>
                        <CardHeader className="p-4 border-b flex flex-row items-center justify-between">
                            <div className="flex items-center">
                                <Avatar className="h-10 w-10 border">
                                    <AvatarImage src={selectedContact.image} />
                                    <AvatarFallback>{selectedContact.name.charAt(0)}</AvatarFallback>
                                </Avatar>
                                <div className="ml-3">
                                    <CardTitle className="text-base">{selectedContact.name}</CardTitle>
                                    <div className="flex items-center text-xs text-green-500">
                                        <Circle className="h-2 w-2 fill-current mr-1" /> Online
                                    </div>
                                </div>
                            </div>
                            <Button variant="ghost" size="icon" onClick={() => fetchConversation(selectedContact.id)}>
                                <RefreshCw className={cn("h-4 w-4", loading && "animate-spin")} />
                            </Button>
                        </CardHeader>
                        
                        <div 
                            className="flex-1 p-4 overflow-y-auto space-y-4"
                            ref={scrollRef}
                        >
                            {messages.map((msg) => {
                                const isMe = msg.sender_id === user.sub;
                                return (
                                    <div key={msg.id} className={cn(
                                        "flex flex-col max-w-[70%]",
                                        isMe ? "ml-auto items-end" : "mr-auto items-start"
                                    )}>
                                        <div className={cn(
                                            "px-4 py-2 rounded-2xl text-sm",
                                            isMe ? "bg-blue-600 text-white rounded-tr-none" : "bg-white border rounded-tl-none"
                                        )}>
                                            {msg.content}
                                        </div>
                                        <span className="text-[10px] text-muted-foreground mt-1">
                                            {format(new Date(msg.created_at), 'p')}
                                        </span>
                                    </div>
                                );
                            })}
                        </div>

                        <div className="p-4 border-t">
                            <form onSubmit={handleSendMessage} className="flex gap-2">
                                <Input 
                                    placeholder="Type a message..." 
                                    value={newMessage}
                                    onChange={(e) => setNewMessage(e.target.value)}
                                    className="flex-1"
                                />
                                <Button type="submit" disabled={sending || !newMessage.trim()}>
                                    <Send className="h-4 w-4" />
                                </Button>
                            </form>
                        </div>
                    </>
                ) : (
                    <div className="flex-1 flex flex-col items-center justify-center text-muted-foreground">
                        <div className="bg-gray-100 p-6 rounded-full mb-4">
                            <UserIcon size={48} />
                        </div>
                        <p>Select a contact to start messaging</p>
                    </div>
                )}
            </Card>
        </div>
    );
};

export default Messages;
