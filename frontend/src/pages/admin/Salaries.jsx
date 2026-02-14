import React, { useState, useEffect } from 'react';
import {
    RefreshCw,
    DollarSign,
    CreditCard,
    TrendingUp
} from 'lucide-react';
import api from '../../api/axios';
import { useToast } from "@/components/ui/use-toast";
import { DataTable } from "@/components/ui/data-table";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from '@/lib/utils';
import { format } from 'date-fns';

const Salaries = () => {
    const [salaries, setSalaries] = useState([]);
    const [payroll, setPayroll] = useState([]);
    const [loading, setLoading] = useState(true);
    const { toast } = useToast();

    const fetchData = async () => {
        setLoading(true);
        try {
            const [salRes, payRes] = await Promise.all([
                api.get('/salaries/salaries'),
                api.get('/salaries/payroll')
            ]);
            setSalaries(salRes.data);
            setPayroll(payRes.data);
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to fetch payroll data",
                variant: "destructive",
            });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const payrollColumns = [
        { 
            accessorKey: "created_at", 
            header: "Date",
            cell: ({ row }) => format(new Date(row.original.created_at), 'PPP')
        },
        { 
            accessorKey: "teacher_id", 
            header: "Staff ID",
            cell: ({ row }) => <span className="font-mono text-xs">{row.original.teacher_id.substring(0, 8)}...</span>
        },
        { 
            header: "Period",
            cell: ({ row }) => `${row.original.month}/${row.original.year}`
        },
        { 
            accessorKey: "amount_paid", 
            header: "Amount",
            cell: ({ row }) => `$${row.original.amount_paid.toLocaleString()}`
        },
        { 
            accessorKey: "status", 
            header: "Status",
            cell: ({ row }) => (
                <Badge className={cn(
                    row.original.status === 'PAID' ? 'bg-green-500' : 'bg-yellow-500'
                )}>
                    {row.original.status}
                </Badge>
            )
        }
    ];

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">HR & Payroll</h2>
                    <p className="text-muted-foreground">Manage staff salaries and payment records.</p>
                </div>
                <Button variant="outline" onClick={fetchData} disabled={loading}>
                    <RefreshCw className={cn("mr-2 h-4 w-4", loading && "animate-spin")} />
                    Refresh
                </Button>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
                <Card className="glass border-none">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Monthly Payroll</CardTitle>
                        <DollarSign className="h-4 w-4 text-green-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">
                            ${payroll.reduce((acc, curr) => acc + curr.amount_paid, 0).toLocaleString()}
                        </div>
                        <p className="text-xs text-muted-foreground">Across all departments</p>
                    </CardContent>
                </Card>
                <Card className="glass border-none">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Active Staff</CardTitle>
                        <TrendingUp className="h-4 w-4 text-blue-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{salaries.length}</div>
                        <p className="text-xs text-muted-foreground">Paid this month</p>
                    </CardContent>
                </Card>
                <Card className="glass border-none">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Pending Payments</CardTitle>
                        <CreditCard className="h-4 w-4 text-yellow-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{payroll.filter(p => p.status !== 'PAID').length}</div>
                        <p className="text-xs text-muted-foreground">Requiring approval</p>
                    </CardContent>
                </Card>
            </div>

            <Card className="glass border-none">
                <CardHeader>
                    <CardTitle>Payroll History</CardTitle>
                </CardHeader>
                <CardContent>
                    <DataTable 
                        columns={payrollColumns} 
                        data={payroll} 
                        loading={loading}
                    />
                </CardContent>
            </Card>
        </div>
    );
};

export default Salaries;
