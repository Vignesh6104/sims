import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    Clock,
    AlertCircle,
    CheckCircle,
    ChevronLeft,
    ChevronRight,
    Send
} from 'lucide-react';
import api from '../../api/axios';
import { useToast } from "@/components/ui/use-toast";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { useAuth } from "@/context/AuthContext";

const TakeQuiz = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { toast } = useToast();
    
    const [quiz, setQuiz] = useState(null);
    const [loading, setLoading] = useState(true);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [answers, setAnswers] = useState([]);
    const [timeLeft, setTimeLeft] = useState(0);
    const [submitted, setSubmitted] = useState(false);
    const [result, setResult] = useState(null);

    useEffect(() => {
        const fetchQuiz = async () => {
            try {
                const response = await api.get(`/quizzes`);
                const foundQuiz = response.data.find(q => q.id === id);
                if (!foundQuiz) {
                    toast({ title: "Error", description: "Quiz not found", variant: "destructive" });
                    navigate('/student/quizzes');
                    return;
                }
                setQuiz(foundQuiz);
                setAnswers(new Array(foundQuiz.questions_data.length).fill(-1));
                setTimeLeft(foundQuiz.time_limit_minutes * 60);
            } catch (error) {
                toast({ title: "Error", description: "Failed to load quiz", variant: "destructive" });
            } finally {
                setLoading(false);
            }
        };
        fetchQuiz();
    }, [id]);

    useEffect(() => {
        if (timeLeft <= 0 || submitted) return;
        const timer = setInterval(() => {
            setTimeLeft(prev => {
                if (prev <= 1) {
                    clearInterval(timer);
                    handleSubmit();
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);
        return () => clearInterval(timer);
    }, [timeLeft, submitted]);

    const handleAnswerChange = (value) => {
        const newAnswers = [...answers];
        newAnswers[currentQuestionIndex] = parseInt(value);
        setAnswers(newAnswers);
    };

    const handleSubmit = async () => {
        if (submitted) return;
        setSubmitted(true);
        try {
            const response = await api.post('/quizzes/submit', {
                quiz_id: id,
                answers: answers
            });
            setResult(response.data);
            toast({ title: "Submitted", description: "Quiz submitted successfully!" });
        } catch (error) {
            toast({ title: "Error", description: "Submission failed", variant: "destructive" });
        }
    };

    if (loading) return <div className="flex justify-center p-10">Loading Quiz...</div>;
    if (!quiz) return null;

    if (result) {
        return (
            <div className="max-w-2xl mx-auto space-y-6 p-4">
                <Card className="glass border-none text-center p-8">
                    <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
                    <CardTitle className="text-3xl mb-2">Quiz Completed!</CardTitle>
                    <div className="text-5xl font-bold text-blue-600 my-6">
                        {result.score} / {result.total_points}
                    </div>
                    <p className="text-muted-foreground mb-8">
                        Your results have been recorded.
                    </p>
                    <Button onClick={() => navigate('/student/quizzes')}>Back to Quizzes</Button>
                </Card>
            </div>
        );
    }

    const currentQuestion = quiz.questions_data[currentQuestionIndex];
    const progress = ((currentQuestionIndex + 1) / quiz.questions_data.length) * 100;

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
    };

    return (
        <div className="max-w-3xl mx-auto space-y-6 p-4">
            <div className="flex items-center justify-between">
                <Button variant="ghost" onClick={() => navigate('/student/quizzes')}>
                    <ChevronLeft className="mr-2 h-4 w-4" /> Exit
                </Button>
                <div className={cn(
                    "flex items-center font-mono font-bold text-lg px-4 py-2 rounded-full",
                    timeLeft < 60 ? "bg-red-100 text-red-600 animate-pulse" : "bg-blue-100 text-blue-600"
                )}>
                    <Clock className="mr-2 h-5 w-5" />
                    {formatTime(timeLeft)}
                </div>
            </div>

            <Progress value={progress} className="h-2" />

            <Card className="glass border-none shadow-xl">
                <CardHeader>
                    <div className="flex justify-between items-center mb-2">
                        <Badge variant="secondary">Question {currentQuestionIndex + 1} of {quiz.questions_data.length}</Badge>
                        <Badge variant="outline">{currentQuestion.points} Points</Badge>
                    </div>
                    <CardTitle className="text-xl leading-relaxed">
                        {currentQuestion.question}
                    </CardTitle>
                </CardHeader>
                <CardContent className="pt-6">
                    <RadioGroup 
                        value={String(answers[currentQuestionIndex])} 
                        onValueChange={handleAnswerChange}
                        className="space-y-4"
                    >
                        {currentQuestion.options.map((option, idx) => (
                            <div key={idx} className={cn(
                                "flex items-center space-x-3 p-4 rounded-xl border transition-all cursor-pointer hover:bg-blue-50/50",
                                answers[currentQuestionIndex] === idx ? "border-blue-500 bg-blue-50" : "border-gray-200"
                            )}>
                                <RadioGroupItem value={String(idx)} id={`option-${idx}`} />
                                <Label htmlFor={`option-${idx}`} className="flex-1 cursor-pointer text-base">
                                    {option}
                                </Label>
                            </div>
                        ))}
                    </RadioGroup>
                </CardContent>
                <CardFooter className="flex justify-between border-t p-6">
                    <Button 
                        variant="outline" 
                        disabled={currentQuestionIndex === 0}
                        onClick={() => setCurrentQuestionIndex(prev => prev - 1)}
                    >
                        <ChevronLeft className="mr-2 h-4 w-4" /> Previous
                    </Button>
                    
                    {currentQuestionIndex === quiz.questions_data.length - 1 ? (
                        <Button className="bg-green-600 hover:bg-green-700" onClick={handleSubmit}>
                            <Send className="mr-2 h-4 w-4" /> Finish Quiz
                        </Button>
                    ) : (
                        <Button onClick={() => setCurrentQuestionIndex(prev => prev + 1)}>
                            Next <ChevronRight className="ml-2 h-4 w-4" />
                        </Button>
                    )}
                </CardFooter>
            </Card>
        </div>
    );
};

export default TakeQuiz;
