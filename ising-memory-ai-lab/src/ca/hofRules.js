/**
 * Hall of Fame Rules - Top memory rules from ising-life-lab
 * Based on extreme search results (10k+ rules tested)
 */

export const HOF_RULES = [
  {
    id: 'seed_1_88a',
    name: 'Seed_1.88a',
    notation: 'B2456/S078',
    born: [2, 4, 5, 6],
    survive: [0, 7, 8],
    memoryScore: 0.847,
    complexity: 'high',
    discovered: '2024-12'
  },
  {
    id: 'seed_1_88b',
    name: 'Seed_1.88b',
    notation: 'B2456/S068',
    born: [2, 4, 5, 6],
    survive: [0, 6, 8],
    memoryScore: 0.823,
    complexity: 'high',
    discovered: '2024-12'
  },
  {
    id: 'evo_b246_s58',
    name: 'Evo B246/S58',
    notation: 'B246/S58',
    born: [2, 4, 6],
    survive: [5, 8],
    memoryScore: 0.792,
    complexity: 'medium',
    discovered: '2024-12'
  },
  {
    id: 'evo_b2456_s07',
    name: 'Evo B2456/S07',
    notation: 'B2456/S07',
    born: [2, 4, 5, 6],
    survive: [0, 7],
    memoryScore: 0.778,
    complexity: 'medium',
    discovered: '2024-12'
  },
  {
    id: 'evo_b246_s5',
    name: 'Evo B246/S5',
    notation: 'B246/S5',
    born: [2, 4, 6],
    survive: [5],
    memoryScore: 0.765,
    complexity: 'medium',
    discovered: '2024-12'
  },
  {
    id: 'mythmaker_1',
    name: 'Mythmaker_1',
    notation: 'B2456/S5',
    born: [2, 4, 5, 6],
    survive: [5],
    memoryScore: 0.742,
    complexity: 'low',
    discovered: '2024-11'
  },
  {
    id: 'mythmaker_2',
    name: 'Mythmaker_2',
    notation: 'B01/S3',
    born: [0, 1],
    survive: [3],
    memoryScore: 0.728,
    complexity: 'medium',
    discovered: '2024-11'
  }
];

export function getRuleByNotation(notation) {
  return HOF_RULES.find(r => r.notation === notation);
}

export function getRuleById(id) {
  return HOF_RULES.find(r => r.id === id);
}




