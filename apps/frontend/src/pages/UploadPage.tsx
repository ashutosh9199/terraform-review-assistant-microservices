import { CloudUpload as CloudUploadIcon } from '@mui/icons-material';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  TextField,
  Typography
} from '@mui/material';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';
import { createProject, getProjects, uploadReview } from '../api/queries';

export function UploadPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { data: projects } = useQuery({ queryKey: ['projects'], queryFn: getProjects });
  const [projectId, setProjectId] = useState<number | ''>('');
  const [newProjectName, setNewProjectName] = useState('Azure Landing Zone Review');
  const [files, setFiles] = useState<File[]>([]);

  const projectMutation = useMutation({
    mutationFn: () => createProject(newProjectName),
    onSuccess: (project) => {
      setProjectId(project.id);
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    }
  });

  const uploadMutation = useMutation({
    mutationFn: async () => {
      const effectiveProjectId =
        projectId || (await createProject(newProjectName, 'Created during Terraform upload')).id;
      if (!files.length) throw new Error('Select files first');
      return uploadReview(Number(effectiveProjectId), files);
    },
    onSuccess: (review) => navigate(`/analysis/${review.id}`)
  });

  const dropzone = useDropzone({
    multiple: true,
    accept: {
      'application/zip': ['.zip'],
      'text/plain': ['.tf', '.tfvars']
    },
    onDrop: (accepted) => setFiles(accepted)
  });

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h4">Upload Terraform</Typography>
        <Typography color="text.secondary">Submit a ZIP project or individual Terraform files for review.</Typography>
      </Box>
      <Card>
        <CardContent>
          <Stack spacing={3}>
            <Box sx={{ display: 'grid', gap: 2, gridTemplateColumns: { xs: '1fr', md: '1fr 1fr auto' } }}>
              <FormControl fullWidth>
                <InputLabel>Project</InputLabel>
                <Select
                  label="Project"
                  value={projectId}
                  onChange={(event) => setProjectId(Number(event.target.value))}
                >
                  {(projects ?? []).map((project) => (
                    <MenuItem key={project.id} value={project.id}>
                      {project.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <TextField
                label="New project name"
                value={newProjectName}
                onChange={(event) => setNewProjectName(event.target.value)}
              />
              <Button variant="outlined" onClick={() => projectMutation.mutate()} disabled={projectMutation.isPending}>
                Create
              </Button>
            </Box>

            <Box
              {...dropzone.getRootProps()}
              sx={{
                border: '1px dashed #8aa4c2',
                borderRadius: 2,
                minHeight: 220,
                display: 'grid',
                placeItems: 'center',
                textAlign: 'center',
                bgcolor: dropzone.isDragActive ? '#eef6f8' : '#fbfcfe',
                cursor: 'pointer'
              }}
            >
              <input {...dropzone.getInputProps()} />
              <Stack spacing={1} alignItems="center">
                <CloudUploadIcon color="primary" fontSize="large" />
                <Typography variant="h6">
                  {files.length === 1 ? files[0].name : files.length ? `${files.length} files selected` : 'Drop Terraform ZIP or files here'}
                </Typography>
                <Typography color="text.secondary">Supported: .zip, .tf, .tfvars</Typography>
              </Stack>
            </Box>

            {files.length > 1 && (
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {files.map((selectedFile) => (
                  <Alert key={`${selectedFile.name}-${selectedFile.size}`} severity="info" sx={{ py: 0 }}>
                    {selectedFile.name}
                  </Alert>
                ))}
              </Box>
            )}

            {uploadMutation.isError && <Alert severity="error">Upload failed. Check the file and API connection.</Alert>}

            <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
              <Button
                variant="contained"
                size="large"
                disabled={!files.length || uploadMutation.isPending}
                onClick={() => uploadMutation.mutate()}
              >
                Start review
              </Button>
            </Box>
          </Stack>
        </CardContent>
      </Card>
    </Stack>
  );
}
