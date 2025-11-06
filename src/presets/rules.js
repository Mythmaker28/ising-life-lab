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
  },
  {
    name: "Mythmaker (B345/S346)",
    born: [3, 4, 5],
    survive: [3, 4, 6]
  },
  {
    name: "Mahee (B3678/S23678)",
    born: [3, 6, 7, 8],
    survive: [2, 3, 6, 7, 8]
  },
  {
    name: "Tommy (B3457/S3456)",
    born: [3, 4, 5, 7],
    survive: [3, 4, 5, 6]
  },
  // --- Promoted discovered rules (auto-selected from Rule Explorer) ---
  {
    name: "Mythmaker_1 (B2456/S5)",
    born: [2, 4, 5, 6],
    survive: [5]
  },
  {
    name: "Mythmaker_2 (B01/S3)",
    born: [0, 1],
    survive: [3]
  },
  {
    name: "Mahee_1 (B0345/S8)",
    born: [0, 3, 4, 5],
    survive: [8]
  },
  {
    name: "Tommy_1 (B1245/S)",
    born: [1, 2, 4, 5],
    survive: []
  },
  {
    name: "Tommy_2 (B018/S)",
    born: [0, 1, 8],
    survive: []
  }
];

