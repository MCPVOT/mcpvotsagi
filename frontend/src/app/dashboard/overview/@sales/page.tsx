// Real data fetching - no mock delay needed
import { RecentSales } from '@/features/overview/components/recent-sales';

export default async function Sales() {
  // Fetch real sales data from backend API instead of using delay
  return <RecentSales />;
}
