import { PersonAdd as PersonAddIcon } from '@mui/icons-material';
import { Alert, Box, Button, Link, Paper, Stack, TextField, Typography } from '@mui/material';
import { useMutation } from '@tanstack/react-query';
import { AxiosError } from 'axios';
import { FormEvent, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { setToken } from '../api/client';
import { signup } from '../api/queries';

function errorDetail(error: unknown): string {
  const detail = (error as AxiosError<{ detail?: string }>)?.response?.data?.detail;
  return detail ?? 'Unable to create an account.';
}

export function SignupPage() {
  const navigate = useNavigate();
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const mutation = useMutation({
    mutationFn: () => signup(email, password, fullName),
    onSuccess: (data) => {
      setToken(data.access_token);
      navigate('/');
    }
  });

  const passwordsMismatch = confirmPassword.length > 0 && password !== confirmPassword;

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (passwordsMismatch || password.length < 8) return;
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
            <PersonAddIcon color="primary" />
            <Typography variant="h5">Create an account</Typography>
          </Box>
          {mutation.isError && <Alert severity="error">{errorDetail(mutation.error)}</Alert>}
          <TextField label="Full name" value={fullName} onChange={(event) => setFullName(event.target.value)} fullWidth />
          <TextField
            label="Email"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
            fullWidth
          />
          <TextField
            label="Password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            helperText="At least 8 characters"
            required
            fullWidth
          />
          <TextField
            label="Confirm password"
            type="password"
            value={confirmPassword}
            onChange={(event) => setConfirmPassword(event.target.value)}
            error={passwordsMismatch}
            helperText={passwordsMismatch ? 'Passwords do not match' : ' '}
            required
            fullWidth
          />
          <Button
            type="submit"
            variant="contained"
            size="large"
            disabled={mutation.isPending || password.length < 8 || passwordsMismatch}
          >
            Sign up
          </Button>
          <Typography variant="body2" color="text.secondary" textAlign="center">
            Already have an account?{' '}
            <Link component="button" type="button" onClick={() => navigate('/login')}>
              Sign in
            </Link>
          </Typography>
        </Stack>
      </Paper>
    </Box>
  );
}
