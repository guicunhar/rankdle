/** Converts an ISO date ("YYYY-MM-DD", as used by the API/URLs) to "DD/MM/AAAA" for display. */
export function formatDateBR(isoDate: string): string {
  const [year, month, day] = isoDate.split("-");
  return `${day}/${month}/${year}`;
}
