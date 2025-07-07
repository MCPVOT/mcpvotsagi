import {
  IconDashboard,
  IconFiles,
  IconUsers,
  IconPackages,
  IconSettings,
  IconChartLine,
  IconBrain,
  IconRobot,
  IconDatabase,
  IconCloud,
  IconShield,
  IconCode,
  IconWallet,
  IconChartPie,
  IconTarget,
  IconBulb,
  IconAdjustments
} from '@tabler/icons-react';

export interface NavItem {
  title: string;
  url: string;
  icon?: React.ComponentType<{ className?: string }>;
  isActive?: boolean;
  items?: NavItem[];
}

export const navItems: NavItem[] = [
  {
    title: 'Dashboard',
    url: '/dashboard',
    icon: IconDashboard,
    isActive: true,
  },
  {
    title: 'AGI System',
    url: '/agi',
    icon: IconBrain,
    items: [
      {
        title: 'System Overview',
        url: '/agi/overview',
        icon: IconChartLine,
      },
      {
        title: 'Agent Management',
        url: '/agi/agents',
        icon: IconRobot,
      },
      {
        title: 'Context7 Integration',
        url: '/agi/context7',
        icon: IconCode,
      },
      {
        title: 'Performance Metrics',
        url: '/agi/metrics',
        icon: IconChartPie,
      },
    ],
  },
  {
    title: 'Trading',
    url: '/trading',
    icon: IconChartLine,
    items: [
      {
        title: 'Market Overview',
        url: '/trading/overview',
        icon: IconTarget,
      },
      {
        title: 'Portfolio',
        url: '/trading/portfolio',
        icon: IconWallet,
      },
      {
        title: 'Strategies',
        url: '/trading/strategies',
        icon: IconBulb,
      },
      {
        title: 'Risk Management',
        url: '/trading/risk',
        icon: IconShield,
      },
    ],
  },
  {
    title: 'Data Sources',
    url: '/data',
    icon: IconDatabase,
    items: [
      {
        title: 'Market Data',
        url: '/data/market',
        icon: IconChartLine,
      },
      {
        title: 'Blockchain',
        url: '/data/blockchain',
        icon: IconCloud,
      },
      {
        title: 'APIs',
        url: '/data/apis',
        icon: IconAdjustments,
      },
    ],
  },
  {
    title: 'Files',
    url: '/files',
    icon: IconFiles,
  },
  {
    title: 'Users',
    url: '/users',
    icon: IconUsers,
  },
  {
    title: 'Products',
    url: '/products',
    icon: IconPackages,
  },
  {
    title: 'Settings',
    url: '/settings',
    icon: IconSettings,
  },
];

// Additional navigation items for different sections
export const adminNavItems: NavItem[] = [
  {
    title: 'System Admin',
    url: '/admin',
    icon: IconShield,
    items: [
      {
        title: 'System Health',
        url: '/admin/health',
        icon: IconChartLine,
      },
      {
        title: 'User Management',
        url: '/admin/users',
        icon: IconUsers,
      },
      {
        title: 'Configuration',
        url: '/admin/config',
        icon: IconSettings,
      },
    ],
  },
];

export const quickActions = [
  {
    title: 'New Agent',
    url: '/agi/agents/new',
    icon: IconRobot,
  },
  {
    title: 'Market Analysis',
    url: '/trading/analysis',
    icon: IconChartLine,
  },
  {
    title: 'System Status',
    url: '/agi/status',
    icon: IconBrain,
  },
];

// Breadcrumb mapping for custom titles
export const breadcrumbTitles: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/agi': 'AGI System',
  '/agi/overview': 'System Overview',
  '/agi/agents': 'Agent Management',
  '/agi/context7': 'Context7 Integration',
  '/agi/metrics': 'Performance Metrics',
  '/trading': 'Trading',
  '/trading/overview': 'Market Overview',
  '/trading/portfolio': 'Portfolio',
  '/trading/strategies': 'Strategies',
  '/trading/risk': 'Risk Management',
  '/data': 'Data Sources',
  '/data/market': 'Market Data',
  '/data/blockchain': 'Blockchain',
  '/data/apis': 'APIs',
  '/files': 'Files',
  '/users': 'Users',
  '/products': 'Products',
  '/settings': 'Settings',
};

// Status indicators
export const systemStatus = {
  healthy: { color: 'green', label: 'Healthy' },
  warning: { color: 'yellow', label: 'Warning' },
  error: { color: 'red', label: 'Error' },
  offline: { color: 'gray', label: 'Offline' },
};

// Component configurations
export const componentConfig = {
  sidebar: {
    width: 280,
    collapsedWidth: 80,
  },
  header: {
    height: 60,
  },
  footer: {
    height: 40,
  },
};
