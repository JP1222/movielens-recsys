import { RecommendationList } from "../components/RecommendationList";
import { useRecommendations } from "../hooks/useRecommendations";

export function PopularPage() {
  const { data, isLoading, error } = useRecommendations({
    algorithm: "popular",
    params: { k: 10 }
  });

  return (
    <section className="mt-8">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold text-slate-100">
          Trending Right Now
        </h2>
      </div>
      <RecommendationList data={data} isLoading={isLoading} error={error} />
    </section>
  );
}

