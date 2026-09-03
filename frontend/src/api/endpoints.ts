import { apiRequest } from "./client";
import type {
  ArchiveEntry,
  DailyChallenge,
  DailyResult,
  GameMode,
  GuessResponse,
  MeInfo,
  SearchItem,
  Theme,
} from "./types";

// "lives" é o padrão do backend, então só mandamos o parâmetro quando for infinito
function modeParam(mode: GameMode | undefined) {
  return mode === "infinite" ? { mode } : {};
}

export function fetchThemes(): Promise<Theme[]> {
  return apiRequest<Theme[]>("/themes");
}

export function fetchDaily(
  themeSlug: string,
  date?: string,
  mode?: GameMode,
): Promise<DailyChallenge> {
  return apiRequest<DailyChallenge>("/daily", {
    params: { theme: themeSlug, date, ...modeParam(mode) },
  });
}

export function searchItems(challengeId: number, q: string, limit?: number): Promise<SearchItem[]> {
  return apiRequest<SearchItem[]>(`/daily/${challengeId}/search`, { params: { q, limit } });
}

export function submitGuess(
  challengeId: number,
  itemId: number,
  mode?: GameMode,
): Promise<GuessResponse> {
  return apiRequest<GuessResponse>(`/daily/${challengeId}/guess`, {
    method: "POST",
    params: modeParam(mode),
    body: { item_id: itemId },
  });
}

export function giveUp(challengeId: number): Promise<DailyChallenge> {
  return apiRequest<DailyChallenge>(`/daily/${challengeId}/giveup`, {
    method: "POST",
    params: { mode: "infinite" },
  });
}

export function fetchResult(challengeId: number, mode?: GameMode): Promise<DailyResult> {
  return apiRequest<DailyResult>(`/daily/${challengeId}/result`, { params: modeParam(mode) });
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
