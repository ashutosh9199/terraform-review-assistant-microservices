export type Scorecard = {
  overall_score: number;
  security_score: number;
  cost_score: number;
  governance_score: number;
  operations_score: number;
  terraform_quality_score: number;
  reasoning: Record<string, string[]>;
};

export type Finding = {
  id: number;
  source: string;
  category: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  resource_address?: string;
  title: string;
  description: string;
  recommendation: string;
  business_impact?: string;
  terraform_fix?: string;
  confidence: number;
};

export type Review = {
  id: number;
  project_id: number;
  status: string;
  original_filename: string;
  created_at: string;
  completed_at?: string;
  error_message?: string;
  inventory?: {
    files: string[];
    resource_count: number;
    resources: Array<Record<string, unknown>>;
    diagnostics: Array<Record<string, string>>;
  };
  dependency_graph?: Record<string, unknown>;
  scorecard?: Scorecard;
  findings: Finding[];
};

export type Project = {
  id: number;
  name: string;
  description?: string;
  created_at: string;
};

export type DashboardSummary = {
  total_reviews: number;
  average_score: number;
  security_average: number;
  cost_average: number;
  governance_average: number;
  operations_average: number;
  security_trend: Array<{ label: string; score: number }>;
  cost_trend: Array<{ label: string; score: number }>;
  recent_reviews: Array<{
    id: number;
    filename: string;
    status: string;
    created_at: string;
    score?: number;
  }>;
};

export type LlmSettings = {
  provider: string;
  endpoint?: string;
  model?: string;
  has_api_key: boolean;
  updated_at?: string;
};
