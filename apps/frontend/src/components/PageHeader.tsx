import { Box, Stack, Typography } from '@mui/material';
import { ReactNode } from 'react';

type Props = {
  title: string;
  description?: string;
  actions?: ReactNode;
};

export function PageHeader({ title, description, actions }: Props) {
  return (
    <Stack direction="row" alignItems="flex-start" justifyContent="space-between" spacing={2} flexWrap="wrap">
      <Box>
        <Typography variant="h4">{title}</Typography>
        {description && (
          <Typography color="text.secondary" sx={{ mt: 0.5 }}>
            {description}
          </Typography>
        )}
      </Box>
      {actions && <Box sx={{ flexShrink: 0 }}>{actions}</Box>}
    </Stack>
  );
}
