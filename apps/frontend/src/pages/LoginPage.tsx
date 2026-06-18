import { Lock as LockIcon } from '@mui/icons-material';
import { Alert, Box, Button, Paper, Stack, TextField, Typography } from '@mui/material';
import { useMutation } from '@tanstack/react-query';
import { FormEvent, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { setToken } from '../api/client';
import { login } from '../api/queries';

export function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('admin@example.com');
  const [password, setPassword] = useState('ChangeMe123!');
  const mutation = useMutation({
    mutationFn: () => login(email, password),
    onSuccess: (data) => {
      setToken(data.access_token);
      navigate('/');
    }
  });

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    mutation.mutate();
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'grid',
        placeItems: 'center',
        background: '#eef3f8',
        p: 2
      }}
    >
      <Paper sx={{ width: '100%', maxWidth: 430, p: 4, border: '1px solid #d9e1ec' }} elevation={0}>
        <Stack spacing={2.5} component="form" onSubmit={onSubmit}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <LockIcon color="primary" />
            <Typography variant="h5">Sign in</Typography>
          </Box>
          {mutation.isError && <Alert severity="error">Unable to sign in with those credentials.</Alert>}
          <TextField label="Email" value={email} onChange={(event) => setEmail(event.target.value)} fullWidth />
          <TextField
            label="Password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            fullWidth
          />
          <Button type="submit" variant="contained" size="large" disabled={mutation.isPending}>
            Sign in
          </Button>
        </Stack>
      </Paper>
    </Box>
  );
}
