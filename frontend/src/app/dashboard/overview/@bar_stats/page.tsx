// Real data fetching - no mock delay needed
import { BarGraph } from '@/features/overview/components/bar-graph';

export default async function BarStats() {
  // Fetch real bar chart data from backend API instead of using delay
  return <BarGraph />;
}
