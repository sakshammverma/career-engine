/** Typed client for the FastAPI career engine. Mirrors app/models.py. */

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

// ---------- profile ----------
export interface Academic {
  college_tier: number;
  university?: string | null;
  branch?: string | null;
  current_semester: number;
  graduation_year?: number | null;
  cgpa?: number | null;
  backlogs: number;
  attendance_restricted: boolean;
}

export interface CareerGoals {
  target_role: string;
  campus: boolean;
  off_campus: boolean;
  target_salary_lpa?: number | null;
  preferred_companies: string[];
  work_mode?: string | null;
}

export interface LearningConstraints {
  daily_study_hours: number;
  budget: "free_only" | "paid_ok";
  learning_style: "video" | "text" | "interactive" | "project";
}

export interface Experience {
  resume_quality: number;
  github_maturity: number;
  cp_level: number;
  internships: number;
  projects_completed: number;
  open_source_prs: number;
  hackathons: number;
  certifications: number;
}

export interface StudentProfile {
  academic: Academic;
  goals: CareerGoals;
  constraints: LearningConstraints;
  skills: { levels: Record<string, number> };
  experience: Experience;
}

// ---------- engine outputs ----------
export interface SkillGap {
  skill_id: string;
  name: string;
  current_level: number;
  target_level: number;
  weight: number;
  gap_fraction: number;
}

export interface Recommendation {
  skill_id: string;
  name: string;
  reason: string;
  current_level: number;
  target_level: number;
  effort_hours: number;
  blocked_by: string[];
  readiness_gain: number;
}

export interface ReadinessResult {
  role: string;
  readiness_pct: number;
  gaps: SkillGap[];
  recommendations: Recommendation[];
  projected_readiness_pct: number;
  projected_from: string[];
}

export interface RoadmapItem {
  skill_id: string;
  name: string;
  effort_hours: number;
  prerequisites: string[];
  rationale: string;
}

export interface SemesterPlan {
  semester: number;
  theme: string;
  items: RoadmapItem[];
  total_effort_hours: number;
}

export interface Roadmap {
  role: string;
  current_semester: number;
  readiness_pct: number;
  projected_readiness_pct: number;
  semesters: SemesterPlan[];
}

export interface MilestoneStatus {
  id: string;
  name: string;
  category: string;
  relevant_from_semester: number;
  completed: boolean;
  due_now: boolean;
}

export interface MilestoneProgress {
  completion_pct: number;
  completed_count: number;
  total_count: number;
  due_completion_pct: number;
  statuses: MilestoneStatus[];
}

export interface Resource {
  title: string;
  url: string;
  kind: string;
  free: boolean;
  styles: string[];
}

export interface WeeklyPlan {
  week: number;
  semester: number;
  focus_skill_id: string;
  focus_skill: string;
  topics: string;
  estimated_hours: number;
  practice: string;
  project_or_milestone: string;
  revision: string;
  interview_prep?: string | null;
  resources: Resource[];
}

export interface Opportunity {
  id: string;
  name: string;
  kind: string;
  url: string;
  description: string;
  min_semester: number;
  max_semester: number;
  roles: string[];
  required_skills: Record<string, number>;
  min_cp_level: number;
}

export interface OpportunityMatch {
  opportunity: Opportunity;
  eligible: boolean;
  fit_score: number;
  reasons: string[];
  missing: string[];
}

export interface Dashboard {
  student_id: string;
  profile: StudentProfile;
  readiness: ReadinessResult;
  roadmap: Roadmap;
  milestones: MilestoneProgress;
  weekly_plan: WeeklyPlan[];
  opportunities: OpportunityMatch[];
}

export interface MentorReply {
  answer: string;
  mode: "llm" | "offline";
  model?: string | null;
  context: string;
}

export interface RoleGraph {
  role: string;
  name: string;
  requirements: { skill_id: string; target_level: number; weight: number }[];
}

// ---------- fetchers ----------
async function j<T>(res: Response): Promise<T> {
  if (!res.ok) throw new Error(`${res.status}: ${await res.text()}`);
  return res.json() as Promise<T>;
}

export const api = {
  roles: () => fetch(`${API}/roles`).then((r) => j<RoleGraph[]>(r)),

  createStudent: (profile: StudentProfile) =>
    fetch(`${API}/students`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(profile),
    }).then((r) => j<{ student_id: string }>(r)),

  dashboard: (id: string) =>
    fetch(`${API}/students/${id}/dashboard`).then((r) => j<Dashboard>(r)),

  setSkill: (id: string, skill: string, level: number) =>
    fetch(`${API}/students/${id}/skills/${skill}`, {
      method: "PATCH",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ level }),
    }).then((r) => j<Dashboard>(r)),

  setMilestone: (id: string, milestone: string, done: boolean) =>
    fetch(`${API}/students/${id}/milestones/${milestone}`, {
      method: "PATCH",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ done }),
    }).then((r) => j<Dashboard>(r)),

  advanceSemester: (id: string) =>
    fetch(`${API}/students/${id}/advance-semester`, { method: "POST" }).then(
      (r) => j<Dashboard>(r),
    ),

  askMentor: (id: string, question: string) =>
    fetch(`${API}/students/${id}/mentor`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ question }),
    }).then((r) => j<MentorReply>(r)),
};

export const STUDENT_KEY = "career_student_id";
