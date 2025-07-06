// Real data fetching - no mock delay needed
import { AreaGraph } from '@/features/overview/components/area-graph';

export default async function AreaStats() {
  // Fetch real area chart data from backend API instead of using delay
  return <AreaGraph />;
}
