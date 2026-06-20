import { Card, CardContent, Stack } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { useNavigate } from 'react-router-dom';
import { getDashboard } from '../api/queries';
import { PageHeader } from '../components/PageHeader';

const columns: GridColDef[] = [
  { field: 'filename', headerName: 'Report', flex: 1 },
  { field: 'status', headerName: 'Status', width: 130 },
  { field: 'score', headerName: 'Score', width: 100 },
  { field: 'created_at', headerName: 'Created', flex: 1 }
];

export function ReportsPage() {
  const navigate = useNavigate();
  const { data, isLoading } = useQuery({ queryKey: ['dashboard'], queryFn: getDashboard });

  return (
    <Stack spacing={3}>
      <PageHeader title="Reports" description="Open completed reviews and download assessment artifacts." />
      <Card>
        <CardContent>
          <DataGrid
            rows={data?.recent_reviews ?? []}
            columns={columns}
            loading={isLoading}
            autoHeight
            disableRowSelectionOnClick
            pageSizeOptions={[10, 25, 100]}
            onRowClick={(params) => navigate(`/app/analysis/${params.id}`)}
          />
        </CardContent>
      </Card>
    </Stack>
  );
}
