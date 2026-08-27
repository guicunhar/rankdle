/** Portuguese ordinal for a ranking position (e.g. 34 -> "34ª"), matching "a Xª posição". */
export function ordinal(n: number): string {
  return `${n}ª`;
}
