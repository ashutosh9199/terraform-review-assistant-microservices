import {
  AutoAwesome as AutoAwesomeIcon,
  Gavel as GavelIcon,
  Layers as LayersIcon,
  Shield as ShieldIcon
} from '@mui/icons-material';
import { Box, Paper, Stack, Typography } from '@mui/material';
import { ReactNode } from 'react';
import { Link } from 'react-router-dom';

const highlights = [
  { icon: <ShieldIcon fontSize="small" />, text: 'Azure security & governance rules, evaluated deterministically' },
  { icon: <AutoAwesomeIcon fontSize="small" />, text: 'Specialist AI reviewers for security, cost, governance, ops' },
  { icon: <GavelIcon fontSize="small" />, text: 'Weighted scorecards with exportable JSON, HTML, and PDF reports' }
];

export function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'grid',
        gridTemplateColumns: { xs: '1fr', md: '1.1fr 1fr' },
        background: '#f5f7fb'
      }}
    >
      <Box
        sx={{
          display: { xs: 'none', md: 'flex' },
          flexDirection: 'column',
          justifyContent: 'space-between',
          p: 6,
          color: '#fff',
          backgroundImage:
            'radial-gradient(circle at 20% 20%, rgba(255,255,255,0.08), transparent 40%), linear-gradient(150deg, #163d6e 0%, #205493 55%, #1f7a6d 100%)'
        }}
      >
        <Link to="/" style={{ textDecoration: 'none' }}>
          <Stack direction="row" alignItems="center" spacing={1.25} sx={{ color: '#fff' }}>
            <Box
              sx={{
                width: 36,
                height: 36,
                borderRadius: 2,
                display: 'grid',
                placeItems: 'center',
                bgcolor: 'rgba(255,255,255,0.16)'
              }}
            >
              <LayersIcon fontSize="small" />
            </Box>
            <Typography variant="h6" sx={{ color: '#fff' }}>
              Terraform Review Assistant
            </Typography>
          </Stack>
        </Link>

        <Stack spacing={4} sx={{ maxWidth: 440 }}>
          <Typography variant="h3" sx={{ fontSize: { md: '2.1rem' } }}>
            Enterprise-grade review for Azure infrastructure as code.
          </Typography>
          <Stack spacing={2.5}>
            {highlights.map((item) => (
              <Stack direction="row" spacing={1.5} key={item.text} alignItems="flex-start">
                <Box
                  sx={{
                    width: 28,
                    height: 28,
                    borderRadius: '50%',
                    display: 'grid',
                    placeItems: 'center',
                    bgcolor: 'rgba(255,255,255,0.16)',
                    flexShrink: 0,
                    mt: 0.25
                  }}
                >
                  {item.icon}
                </Box>
                <Typography sx={{ opacity: 0.92 }}>{item.text}</Typography>
              </Stack>
            ))}
          </Stack>
        </Stack>

        <Typography variant="caption" sx={{ opacity: 0.7 }}>
          Uploaded Terraform is parsed only — it is never executed.
        </Typography>
      </Box>

      <Box sx={{ display: 'grid', placeItems: 'center', p: { xs: 2, sm: 4 } }}>
        <Paper sx={{ width: '100%', maxWidth: 420, p: 4 }} elevation={0}>
          {children}
        </Paper>
      </Box>
    </Box>
  );
}
