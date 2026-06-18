import { Chip } from '@mui/material';
import type { Finding } from '../api/types';

const colorBySeverity: Record<Finding['severity'], 'error' | 'warning' | 'info' | 'success' | 'default'> = {
  critical: 'error',
  high: 'error',
  medium: 'warning',
  low: 'info',
  info: 'default'
};

export function SeverityChip({ severity }: { severity: Finding['severity'] }) {
  return <Chip size="small" color={colorBySeverity[severity]} label={severity.toUpperCase()} />;
}
