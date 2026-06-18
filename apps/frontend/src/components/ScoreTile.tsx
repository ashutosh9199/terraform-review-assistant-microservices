import { Box, Card, CardContent, LinearProgress, Typography } from '@mui/material';

type Props = {
  label: string;
  value: number;
  tone?: 'primary' | 'success' | 'warning' | 'error';
};

export function ScoreTile({ label, value, tone = 'primary' }: Props) {
  return (
    <Card>
      <CardContent>
        <Typography variant="body2" color="text.secondary">
          {label}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1, mt: 1 }}>
          <Typography variant="h4">{value}</Typography>
          <Typography variant="body2" color="text.secondary">
            /100
          </Typography>
        </Box>
        <LinearProgress
          variant="determinate"
          value={value}
          color={tone}
          sx={{ mt: 2, height: 8, borderRadius: 4 }}
        />
      </CardContent>
    </Card>
  );
}
