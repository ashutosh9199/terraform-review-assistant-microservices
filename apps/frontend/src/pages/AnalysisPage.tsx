import { Download as DownloadIcon, Refresh as RefreshIcon } from '@mui/icons-material';
import { Box, Button, Card, CardContent, Chip, Grid, Stack, Typography } from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { useQuery } from '@tanstack/react-query';
import { useParams } from 'react-router-dom';
import { getReview } from '../api/queries';
import { api } from '../api/client';
import { ReviewStageStepper } from '../components/ReviewStageStepper';
import { ScoreTile } from '../components/ScoreTile';
import { SeverityChip } from '../components/SeverityChip';

const findingColumns: GridColDef[] = [
  {
    field: 'severity',
    headerName: 'Severity',
    width: 125,
    renderCell: (params) => <SeverityChip severity={params.value} />
  },
  { field: 'category', headerName: 'Category', width: 130 },
  { field: 'source', headerName: 'Source', width: 120 },
  { field: 'resource_address', headerName: 'Resource', flex: 1 },
  { field: 'title', headerName: 'Finding', flex: 1.4 },
  { field: 'recommendation', headerName: 'Recommendation', flex: 1.6 }
];

const resourceColumns: GridColDef[] = [
  { field: 'address', headerName: 'Address', flex: 1 },
  { field: 'resource_type', headerName: 'Type', flex: 1 },
  { field: 'file', headerName: 'File', flex: 1 },
  {
    field: 'supported',
    headerName: 'Coverage',
    width: 120,
    renderCell: (params) => <Chip size="small" label={params.value ? 'Supported' : 'Review'} />
  }
];

const REPORT_MIME: Record<'json' | 'html' | 'pdf', string> = {
  json: 'application/json',
  html: 'text/html',
  pdf: 'application/pdf'
};

export function AnalysisPage() {
  const { reviewId } = useParams();
  const { data, refetch, isLoading } = useQuery({
    queryKey: ['review', reviewId],
    queryFn: () => getReview(Number(reviewId)),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === 'queued' || status === 'running' ? 2500 : false;
    }
  });

  async function downloadReport(format: 'json' | 'html' | 'pdf') {
    const response = await api.get(`/api/reviews/${reviewId}/report.${format}`, {
      responseType: 'blob'
    });
    const blob = new Blob([response.data], { type: REPORT_MIME[format] });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `terraform-review-${reviewId}.${format}`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  return (
    <Stack spacing={3}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', gap: 2 }}>
        <Box>
          <Typography variant="h4">Analysis</Typography>
          <Typography color="text.secondary">{data?.original_filename ?? 'Review details'}</Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          <Button startIcon={<RefreshIcon />} onClick={() => refetch()}>
            Refresh
          </Button>
          <Button startIcon={<DownloadIcon />} onClick={() => downloadReport('json')} disabled={data?.status !== 'completed'}>
            JSON
          </Button>
          <Button variant="contained" startIcon={<DownloadIcon />} onClick={() => downloadReport('html')} disabled={data?.status !== 'completed'}>
            HTML
          </Button>
          <Button startIcon={<DownloadIcon />} onClick={() => downloadReport('pdf')} disabled={data?.status !== 'completed'}>
            PDF
          </Button>
        </Stack>
      </Box>

      <Chip
        sx={{ width: 'fit-content' }}
        color={data?.status === 'completed' ? 'success' : data?.status === 'failed' ? 'error' : 'info'}
        label={data?.status === 'running' ? data?.current_stage_label ?? 'running' : data?.status ?? 'loading'}
      />

      {data && (
        <ReviewStageStepper
          status={data.status}
          currentStage={data.current_stage}
          currentStageLabel={data.current_stage_label}
        />
      )}

      <Grid container spacing={2}>
        <Grid item xs={12} md={2.4}>
          <ScoreTile label="Overall" value={data?.scorecard?.overall_score ?? 0} />
        </Grid>
        <Grid item xs={12} md={2.4}>
          <ScoreTile label="Security" value={data?.scorecard?.security_score ?? 0} tone="error" />
        </Grid>
        <Grid item xs={12} md={2.4}>
          <ScoreTile label="Cost" value={data?.scorecard?.cost_score ?? 0} tone="success" />
        </Grid>
        <Grid item xs={12} md={2.4}>
          <ScoreTile label="Governance" value={data?.scorecard?.governance_score ?? 0} tone="warning" />
        </Grid>
        <Grid item xs={12} md={2.4}>
          <ScoreTile label="Operations" value={data?.scorecard?.operations_score ?? 0} />
        </Grid>
      </Grid>

      {data?.executive_feedback && (
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 1 }}>
              Reviewer Feedback
            </Typography>
            <Typography color="text.secondary">{data.executive_feedback}</Typography>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Findings
          </Typography>
          <DataGrid rows={data?.findings ?? []} columns={findingColumns} loading={isLoading} autoHeight pageSizeOptions={[10, 25, 100]} />
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Resource Inventory
          </Typography>
          <DataGrid
            rows={(data?.inventory?.resources ?? []).map((row, index) => ({ id: index, ...row }))}
            columns={resourceColumns}
            autoHeight
            pageSizeOptions={[10, 25, 100]}
          />
        </CardContent>
      </Card>
    </Stack>
  );
}
