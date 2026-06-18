import { Card, CardContent, Step, StepLabel, Stepper, Typography } from '@mui/material';

// Mirrors STAGE_ORDER / STAGE_LABELS in apps/api-gateway/app/services/stages.py.
// AI agent stages are listed individually so the user can see exactly which
// specialist (or the executive synthesis agent) is currently running.
const STAGES: Array<{ key: string; label: string }> = [
  { key: 'fetching_files', label: 'Loading files' },
  { key: 'parsing', label: 'Parsing Terraform' },
  { key: 'evaluating_rules', label: 'Rule engine' },
  { key: 'ai_security', label: 'AI: Security Reviewer' },
  { key: 'ai_cost', label: 'AI: Cost Reviewer' },
  { key: 'ai_governance', label: 'AI: Governance Reviewer' },
  { key: 'ai_operations', label: 'AI: Operations Reviewer' },
  { key: 'scoring', label: 'Scoring' },
  { key: 'synthesizing', label: 'AI: Executive Reviewer' },
  { key: 'reporting', label: 'Generating reports' }
];

type Props = {
  status: string;
  currentStage?: string;
  currentStageLabel?: string;
};

export function ReviewStageStepper({ status, currentStage, currentStageLabel }: Props) {
  if (status === 'completed' || status === 'failed') {
    return null;
  }

  const activeIndex = STAGES.findIndex((stage) => stage.key === currentStage);

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" sx={{ mb: 0.5 }}>
          {currentStageLabel ?? 'Queued'}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          This review is in progress. The page updates automatically as each stage completes.
        </Typography>
        <Stepper activeStep={activeIndex} alternativeLabel>
          {STAGES.map((stage) => (
            <Step key={stage.key} completed={activeIndex > STAGES.indexOf(stage)}>
              <StepLabel>{stage.label}</StepLabel>
            </Step>
          ))}
        </Stepper>
      </CardContent>
    </Card>
  );
}
