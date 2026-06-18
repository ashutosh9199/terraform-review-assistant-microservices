import { Box, Card, CardContent, Grid, Stack, Typography } from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { useQuery } from '@tanstack/react-query';
import { getDashboard } from '../api/queries';
import { ScoreTile } from '../components/ScoreTile';

const columns: GridColDef[] = [
  { field: 'filename', headerName: 'Review', flex: 1 },
  { field: 'status', headerName: 'Status', width: 130 },
  { field: 'score', headerName: 'Score', width: 100 },
  { field: 'created_at', headerName: 'Created', flex: 1 }
];

export function DashboardPage() {
  const { data, isLoading } = useQuery({ queryKey: ['dashboard'], queryFn: getDashboard });

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h4">Dashboard</Typography>
        <Typography color="text.secondary">Infrastructure review posture across submitted Terraform projects.</Typography>
      </Box>
      <Grid container spacing={2}>
        <Grid item xs={12} md={2}>
          <ScoreTile label="Total Reviews" value={data?.total_reviews ?? 0} />
        </Grid>
        <Grid item xs={12} md={2}>
          <ScoreTile label="Average Score" value={data?.average_score ?? 0} />
        </Grid>
        <Grid item xs={12} md={2}>
          <ScoreTile label="Security" value={data?.security_average ?? 0} tone="error" />
        </Grid>
        <Grid item xs={12} md={2}>
          <ScoreTile label="Cost" value={data?.cost_average ?? 0} tone="success" />
        </Grid>
        <Grid item xs={12} md={2}>
          <ScoreTile label="Governance" value={data?.governance_average ?? 0} tone="warning" />
        </Grid>
        <Grid item xs={12} md={2}>
          <ScoreTile label="Operations" value={data?.operations_average ?? 0} />
        </Grid>
      </Grid>
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <TrendPanel title="Security Trends" values={data?.security_trend ?? []} tone="#d32f2f" />
        </Grid>
        <Grid item xs={12} md={6}>
          <TrendPanel title="Cost Trends" values={data?.cost_trend ?? []} tone="#2e7d32" />
        </Grid>
      </Grid>
      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Recent Reviews
          </Typography>
          <DataGrid
            rows={data?.recent_reviews ?? []}
            columns={columns}
            loading={isLoading}
            autoHeight
            disableRowSelectionOnClick
            pageSizeOptions={[8, 25, 100]}
          />
        </CardContent>
      </Card>
    </Stack>
  );
}

function TrendPanel({
  title,
  values,
  tone
}: {
  title: string;
  values: Array<{ label: string; score: number }>;
  tone: string;
}) {
  const bars = values.length ? values : [{ label: 'No data', score: 0 }];
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" sx={{ mb: 2 }}>
          {title}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'end', gap: 1, minHeight: 150 }}>
          {bars.map((item, index) => (
            <Box key={`${item.label}-${index}`} sx={{ flex: 1, minWidth: 0 }}>
              <Box
                title={`${item.label}: ${item.score}`}
                sx={{
                  height: 112,
                  display: 'flex',
                  alignItems: 'end',
                  borderBottom: '1px solid',
                  borderColor: 'divider'
                }}
              >
                <Box
                  sx={{
                    width: '100%',
                    height: `${Math.max(4, item.score)}%`,
                    bgcolor: tone,
                    opacity: 0.8,
                    borderRadius: '4px 4px 0 0'
                  }}
                />
              </Box>
              <Typography variant="caption" color="text.secondary" noWrap>
                {item.label}
              </Typography>
            </Box>
          ))}
        </Box>
      </CardContent>
    </Card>
  );
}
