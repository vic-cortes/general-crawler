import {
  ContractType,
  ExperienceLevel,
  JobOffer,
  LanguageLevel,
  WorkMode,
} from '../types';
import rawOffers from './rawOffers.json';

function mapWorkMode(mode: string): WorkMode {
  const map: Record<string, WorkMode> = {
    remote: 'Remote',
    onsite: 'On-site',
    hybrid: 'Hybrid',
  };
  return map[mode] ?? 'On-site';
}

function mapExperienceLevel(years: number): ExperienceLevel {
  if (years <= 1) return 'Junior';
  if (years <= 3) return 'Mid';
  if (years <= 6) return 'Senior';
  if (years <= 9) return 'Lead';
  return 'Staff';
}

function mapContractType(jobType: string): ContractType {
  const normalized = jobType.toLowerCase();
  if (normalized === 'part-time') return 'Part-time';
  if (normalized === 'contract' || normalized === 'internship')
    return 'Contract';
  return 'Full-time';
}

function mapLanguageLevel(level: string): LanguageLevel {
  if (level === 'native') return 'Native';
  return level.toUpperCase() as LanguageLevel;
}

function buildTechStack(tech: Record<string, unknown>): string[] {
  const stack: string[] = [];

  for (const pl of (tech.programming_languages as
    | { name?: string }[]
    | undefined) ?? []) {
    if (pl.name) stack.push(pl.name);
  }

  for (const key of ['cloud', 'frameworks', 'databases', 'big_data'] as const) {
    for (const item of (tech[key] as string[] | undefined) ?? []) {
      if (!stack.includes(item)) stack.push(item);
    }
  }

  return stack;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const REAL_OFFERS: JobOffer[] = (rawOffers as any[]).map((d, i) => {
  const wm = d.work_mode ?? {};
  const sal = wm.salary ?? {};
  const amount: number | null = sal.amount ?? null;

  const languages = (d.foreign_languages ?? [])
    .filter(
      (l: { name?: string; language_proficiency_level?: string }) =>
        l.name && l.language_proficiency_level,
    )
    .map((l: { name: string; language_proficiency_level: string }) => ({
      name: l.name,
      level: mapLanguageLevel(l.language_proficiency_level),
    }));

  return {
    id: String(i + 1),
    title: d.position ?? 'Unknown',
    salaryMin: amount ? Math.round(amount * 0.9) : 0,
    salaryMax: amount ? Math.round(amount * 1.1) : 0,
    salaryCurrency: sal.currency ?? 'MXN',
    workMode: mapWorkMode(wm.mode),
    ...(wm.location ? { location: wm.location } : {}),
    techStack: buildTechStack(d.technologies ?? {}),
    experienceLevel: mapExperienceLevel(
      d.experience_required?.minimum_years ?? 0,
    ),
    contractType: mapContractType(d.job_type?.[0] ?? 'Full-time'),
    benefits: [],
    createdAt: '2026-05-23T10:00:00Z',
    tags: d.experience_required?.areas ?? [],
    sourceName: 'CompuTrabajo',
    sourceUrl: 'https://mx.computrabajo.com',
    ...(languages.length > 0 ? { languages } : {}),
  } satisfies JobOffer;
});
