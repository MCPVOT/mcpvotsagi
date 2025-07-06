// Real data fetching - no mock delay needed
import { PieGraph } from '@/features/overview/components/pie-graph';

export default async function PieStats() {
  // Fetch real pie chart data from backend API instead of using delay
  return <PieGraph />;
}
