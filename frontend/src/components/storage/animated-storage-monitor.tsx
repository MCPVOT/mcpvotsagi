'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { HardDrive } from 'lucide-react';
import { cn } from '@/lib/utils';

interface AnimatedStorageMonitorProps {
  used: number;
  total: number;
  className?: string;
}

export function AnimatedStorageMonitor({ used, total, className }: AnimatedStorageMonitorProps) {
  const percentage = (used / total) * 100;
  
  return (
    <Card className={cn('transition-all hover:shadow-lg', className)}>
      <CardHeader>
        <div className="flex items-center gap-2">
          <HardDrive className="h-5 w-5" />
          <CardTitle>Storage Monitor</CardTitle>
        </div>
        <CardDescription>
          {used.toFixed(2)} GB / {total.toFixed(2)} GB used
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Progress value={percentage} className="h-2" />
        <p className="text-sm text-muted-foreground mt-2">
          {percentage.toFixed(1)}% utilized
        </p>
      </CardContent>
    </Card>
  );
}