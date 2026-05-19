/**
 * Build a PolicyEngine household-situation dict for the RI CTC reform.
 *
 * The situation is consumed by ``POST /us/calculate``. Variables to
 * read back from the simulation appear as ``null`` keys at the
 * appropriate entity level (person / tax_unit / household).
 *
 * For the income-sweep chart we request a single-axis sweep of
 * ``employment_income`` on the head, 0 → 500 000 across 101 points.
 * The /us/calculate response then returns vectors of every requested
 * variable across the sweep.
 */
import type { HouseholdRequest } from './types';

const SWEEP_POINTS = 101;
const SWEEP_MAX = 500_000;

interface PEPerson {
  age: Record<string, number>;
  is_tax_unit_head?: Record<string, boolean>;
  is_tax_unit_spouse?: Record<string, boolean>;
  is_tax_unit_dependent?: Record<string, boolean>;
  employment_income?: Record<string, number>;
}

interface PETaxUnit {
  members: string[];
  filing_status?: Record<string, string>;
}

interface PEHousehold {
  members: string[];
  state_code: Record<string, string>;
  household_net_income?: Record<string, number | null>;
}

export interface PESituation {
  people: Record<string, PEPerson>;
  tax_units: Record<string, PETaxUnit>;
  households: Record<string, PEHousehold>;
  axes?: Array<
    Array<{
      name: string;
      period: string;
      min: number;
      max: number;
      count: number;
      target?: string;
    }>
  >;
}

/**
 * Build the situation for an income sweep (used by the household chart).
 * The head's ``employment_income`` is set as the sweep axis; the
 * response will contain N-point vectors for every requested variable.
 */
export function buildHouseholdSituation(req: HouseholdRequest): PESituation {
  const year = String(req.year);
  const people: Record<string, PEPerson> = {
    you: {
      age: { [year]: req.age_head },
      is_tax_unit_head: { [year]: true },
      // employment_income overridden by the axis below; placeholder of 0
      // so PolicyEngine sees it as a known input.
      employment_income: { [year]: 0 },
    },
  };
  const taxUnitMembers: string[] = ['you'];
  const householdMembers: string[] = ['you'];

  if (req.age_spouse !== null && req.age_spouse !== undefined) {
    people.spouse = {
      age: { [year]: req.age_spouse },
      is_tax_unit_spouse: { [year]: true },
    };
    taxUnitMembers.push('spouse');
    householdMembers.push('spouse');
  }

  req.dependent_ages.forEach((age, i) => {
    const id = `dependent_${i + 1}`;
    people[id] = {
      age: { [year]: age },
      is_tax_unit_dependent: { [year]: true },
    };
    taxUnitMembers.push(id);
    householdMembers.push(id);
  });

  const filingStatus = req.age_spouse !== null ? 'JOINT' : 'SINGLE';

  return {
    people,
    tax_units: {
      'your tax unit': {
        members: taxUnitMembers,
        filing_status: { [year]: filingStatus },
      },
    },
    households: {
      'your household': {
        members: householdMembers,
        state_code: { [year]: 'RI' },
        household_net_income: { [year]: null },
      },
    },
    axes: [
      [
        {
          name: 'employment_income',
          period: year,
          min: 0,
          max: SWEEP_MAX,
          count: SWEEP_POINTS,
          target: 'person',
        },
      ],
    ],
  };
}

export const HOUSEHOLD_SWEEP_MAX = SWEEP_MAX;
export const HOUSEHOLD_SWEEP_POINTS = SWEEP_POINTS;
