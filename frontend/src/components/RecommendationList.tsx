import { RecommendationCard } from "./RecommendationCard";
import type { Recommendation } from "../hooks/useRecommendations";

type RecommendationListProps = {
  data: Recommendation[] | undefined;
  isLoading: boolean;
  error: string | null;
};

export function RecommendationList({
  data,
  isLoading,
  error
}: RecommendationListProps) {
  if (isLoading) {
    return (
      <div className="mt-6 rounded-md border border-slate-800 bg-slate-900 p-6 text-slate-400">
        Loading recommendations...
      </div>
    );
  }

  if (error) {
    return (
      <div className="mt-6 rounded-md border border-rose-600/40 bg-rose-900/30 p-6 text-rose-300">
        {error}
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="mt-6 rounded-md border border-slate-800 bg-slate-900 p-6 text-slate-400">
        No recommendations available. Try a different user or adjust filters.
      </div>
    );
  }

  return (
    <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {data.map((item) => (
        <RecommendationCard key={item.movie_id} item={item} />
      ))}
    </div>
  );
}
