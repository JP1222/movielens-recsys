import type { Recommendation } from "../hooks/useRecommendations";

type Props = {
  item: Recommendation;
};

export function RecommendationCard({ item }: Props) {
  return (
    <article className="flex h-full flex-col rounded-lg border border-slate-800 bg-slate-900 p-4 shadow-md shadow-slate-950/40 transition hover:-translate-y-1 hover:shadow-lg">
      <header>
        <h3 className="text-lg font-semibold text-emerald-400">{item.title}</h3>
        <p className="text-xs uppercase tracking-wide text-slate-400">
          {item.genres.join(" · ") || "Unknown Genre"}
        </p>
      </header>
      <p className="mt-3 flex-1 text-sm text-slate-300">{item.reason}</p>
      <footer className="mt-4 flex items-center justify-between text-xs text-slate-400">
        <span>Score: {item.score.toFixed(3)}</span>
        <span className="rounded bg-slate-800 px-2 py-1 text-[10px] uppercase tracking-wide text-slate-300">
          {item.source}
        </span>
      </footer>
    </article>
  );
}

