import { DeleteOutline as DeleteIcon, Save as SaveIcon, Science as TestIcon } from '@mui/icons-material';
import {
  Alert,
  Autocomplete,
  Button,
  Card,
  CardContent,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  TextField,
  Typography
} from '@mui/material';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { AxiosError } from 'axios';
import { FormEvent, useState } from 'react';
import { deleteLlmSettings, getLlmSettings, saveLlmSettings, testLlmSettings } from '../api/queries';
import { detectProvider, findProvider, PROVIDERS, ProviderId } from '../llmProviders';

function errorDetail(error: unknown): string {
  const detail = (error as AxiosError<{ detail?: string }>)?.response?.data?.detail;
  return detail ?? 'Request failed.';
}

export function SettingsPage() {
  const queryClient = useQueryClient();
  const { data } = useQuery({ queryKey: ['llm-settings'], queryFn: getLlmSettings });
  const [provider, setProvider] = useState<ProviderId>('auto');
  const [endpoint, setEndpoint] = useState('');
  const [model, setModel] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [tested, setTested] = useState(false);
  const [confirmRemoveOpen, setConfirmRemoveOpen] = useState(false);

  const providerOption = findProvider(provider);

  function onApiKeyChange(value: string) {
    setApiKey(value);
    setTested(false);
    if (provider === 'auto' && value.length >= 8) {
      const detected = detectProvider(value, endpoint, model);
      if (detected !== 'auto') setProvider(detected);
    }
  }

  const testMutation = useMutation({
    mutationFn: () =>
      testLlmSettings({
        api_key: apiKey,
        endpoint: endpoint || undefined,
        model: model || undefined,
        provider: provider === 'auto' ? undefined : provider
      }),
    onSuccess: () => setTested(true)
  });

  const saveMutation = useMutation({
    mutationFn: () =>
      saveLlmSettings({
        api_key: apiKey,
        endpoint: endpoint || undefined,
        model: model || undefined,
        provider: provider === 'auto' ? undefined : provider
      }),
    onSuccess: () => {
      setApiKey('');
      setTested(false);
      queryClient.invalidateQueries({ queryKey: ['llm-settings'] });
    }
  });

  const removeMutation = useMutation({
    mutationFn: deleteLlmSettings,
    onSuccess: () => {
      setConfirmRemoveOpen(false);
      queryClient.invalidateQueries({ queryKey: ['llm-settings'] });
    }
  });

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    saveMutation.mutate();
  }

  return (
    <Stack spacing={3}>
      <div>
        <Typography variant="h4">Settings</Typography>
        <Typography color="text.secondary">Configure LLM access and review behavior.</Typography>
      </div>
      <Card>
        <CardContent>
          <Stack component="form" spacing={2.5} onSubmit={onSubmit}>
            {data && (
              <Alert
                severity="info"
                action={
                  <Button color="error" size="small" startIcon={<DeleteIcon />} onClick={() => setConfirmRemoveOpen(true)}>
                    Remove key
                  </Button>
                }
              >
                Active provider: {data.provider}
                {data.model ? `, model: ${data.model}` : ''}
              </Alert>
            )}
            {removeMutation.isSuccess && <Alert severity="success">API key removed. Reviews will use the offline heuristic until a new key is configured.</Alert>}
            {removeMutation.isError && <Alert severity="error">{errorDetail(removeMutation.error)}</Alert>}
            {saveMutation.isSuccess && <Alert severity="success">LLM settings saved.</Alert>}
            {saveMutation.isError && <Alert severity="error">{errorDetail(saveMutation.error)}</Alert>}
            <FormControl fullWidth>
              <InputLabel>Provider</InputLabel>
              <Select
                label="Provider"
                value={provider}
                onChange={(event) => {
                  setProvider(event.target.value as ProviderId);
                  setModel('');
                  setTested(false);
                }}
              >
                {PROVIDERS.map((item) => (
                  <MenuItem key={item.id} value={item.id}>
                    {item.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label="API key"
              type="password"
              value={apiKey}
              onChange={(event) => onApiKeyChange(event.target.value)}
              helperText={provider !== 'auto' ? `Detected/selected provider: ${providerOption?.label}` : 'Paste a key to auto-detect the provider'}
              required
              fullWidth
            />
            <TextField
              label="Endpoint"
              value={endpoint}
              onChange={(event) => {
                setEndpoint(event.target.value);
                setTested(false);
              }}
              placeholder="https://resource.openai.azure.com"
              required={providerOption?.requiresEndpoint}
              fullWidth
            />
            <Autocomplete
              freeSolo
              options={providerOption?.models ?? []}
              value={model}
              onInputChange={(_event, value) => {
                setModel(value);
                setTested(false);
              }}
              renderInput={(params) => (
                <TextField {...params} label="Model or deployment" placeholder="gpt-4o or Azure deployment name" fullWidth />
              )}
            />
            <Stack direction="row" spacing={1.5}>
              <Button
                variant="outlined"
                startIcon={<TestIcon />}
                onClick={() => testMutation.mutate()}
                disabled={testMutation.isPending || apiKey.length < 8}
              >
                Test connection
              </Button>
              <Button
                type="submit"
                variant="contained"
                startIcon={<SaveIcon />}
                disabled={saveMutation.isPending || apiKey.length < 8}
              >
                Save settings
              </Button>
            </Stack>
            {testMutation.isPending && <Alert severity="info">Sending a test message to the provider...</Alert>}
            {testMutation.isError && <Alert severity="error">Connection test failed: {errorDetail(testMutation.error)}</Alert>}
            {tested && testMutation.data && (
              <Alert severity="success">
                Connected to {testMutation.data.provider} ({testMutation.data.model}). Reply: &ldquo;{testMutation.data.reply}&rdquo;
              </Alert>
            )}
          </Stack>
        </CardContent>
      </Card>

      <Dialog open={confirmRemoveOpen} onClose={() => setConfirmRemoveOpen(false)}>
        <DialogTitle>Remove API key?</DialogTitle>
        <DialogContent>
          <DialogContentText>
            This deactivates the current LLM connection. New reviews will use the offline rule-based
            heuristic instead of AI-generated findings until you add and verify a new key.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmRemoveOpen(false)} disabled={removeMutation.isPending}>
            Cancel
          </Button>
          <Button color="error" variant="contained" onClick={() => removeMutation.mutate()} disabled={removeMutation.isPending}>
            Remove key
          </Button>
        </DialogActions>
      </Dialog>
    </Stack>
  );
}
