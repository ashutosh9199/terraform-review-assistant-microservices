import { PersonAdd as PersonAddIcon } from '@mui/icons-material';
import { Alert, Button, Link, Stack, TextField, Typography } from '@mui/material';
import { useMutation } from '@tanstack/react-query';
import { AxiosError } from 'axios';
import { FormEvent, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { setToken } from '../api/client';
import { signup } from '../api/queries';
import { AuthLayout } from '../components/AuthLayout';

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
      navigate('/app');
    }
  });

  const passwordsMismatch = confirmPassword.length > 0 && password !== confirmPassword;

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (passwordsMismatch || password.length < 8) return;
    mutation.mutate();
  }

  return (
    <AuthLayout>
      <Stack spacing={2.5} component="form" onSubmit={onSubmit}>
        <Stack spacing={0.5}>
          <Stack direction="row" alignItems="center" spacing={1}>
            <PersonAddIcon color="primary" fontSize="small" />
            <Typography variant="h5">Create an account</Typography>
          </Stack>
          <Typography variant="body2" color="text.secondary">
            Start reviewing your Azure Terraform projects in minutes.
          </Typography>
        </Stack>
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
    </AuthLayout>
  );
}
