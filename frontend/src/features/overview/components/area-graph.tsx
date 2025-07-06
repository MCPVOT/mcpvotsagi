'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp } from 'lucide-react';

const chartData = [
  { month: 'Jan', value: 186 },
  { month: 'Feb', value: 305 },
  { month: 'Mar', value: 237 },
  { month: 'Apr', value: 173 },
  { month: 'May', value: 209 },
  { month: 'Jun', value: 214 }
];

export function AreaGraph() {
  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5" />
          System Performance
        </CardTitle>
        <CardDescription>
          AGI system metrics over the last 6 months
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-64 flex items-end gap-2 p-4">
          {chartData.map((data, index) => (
            <div key={index} className="flex-1 flex flex-col items-center gap-2">
              <div
                className="w-full bg-primary rounded-t opacity-80"
                style={{ height: `${(data.value / 305) * 100}%` }}
              />
              <span className="text-xs text-muted-foreground">{data.month}</span>
            </div>
          ))}
        </div>
        <div className="mt-4 text-sm text-muted-foreground">
          Trending up by 5.2% this month
        </div>
      </CardContent>
    </Card>
  );
}

export default AreaGraph;
