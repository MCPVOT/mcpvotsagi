'use client';

import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';

export function AreaGraphSkeleton() {
  return (
    <Card className="w-full">
      <CardHeader>
        <Skeleton className="h-6 w-48" />
        <Skeleton className="h-4 w-64" />
      </CardHeader>
      <CardContent>
        <div className="h-64 flex items-end gap-2 p-4">
          {Array.from({ length: 6 }).map((_, index) => (
            <div key={index} className="flex-1 flex flex-col items-center gap-2">
              <Skeleton
                className="w-full rounded-t"
                style={{ height: `${Math.random() * 80 + 20}%` }}
              />
              <Skeleton className="h-3 w-8" />
            </div>
          ))}
        </div>
        <Skeleton className="h-4 w-32 mt-4" />
      </CardContent>
    </Card>
  );
}

export default AreaGraphSkeleton;
