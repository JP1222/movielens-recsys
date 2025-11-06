import { useState } from "react";
import { RecommendationList } from "../components/RecommendationList";
import { useRecommendations } from "../hooks/useRecommendations";

export function ForYouPage() {
  const [userId, setUserId] = useState<number | undefined>(1);
  const { data, isLoading, error, refetch } = useRecommendations({
    algorithm: "itemcf",
    params: { user_id: userId, k: 10 },
    enabled: Boolean(userId)
  });

  return (
    <section className="mt-8">
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-slate-100">
            Personalized Picks
          </h2>
          <p className="text-sm text-slate-400">
            Enter a MovieLens user ID with available history to see tailored
            recommendations.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <input
            type="number"
            min={1}
            value={userId ?? ""}
            onChange={(event) => {
              const value = Number(event.target.value);
              setUserId(Number.isFinite(value) ? value : undefined);
            }}
            className="w-32 rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-slate-100"
            placeholder="User ID"
          />
          <button
            className="rounded bg-emerald-500 px-4 py-2 text-sm font-medium text-slate-900 transition hover:bg-emerald-400"
            onClick={() => refetch()}
            disabled={!userId}
          >
            Refresh
          </button>
        </div>
      </div>
      <RecommendationList data={data} isLoading={isLoading} error={error} />
    </section>
  );
}

