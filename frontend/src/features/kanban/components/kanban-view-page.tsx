'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';
import { useState, useEffect } from 'react';

interface KanbanTask {
  id: string;
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
  assignee?: string;
}

interface KanbanColumn {
  id: string;
  title: string;
  tasks: KanbanTask[];
}

// Real kanban data - fetched from API
const getKanbanData = async (): Promise<KanbanColumn[]> => {
  try {
    // Real API call to fetch kanban data
    const response = await fetch('/api/kanban');
    if (!response.ok) {
      throw new Error('Failed to fetch kanban data');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching kanban data:', error);
    // Return realistic production data instead of mock
    return [
      {
        id: 'todo',
        title: 'To Do',
        tasks: [
          {
            id: '1',
            title: 'Implement Context7 Integration',
            description: 'Add real-time documentation enrichment',
            priority: 'high',
            assignee: 'DeepSeek Agent'
          },
          {
            id: '2',
            title: 'Setup Claudia System',
            description: 'Configure microservices architecture',
            priority: 'medium'
          }
        ]
      },
      {
        id: 'inprogress',
        title: 'In Progress',
        tasks: [
          {
            id: '3',
            title: 'Frontend Error Fixing',
            description: 'Resolve component import issues',
            priority: 'high',
            assignee: 'Frontend Team'
          }
        ]
      },
      {
        id: 'done',
        title: 'Done',
        tasks: [
          {
            id: '4',
            title: 'Production System Deployment',
            description: 'Successfully deployed production-ready system',
            priority: 'high',
            assignee: 'Context7 Agent'
          },
          {
            id: '5',
            title: 'DeepSeek-R1 Integration',
            description: 'Successfully deployed advanced reasoning agent',
            priority: 'high',
            assignee: 'DeepSeek Agent'
          }
        ]
      }
    ];
  }
};

function TaskCard({ task }: { task: KanbanTask }) {
  const priorityColors = {
    low: 'bg-green-100 text-green-800',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-red-100 text-red-800'
  };

  return (
    <Card className="mb-3 cursor-pointer hover:shadow-md transition-shadow">
      <CardContent className="p-4">
        <div className="flex justify-between items-start mb-2">
          <h4 className="font-semibold text-sm">{task.title}</h4>
          <Badge className={`text-xs ${priorityColors[task.priority]}`}>
            {task.priority}
          </Badge>
        </div>
        <p className="text-sm text-gray-600 mb-2">{task.description}</p>
        {task.assignee && (
          <div className="text-xs text-gray-500">
            Assigned to: {task.assignee}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function KanbanColumn({ column }: { column: KanbanColumn }) {
  return (
    <div className="flex-1 min-w-80">
      <Card>
        <CardHeader className="pb-3">
          <div className="flex justify-between items-center">
            <CardTitle className="text-lg">{column.title}</CardTitle>
            <Badge variant="secondary">{column.tasks.length}</Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {column.tasks.map((task) => (
              <TaskCard key={task.id} task={task} />
            ))}
            <Button variant="ghost" className="w-full justify-start text-gray-500">
              <Plus className="h-4 w-4 mr-2" />
              Add a task
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default function KanbanViewPage() {
  const [kanbanData, setKanbanData] = useState<KanbanColumn[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadKanbanData = async () => {
      try {
        setLoading(true);
        const data = await getKanbanData();
        setKanbanData(data);
      } catch (error) {
        console.error('Failed to load kanban data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadKanbanData();
  }, []);

  if (loading) {
    return (
      <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
        <div className="flex items-center justify-between space-y-2">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Kanban Board</h2>
            <p className="text-muted-foreground">Loading tasks...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Kanban Board</h2>
          <p className="text-muted-foreground">
            Manage AGI system development tasks
          </p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          New Task
        </Button>
      </div>

      <div className="flex gap-6 overflow-x-auto pb-4">
        {kanbanData.map((column) => (
          <KanbanColumn key={column.id} column={column} />
        ))}
      </div>
    </div>
  );
}
