import { useCallback, useEffect, useMemo, useState } from "react";

export type Recommendation = {
  movie_id: number;
  title: string;
  genres: string[];
  score: number;
  source: string;
  reason: string;
};

type UseRecommendationsParams = {
  algorithm: "popular" | "itemcf" | "byTitles";
  params?: Record<string, unknown>;
  method?: "GET" | "POST";
  enabled?: boolean;
};

export function useRecommendations({
  algorithm,
  params = {},
  method = "GET",
  enabled = true
}: UseRecommendationsParams) {
  const [data, setData] = useState<Recommendation[]>();
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const paramsKey = useMemo(
    () => JSON.stringify(params ?? {}),
    [params]
  );

  const buildUrl = useCallback(() => {
    if (method === "GET") {
      const query = new URLSearchParams();
      const parsedParams = JSON.parse(paramsKey) as Record<string, unknown>;
      Object.entries(parsedParams).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          query.set(key, String(value));
        }
      });
      const queryString = query.toString();
      return `/recommend/${algorithm === "byTitles" ? "by-titles" : algorithm}${
        queryString ? `?${queryString}` : ""
      }`;
    }
    return `/recommend/${algorithm === "byTitles" ? "by-titles" : algorithm}`;
  }, [algorithm, method, paramsKey]);

  const fetchData = useCallback(async () => {
    if (!enabled) {
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(buildUrl(), {
        method,
        headers: { "Content-Type": "application/json" },
        body: method === "POST" ? paramsKey : null
      });
      if (!response.ok) {
        const message = await response.text();
        throw new Error(message || "Failed to fetch recommendations");
      }
      const payload = await response.json();
      setData(payload.items ?? []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
      setData(undefined);
    } finally {
      setIsLoading(false);
    }
  }, [buildUrl, enabled, method, paramsKey]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, isLoading, error, refetch: fetchData };
}
