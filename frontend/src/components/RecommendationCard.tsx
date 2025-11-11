import type { Recommendation } from "../hooks/useRecommendations";
import { usePosterImage } from "../hooks/usePosterImage";

type Props = {
  item: Recommendation;
};

export function RecommendationCard({ item }: Props) {
  const { posterUrl, isPosterLoading } = usePosterImage(item.title);

  return (
    <article className="flex h-full flex-col rounded-lg border border-slate-800/80 bg-slate-900/80 p-3 shadow-md shadow-slate-950/30 transition hover:-translate-y-0.5 hover:shadow-lg">
      <div
        className="mb-2 w-full overflow-hidden rounded-md border border-slate-800/60 bg-slate-950/40"
        style={{ aspectRatio: "3 / 4" }}
      >
        {posterUrl ? (
          <img
            src={posterUrl}
            alt={`${item.title} poster`}
            loading="lazy"
            className="h-full w-full object-cover"
          />
        ) : (
          <div className="flex h-full items-center justify-center text-center text-xs text-slate-500">
            {isPosterLoading ? "Loading artwork…" : "Poster unavailable"}
          </div>
        )}
      </div>
      <header>
        <h3 className="text-base font-semibold text-emerald-400">{item.title}</h3>
        <p className="text-[11px] uppercase tracking-wide text-slate-400">
          {item.genres.join(" · ") || "Unknown Genre"}
        </p>
      </header>
      <p className="mt-2 flex-1 text-xs text-slate-300">{item.reason}</p>
      <footer className="mt-3 flex items-center justify-between text-[11px] text-slate-400">
        <span>Score {item.score.toFixed(3)}</span>
        <span className="rounded bg-slate-800 px-2 py-0.5 text-[10px] uppercase tracking-wide text-slate-300">
          {item.source}
        </span>
      </footer>
    </article>
  );
}
