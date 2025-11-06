import { useState } from "react";
import { ForYouPage } from "./pages/ForYouPage";
import { PopularPage } from "./pages/PopularPage";
import { TitleSearchPanel } from "./components/TitleSearchPanel";

const tabs = [
  { id: "popular", label: "Popular" },
  { id: "personal", label: "For You" }
];

export default function App() {
  const [activeTab, setActiveTab] = useState<string>("popular");

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="bg-slate-900 border-b border-slate-800">
        <div className="mx-auto max-w-5xl px-6 py-6">
          <h1 className="text-3xl font-semibold">MovieLens Recommender</h1>
          <p className="text-slate-400">
            Explore popular titles and get personalized movie recommendations.
          </p>
          <div className="mt-6 flex gap-4">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                className={`rounded px-4 py-2 text-sm font-medium transition ${
                  activeTab === tab.id
                    ? "bg-emerald-500 text-slate-900"
                    : "bg-slate-800 text-slate-300 hover:bg-slate-700"
                }`}
                onClick={() => setActiveTab(tab.id)}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-6 py-8">
        <TitleSearchPanel />
        {activeTab === "popular" ? <PopularPage /> : <ForYouPage />}
      </main>
    </div>
  );
}

