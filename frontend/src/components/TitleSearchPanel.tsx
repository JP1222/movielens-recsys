import { FormEvent, useState } from "react";
import { RecommendationList } from "./RecommendationList";
import { useRecommendations } from "../hooks/useRecommendations";

export function TitleSearchPanel() {
  const [titles, setTitles] = useState<string>("");
  const [submittedTitles, setSubmittedTitles] = useState<string[]>([]);
  const { data, isLoading, error, refetch } = useRecommendations({
    algorithm: "byTitles",
    params: { titles: submittedTitles },
    method: "POST",
    enabled: submittedTitles.length > 0
  });

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    const processed = titles
      .split(",")
      .map((title) => title.trim())
      .filter(Boolean);
    setSubmittedTitles(processed);
    if (processed.length > 0) {
      refetch();
    }
  };

  return (
    <section className="rounded-lg border border-slate-800 bg-slate-900 p-6 shadow-xl shadow-slate-950/30">
      <h2 className="text-xl font-semibold text-emerald-400">
        Recommend by Movie Titles
      </h2>
      <p className="mt-2 text-sm text-slate-400">
        Provide one or more titles separated by commas to discover similar
        movies.
      </p>
      <form className="mt-4 flex flex-col gap-3 md:flex-row" onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="e.g., Toy Story, Matrix"
          value={titles}
          onChange={(event) => setTitles(event.target.value)}
          className="flex-1 rounded-md border border-slate-700 bg-slate-950 px-4 py-2 text-slate-100"
        />
        <button
          type="submit"
          className="rounded-md bg-emerald-500 px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-emerald-400"
        >
          Recommend
        </button>
      </form>

      {submittedTitles.length > 0 && (
        <div className="mt-4">
          <RecommendationList data={data} isLoading={isLoading} error={error} />
        </div>
      )}
    </section>
  );
}

