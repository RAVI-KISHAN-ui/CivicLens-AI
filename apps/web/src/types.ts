export type IssueType =
  | "VAGUE_LINK_TEXT"
  | "UNCLEAR_INSTRUCTION"
  | "JARGON_OR_COMPLEX_LANGUAGE"
  | "INFO_SCATTERED_ACROSS_PAGES"
  | "KEY_INFO_ONLY_IN_PDF"
  | "MISSING_ACCESSIBLE_NAME"
  | "LOW_CONTRAST"
  | "SMALL_TOUCH_TARGET"
  | "NO_LANGUAGE_OPTION"
  | "BROKEN_LINK"
  | "SLOW_ON_MOBILE"
  | "DEEP_NAVIGATION"
  | "NEW_WINDOW_UNANNOUNCED"
  | "OTHER_AXE_RULE";

export interface GateResult {
  gate: string;
  passed: boolean;
  hard: boolean;
  detail: string;
}

export interface Finding {
  id: string;
  scan_id: string;
  source: "axe" | "rule" | "llm";
  issue_type: IssueType;
  evidence_ids: string[];
  quoted_text: string;
  wcag_sc?: string | null;
  gigw_ref?: string | null;
  who_is_affected: string;
  citizen_impact: string;
  suggested_fix: string;
  severity: "blocker" | "major" | "minor";
  on_task_path: boolean;
  status: "verified" | "needs_review" | "rejected";
  gates: GateResult[];
  review: "unreviewed" | "accepted" | "dismissed";
}

export interface Evidence {
  id: string;
  scan_id: string;
  page_id: string;
  page_url: string;
  device: "desktop" | "mobile";
  kind: string;
  selector?: string | null;
  role?: string | null;
  accessible_name?: string | null;
  text: string;
  context: string;
  href?: string | null;
  bbox?: [number, number, number, number] | null;
  crop_path?: string | null;
  axe_rule_id?: string | null;
  wcag_tags: string[];
  dom_snapshot_hash: string;
}

export interface CitedFact {
  id: string;
  field: "eligibility" | "document" | "apply_link" | "deadline" | "contact" | "amount";
  value: string;
  source_url: string;
  evidence_ids: string[];
  cited_text: string;
  human_checked: boolean;
}

export interface TaskMetrics {
  clicks_to_answer: number;
  pages_visited: number;
  pdf_hops: number;
  distinct_domains: number;
  time_to_answer_ms: number;
  words_on_path: number;
  bytes_transferred: number;
}

export interface Scan {
  id: string;
  task_id: string;
  url: string;
  status: "running" | "completed" | "failed";
  total_candidates: number;
  verified_count: number;
  needs_review_count: number;
  rejected_count: number;
  metrics_original?: TaskMetrics | null;
  metrics_prototype?: TaskMetrics | null;
  error_message?: string | null;
}
