import { apiRequest } from "./client";
import type {
  ArchiveEntry,
  DailyChallenge,
  DailyResult,
  GuessResponse,
  MeInfo,
  SearchItem,
  Theme,
} from "./types";

export function fetchThemes(): Promise<Theme[]> {
  return apiRequest<Theme[]>("/themes");
}

export function fetchDaily(themeSlug: string, date?: string): Promise<DailyChallenge> {
  return apiRequest<DailyChallenge>("/daily", { params: { theme: themeSlug, date } });
}

export function searchItems(challengeId: number, q: string, limit?: number): Promise<SearchItem[]> {
  return apiRequest<SearchItem[]>(`/daily/${challengeId}/search`, { params: { q, limit } });
}

export function submitGuess(challengeId: number, itemId: number): Promise<GuessResponse> {
  return apiRequest<GuessResponse>(`/daily/${challengeId}/guess`, {
    method: "POST",
    body: { item_id: itemId },
  });
}

export function fetchResult(challengeId: number): Promise<DailyResult> {
  return apiRequest<DailyResult>(`/daily/${challengeId}/result`);
}

export function fetchArchive(themeSlug: string): Promise<ArchiveEntry[]> {
  return apiRequest<ArchiveEntry[]>("/archive", { params: { theme: themeSlug } });
}

export function fetchMe(): Promise<MeInfo> {
  return apiRequest<MeInfo>("/auth/me");
}

export function register(email: string, password: string, deviceId: string): Promise<{ access_token: string }> {
  return apiRequest("/auth/register", {
    method: "POST",
    body: { email, password, device_id: deviceId },
    skipAuth: true,
  });
}

export function login(email: string, password: string): Promise<{ access_token: string }> {
  return apiRequest("/auth/login", { method: "POST", body: { email, password }, skipAuth: true });
}

export function upgradeGuest(
  deviceId: string,
  email: string,
  password: string,
): Promise<{ access_token: string }> {
  return apiRequest("/auth/upgrade-guest", {
    method: "POST",
    body: { device_id: deviceId, email, password },
    skipAuth: true,
  });
}
