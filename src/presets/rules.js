/**
 * Predefined Life-like cellular automata rules.
 * Format: { name: string, born: number[], survive: number[] }
 * 
 * Notation: "B{born}/S{survive}" where numbers indicate neighbor counts.
 * Example: "B3/S23" means born with 3 neighbors, survive with 2 or 3 neighbors.
 */

export const RULES = [
  {
    name: "Conway's Life (B3/S23)",
    born: [3],
    survive: [2, 3]
  },
  {
    name: "HighLife (B36/S23)",
    born: [3, 6],
    survive: [2, 3]
  },
  {
    name: "Day & Night (B3678/S34678)",
    born: [3, 6, 7, 8],
    survive: [3, 4, 6, 7, 8]
  },
  {
    name: "Seeds (B2/S)",
    born: [2],
    survive: []
  },
  {
    name: "Replicator (B1357/S1357)",
    born: [1, 3, 5, 7],
    survive: [1, 3, 5, 7]
  }
];

