import { Box, Card, CardContent, LinearProgress, Typography } from '@mui/material';

type Props = {
  label: string;
  value: number;
  tone?: 'primary' | 'success' | 'warning' | 'error';
};

export function ScoreTile({ label, value, tone = 'primary' }: Props) {
  return (
    <Card sx={{ position: 'relative', overflow: 'hidden' }}>
      <Box sx={{ position: 'absolute', top: 0, left: 0, right: 0, height: 3, bgcolor: `${tone}.main` }} />
      <CardContent>
        <Typography variant="overline" color="text.secondary" sx={{ fontSize: 11 }}>
          {label}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 0.5, mt: 0.5 }}>
          <Typography variant="h4" sx={{ color: `${tone}.dark`, lineHeight: 1 }}>
            {value}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            /100
          </Typography>
        </Box>
        <LinearProgress
          variant="determinate"
          value={value}
          color={tone}
          sx={{ mt: 2, height: 6, borderRadius: 4, bgcolor: 'rgba(0,0,0,0.06)' }}
        />
      </CardContent>
    </Card>
  );
}
