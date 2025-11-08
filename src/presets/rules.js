/**
 * Predefined Life-like cellular automata rules.
 * Format: { name: string, born: number[], survive: number[] }
 * 
 * Notation: "B{born}/S{survive}" where numbers indicate neighbor counts.
 * Example: "B3/S23" means born with 3 neighbors, survive with 2 or 3 neighbors.
 */

// === Hall of Fame: Top memory rules (validated through extreme search) ===
export const HOF_RULES = [
  { name: "🏆 Seed_1.88a (B2456/S078)", born: [2, 4, 5, 6], survive: [0, 7, 8] },
  { name: "🏆 Seed_1.88b (B2456/S068)", born: [2, 4, 5, 6], survive: [0, 6, 8] },
  { name: "🏆 Evo B246/S58", born: [2, 4, 6], survive: [5, 8] },
  { name: "🏆 Evo B2456/S07", born: [2, 4, 5, 6], survive: [0, 7] },
  { name: "🏆 Evo B246/S5", born: [2, 4, 6], survive: [5] },
  { name: "🏆 Mythmaker_1 (B2456/S5)", born: [2, 4, 5, 6], survive: [5] },
  { name: "🏆 Mythmaker_2 (B01/S3)", born: [0, 1], survive: [3] }
];

// === Memory Candidates: Validated through AutoScan multi-noise testing ===
// These rules show excellent recall (≥70%) across multiple noise levels
export const MEMORY_HALL_OF_FAME = [
  'B01/S3',    // Mythmaker_2 - Champion (~96% recall)
  'B01/S23',   // Variant with Conway survive
  'B01/S34',   // Extended survive range
  'B01/S2',    // Minimal survive
  'B01/S4',    // Single survive
  'B01/S13',   // Low survive
  'B46/S58'    // High-birth variant
];

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
  // --- Promoted discovered rules (auto-selected, high-scoring complex/oscillating) ---
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
    name: "Mythmaker_3 (B018/S)",
    born: [0, 1, 8],
    survive: []
  },
  {
    name: "Mythmaker_4 (B0167/S)",
    born: [0, 1, 6, 7],
    survive: []
  },
  {
    name: "Mythmaker_5 (B0345/S8)",
    born: [0, 3, 4, 5],
    survive: [8]
  },
  {
    name: "Mythmaker_6 (B1245/S)",
    born: [1, 2, 4, 5],
    survive: []
  },
  {
    name: "Mythmaker_7 (B0124/S156)",
    born: [0, 1, 2, 4],
    survive: [1, 5, 6]
  },
  {
    name: "Mythmaker_8 (B238/S37)",
    born: [2, 3, 8],
    survive: [3, 7]
  },
  {
    name: "Mahee_1 (B28/S13478)",
    born: [2, 8],
    survive: [1, 3, 4, 7, 8]
  },
  {
    name: "Mahee_2 (B1234/S)",
    born: [1, 2, 3, 4],
    survive: []
  },
  {
    name: "Mahee_3 (B34/S348)",
    born: [3, 4],
    survive: [3, 4, 8]
  },
  {
    name: "Mahee_4 (B015/S)",
    born: [0, 1, 5],
    survive: []
  },
  {
    name: "Mahee_5 (B123/S)",
    born: [1, 2, 3],
    survive: []
  },
  {
    name: "Mahee_6 (B0246/S1)",
    born: [0, 2, 4, 6],
    survive: [1]
  },
  {
    name: "Tommy_1 (B0267/S)",
    born: [0, 2, 6, 7],
    survive: []
  },
  {
    name: "Tommy_2 (B127/S18)",
    born: [1, 2, 7],
    survive: [1, 8]
  },
  {
    name: "Tommy_3 (B2358/S3)",
    born: [2, 3, 5, 8],
    survive: [3]
  },
  {
    name: "Tommy_4 (B0358/S3)",
    born: [0, 3, 5, 8],
    survive: [3]
  },
  {
    name: "Tommy_5 (B1247/S)",
    born: [1, 2, 4, 7],
    survive: []
  },
  {
    name: "Discovery_1 (B03/S23)",
    born: [0, 3],
    survive: [2, 3]
  },
  {
    name: "Discovery_2 (B3478/S0456)",
    born: [3, 4, 7, 8],
    survive: [0, 4, 5, 6]
  },
  {
    name: "Discovery_3 (B02/S)",
    born: [0, 2],
    survive: []
  },
  {
    name: "Discovery_4 (B0128/S37)",
    born: [0, 1, 2, 8],
    survive: [3, 7]
  },
  {
    name: "Discovery_5 (B345/S45)",
    born: [3, 4, 5],
    survive: [4, 5]
  },
  {
    name: "Discovery_6 (B12/S02)",
    born: [1, 2],
    survive: [0, 2]
  },
  {
    name: "Discovery_7 (B0467/S)",
    born: [0, 4, 6, 7],
    survive: []
  },
  {
    name: "Discovery_8 (B24/S3)",
    born: [2, 4],
    survive: [3]
  },
  {
    name: "Discovery_9 (B3568/S458)",
    born: [3, 5, 6, 8],
    survive: [4, 5, 8]
  },
  {
    name: "Discovery_10 (B01234/S)",
    born: [0, 1, 2, 3, 4],
    survive: []
  },
  {
    name: "Explorer_1 (B4567/S456)",
    born: [4, 5, 6, 7],
    survive: [4, 5, 6]
  },
  {
    name: "Explorer_2 (B37/S238)",
    born: [3, 7],
    survive: [2, 3, 8]
  },
  {
    name: "Explorer_3 (B025/S1)",
    born: [0, 2, 5],
    survive: [1]
  },
  {
    name: "Explorer_4 (B1356/S24)",
    born: [1, 3, 5, 6],
    survive: [2, 4]
  },
  {
    name: "Explorer_5 (B268/S35)",
    born: [2, 6, 8],
    survive: [3, 5]
  },
  {
    name: "Explorer_6 (B0137/S2)",
    born: [0, 1, 3, 7],
    survive: [2]
  },
  {
    name: "Explorer_7 (B458/S23)",
    born: [4, 5, 8],
    survive: [2, 3]
  },
  {
    name: "Explorer_8 (B01568/S)",
    born: [0, 1, 5, 6, 8],
    survive: []
  },
  {
    name: "Explorer_9 (B2467/S34)",
    born: [2, 4, 6, 7],
    survive: [3, 4]
  },
  {
    name: "Explorer_10 (B013/S12)",
    born: [0, 1, 3],
    survive: [1, 2]
  },
  {
    name: "Variant_1 (B36/S125)",
    born: [3, 6],
    survive: [1, 2, 5]
  },
  {
    name: "Variant_2 (B2378/S)",
    born: [2, 3, 7, 8],
    survive: []
  },
  {
    name: "Variant_3 (B048/S1238)",
    born: [0, 4, 8],
    survive: [1, 2, 3, 8]
  },
  {
    name: "Variant_4 (B135/S234)",
    born: [1, 3, 5],
    survive: [2, 3, 4]
  },
  {
    name: "Variant_5 (B0246/S)",
    born: [0, 2, 4, 6],
    survive: []
  }
];

