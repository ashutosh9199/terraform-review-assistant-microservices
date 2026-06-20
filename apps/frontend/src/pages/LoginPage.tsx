import { Lock as LockIcon } from '@mui/icons-material';
import { Alert, Button, Link, Stack, TextField, Typography } from '@mui/material';
import { useMutation } from '@tanstack/react-query';
import { FormEvent, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { setToken } from '../api/client';
import { login } from '../api/queries';
import { AuthLayout } from '../components/AuthLayout';

export function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('admin@example.com');
  const [password, setPassword] = useState('ChangeMe123!');
  const mutation = useMutation({
    mutationFn: () => login(email, password),
    onSuccess: (data) => {
      setToken(data.access_token);
      navigate('/app');
    }
  });

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    mutation.mutate();
  }

  return (
    <AuthLayout>
      <Stack spacing={2.5} component="form" onSubmit={onSubmit}>
        <Stack spacing={0.5}>
          <Stack direction="row" alignItems="center" spacing={1}>
            <LockIcon color="primary" fontSize="small" />
            <Typography variant="h5">Welcome back</Typography>
          </Stack>
          <Typography variant="body2" color="text.secondary">
            Sign in to continue reviewing your Terraform projects.
          </Typography>
        </Stack>
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
        <Typography variant="body2" color="text.secondary" textAlign="center">
          Don&rsquo;t have an account?{' '}
          <Link component="button" type="button" onClick={() => navigate('/signup')}>
            Sign up
          </Link>
        </Typography>
      </Stack>
    </AuthLayout>
  );
}
