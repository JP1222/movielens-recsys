import { useEffect, useState } from "react";

type PosterState = {
  posterUrl: string | null;
  isPosterLoading: boolean;
  posterError: string | null;
};

const TMDB_API_BASE = "https://api.themoviedb.org/3";
const TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w342";

/**
 * Fetch a movie poster from TMDB given a title. The request prefers the bearer
 * token, but falls back to the API key if that is the only credential provided.
 */
export function usePosterImage(title: string | undefined): PosterState {
  const [posterUrl, setPosterUrl] = useState<string | null>(null);
  const [isPosterLoading, setIsPosterLoading] = useState<boolean>(false);
  const [posterError, setPosterError] = useState<string | null>(null);

  useEffect(() => {
    const bearerToken = import.meta.env.VITE_TMDB_BEARER_TOKEN as string | undefined;
    const apiKey = import.meta.env.VITE_TMDB_API_KEY as string | undefined;

    if (!title?.trim() || (!bearerToken && !apiKey)) {
      setPosterUrl(null);
      setPosterError(null);
      setIsPosterLoading(false);
      return;
    }

    const controller = new AbortController();

    async function fetchPoster() {
      setIsPosterLoading(true);
      setPosterError(null);

      try {
        const params = new URLSearchParams({
          query: title,
          include_adult: "false",
          language: "en-US",
          page: "1"
        });
        let url = `${TMDB_API_BASE}/search/movie?${params.toString()}`;
        const headers: Record<string, string> = {
          "Content-Type": "application/json;charset=utf-8"
        };
        const init: RequestInit = {
          signal: controller.signal,
          headers
        };

        if (bearerToken) {
          headers.Authorization = `Bearer ${bearerToken}`;
        } else if (apiKey) {
          url += `&api_key=${apiKey}`;
        }

        const response = await fetch(url, init);
        if (!response.ok) {
          throw new Error(`TMDB request failed (${response.status})`);
        }

        const data: { results?: Array<{ poster_path?: string | null }> } = await response.json();
        const posterPath = data.results?.[0]?.poster_path;
        setPosterUrl(posterPath ? `${TMDB_IMAGE_BASE}${posterPath}` : null);
      } catch (error) {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }
        const message = error instanceof Error ? error.message : "Unable to load poster";
        setPosterError(message);
        setPosterUrl(null);
      } finally {
        setIsPosterLoading(false);
      }
    }

    fetchPoster();
    return () => controller.abort();
  }, [title]);

  return { posterUrl, isPosterLoading, posterError };
}
