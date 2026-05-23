
export type WorkMode = 'Remote' | 'Hybrid' | 'On-site';
export type ExperienceLevel = 'Junior' | 'Mid' | 'Senior' | 'Lead' | 'Staff';
export type ContractType = 'Full-time' | 'Contract' | 'Part-time';
export type LanguageLevel = 'A1' | 'A2' | 'B1' | 'B2' | 'C1' | 'C2' | 'Native';

export interface LanguageRequirement {
  name: string;
  level: LanguageLevel;
}

export interface JobOffer {
  id: string;
  title: string;
  salaryMin: number;
  salaryMax: number;
  salaryCurrency: string;
  workMode: WorkMode;
  techStack: string[];
  experienceLevel: ExperienceLevel;
  contractType: ContractType;
  location?: string;
  benefits: string[];
  createdAt: string;
  tags: string[];
  sourceName: string;
  sourceUrl: string;
  languages?: LanguageRequirement[];
}

export interface ComparisonGroup {
  id: string;
  name: string;
  offerIds: string[];
}

export enum AppRoute {
  DASHBOARD = 'dashboard',
  COMPARISON = 'comparison',
  ANALYTICS = 'analytics',
  SETTINGS = 'settings'
}
