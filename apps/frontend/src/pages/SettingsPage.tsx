import { Save as SaveIcon } from '@mui/icons-material';
import {
  Alert,
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
import { FormEvent, useState } from 'react';
import { getLlmSettings, saveLlmSettings } from '../api/queries';

const providers = [
  { value: '', label: 'Auto detect' },
  { value: 'azure_openai', label: 'Azure OpenAI' },
  { value: 'openai', label: 'OpenAI' },
  { value: 'anthropic', label: 'Anthropic' },
  { value: 'gemini', label: 'Google Gemini' },
  { value: 'openai_compatible', label: 'OpenAI compatible' }
];

export function SettingsPage() {
  const queryClient = useQueryClient();
  const { data } = useQuery({ queryKey: ['llm-settings'], queryFn: getLlmSettings });
  const [provider, setProvider] = useState('');
  const [endpoint, setEndpoint] = useState('');
  const [model, setModel] = useState('');
  const [apiKey, setApiKey] = useState('');

  const mutation = useMutation({
    mutationFn: () =>
      saveLlmSettings({
        api_key: apiKey,
        endpoint: endpoint || undefined,
        model: model || undefined,
        provider: provider || undefined
      }),
    onSuccess: () => {
      setApiKey('');
      queryClient.invalidateQueries({ queryKey: ['llm-settings'] });
    }
  });

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    mutation.mutate();
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
              <Alert severity="info">
                Active provider: {data.provider}
                {data.model ? `, model: ${data.model}` : ''}
              </Alert>
            )}
            {mutation.isSuccess && <Alert severity="success">LLM settings saved.</Alert>}
            {mutation.isError && <Alert severity="error">Unable to save settings.</Alert>}
            <FormControl fullWidth>
              <InputLabel>Provider</InputLabel>
              <Select label="Provider" value={provider} onChange={(event) => setProvider(event.target.value)}>
                {providers.map((item) => (
                  <MenuItem key={item.value} value={item.value}>
                    {item.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label="API key"
              type="password"
              value={apiKey}
              onChange={(event) => setApiKey(event.target.value)}
              required
              fullWidth
            />
            <TextField
              label="Endpoint"
              value={endpoint}
              onChange={(event) => setEndpoint(event.target.value)}
              placeholder="https://resource.openai.azure.com"
              fullWidth
            />
            <TextField
              label="Model or deployment"
              value={model}
              onChange={(event) => setModel(event.target.value)}
              placeholder="gpt-4o or Azure deployment name"
              fullWidth
            />
            <Button type="submit" variant="contained" startIcon={<SaveIcon />} disabled={mutation.isPending || apiKey.length < 8}>
              Save settings
            </Button>
          </Stack>
        </CardContent>
      </Card>
    </Stack>
  );
}
