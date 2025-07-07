'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface AnimatedAgentCardProps {
  name: string;
  status: 'active' | 'idle' | 'offline';
  description?: string;
  model?: string;
  className?: string;
}

export function AnimatedAgentCard({ 
  name, 
  status, 
  description, 
  model,
  className 
}: AnimatedAgentCardProps) {
  const statusColors = {
    active: 'bg-green-500',
    idle: 'bg-yellow-500',
    offline: 'bg-gray-500'
  };

  return (
    <Card className={cn('transition-all hover:shadow-lg', className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">{name}</CardTitle>
          <div className="flex items-center gap-2">
            <div className={cn('w-2 h-2 rounded-full', statusColors[status])} />
            <Badge variant={status === 'active' ? 'default' : 'secondary'}>
              {status}
            </Badge>
          </div>
        </div>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      {model && (
        <CardContent>
          <p className="text-sm text-muted-foreground">Model: {model}</p>
        </CardContent>
      )}
    </Card>
  );
}