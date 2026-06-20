import {
  ArrowForward as ArrowForwardIcon,
  AutoAwesome as AutoAwesomeIcon,
  CloudUpload as CloudUploadIcon,
  Gavel as GavelIcon,
  Insights as InsightsIcon,
  Layers as LayersIcon,
  Shield as ShieldIcon
} from '@mui/icons-material';
import { Box, Button, Card, Chip, Container, Grid, Stack, Typography } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const features = [
  {
    icon: <CloudUploadIcon fontSize="small" />,
    title: 'Upload Terraform',
    description: 'Drop in .tf, .tfvars, or a zipped project. Files are parsed only — never executed.'
  },
  {
    icon: <GavelIcon fontSize="small" />,
    title: 'Deterministic Rules',
    description: 'Azure security, governance, operations, cost, and quality checks run first, before any AI.'
  },
  {
    icon: <AutoAwesomeIcon fontSize="small" />,
    title: 'AI-Assisted Review',
    description: 'Specialist reviewers analyze deterministic evidence and surface prioritized recommendations.'
  },
  {
    icon: <InsightsIcon fontSize="small" />,
    title: 'Scorecards & Reports',
    description: 'Get a weighted infrastructure scorecard and export JSON, HTML, or PDF reports.'
  }
];

const stats = [
  { label: 'Review stages', value: '6' },
  { label: 'Rule categories', value: '5' },
  { label: 'LLM providers', value: '4+' },
  { label: 'Report formats', value: '3' }
];

export function LandingPage() {
  const navigate = useNavigate();

  return (
    <Box sx={{ minHeight: '100vh', background: '#f5f7fb' }}>
      <Box sx={{ borderBottom: '1px solid', borderColor: 'divider', background: 'rgba(255,255,255,0.85)', backdropFilter: 'blur(6px)', position: 'sticky', top: 0, zIndex: 10 }}>
        <Container maxWidth="lg">
          <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ py: 1.75 }}>
            <Stack direction="row" alignItems="center" spacing={1.25}>
              <Box
                sx={{
                  width: 34,
                  height: 34,
                  borderRadius: 2,
                  display: 'grid',
                  placeItems: 'center',
                  backgroundImage: 'linear-gradient(135deg, #205493 0%, #133a65 100%)',
                  color: '#fff'
                }}
              >
                <LayersIcon fontSize="small" />
              </Box>
              <Typography variant="h6">Terraform Review Assistant</Typography>
            </Stack>
            <Stack direction="row" spacing={1.5}>
              <Button onClick={() => navigate('/login')}>Sign in</Button>
              <Button variant="contained" endIcon={<ArrowForwardIcon />} onClick={() => navigate('/signup')}>
                Get started
              </Button>
            </Stack>
          </Stack>
        </Container>
      </Box>

      <Box
        sx={{
          backgroundImage:
            'radial-gradient(circle at 15% 0%, rgba(32, 84, 147, 0.10), transparent 45%), radial-gradient(circle at 85% 10%, rgba(31, 122, 109, 0.10), transparent 40%)'
        }}
      >
        <Container maxWidth="lg" sx={{ pt: { xs: 8, md: 11 }, pb: { xs: 8, md: 10 } }}>
          <Stack spacing={3} alignItems="center" textAlign="center">
            <Chip
              icon={<ShieldIcon fontSize="small" />}
              label="Built for Azure infrastructure-as-code"
              color="primary"
              variant="outlined"
              sx={{ bgcolor: '#fff' }}
            />
            <Typography variant="h3" sx={{ maxWidth: 780, fontSize: { xs: '2.1rem', md: '3rem' } }}>
              AI-powered review for your Azure Terraform projects
            </Typography>
            <Typography variant="h6" color="text.secondary" sx={{ maxWidth: 640, fontWeight: 400 }}>
              Static analysis, governance checks, and AI-assisted recommendations — scored and
              reported, before anything reaches production.
            </Typography>
            <Stack direction="row" spacing={2} sx={{ pt: 1 }}>
              <Button size="large" variant="contained" endIcon={<ArrowForwardIcon />} onClick={() => navigate('/signup')}>
                Get started free
              </Button>
              <Button size="large" onClick={() => navigate('/login')}>
                Sign in
              </Button>
            </Stack>
          </Stack>

          <Card sx={{ mt: 7, py: 2.5 }}>
            <Grid container>
              {stats.map((stat, index) => (
                <Grid
                  item
                  xs={6}
                  md={3}
                  key={stat.label}
                  sx={{
                    textAlign: 'center',
                    borderRight: { md: index < stats.length - 1 ? '1px solid' : 'none' },
                    borderColor: 'divider'
                  }}
                >
                  <Typography variant="h4" color="primary.dark">
                    {stat.value}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {stat.label}
                  </Typography>
                </Grid>
              ))}
            </Grid>
          </Card>
        </Container>
      </Box>

      <Container maxWidth="lg" sx={{ py: { xs: 8, md: 10 } }}>
        <Stack spacing={1} alignItems="center" textAlign="center" sx={{ mb: 6 }}>
          <Typography variant="overline" color="primary">
            How it works
          </Typography>
          <Typography variant="h4">From upload to executive-ready report</Typography>
        </Stack>
        <Grid container spacing={3}>
          {features.map((feature) => (
            <Grid item xs={12} sm={6} md={3} key={feature.title}>
              <Card sx={{ p: 3, height: '100%' }} elevation={0}>
                <Stack spacing={1.75}>
                  <Box
                    sx={{
                      width: 44,
                      height: 44,
                      borderRadius: '50%',
                      display: 'grid',
                      placeItems: 'center',
                      bgcolor: 'rgba(32, 84, 147, 0.1)',
                      color: 'primary.main'
                    }}
                  >
                    {feature.icon}
                  </Box>
                  <Typography variant="h6">{feature.title}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {feature.description}
                  </Typography>
                </Stack>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      <Box sx={{ borderTop: '1px solid', borderColor: 'divider', backgroundImage: 'linear-gradient(135deg, #163d6e 0%, #205493 60%, #1f7a6d 100%)' }}>
        <Container maxWidth="lg" sx={{ py: 7 }}>
          <Stack spacing={2.5} alignItems="center" textAlign="center" sx={{ color: '#fff' }}>
            <Typography variant="h4" sx={{ color: '#fff' }}>
              Ready to review your first project?
            </Typography>
            <Typography sx={{ opacity: 0.85, maxWidth: 520 }}>
              Create an account and upload your Terraform project to get a full scorecard in minutes.
            </Typography>
            <Button
              size="large"
              variant="contained"
              endIcon={<ArrowForwardIcon />}
              onClick={() => navigate('/signup')}
              sx={{ bgcolor: '#fff', color: 'primary.dark', '&:hover': { bgcolor: '#eef1f6' } }}
            >
              Get started free
            </Button>
          </Stack>
        </Container>
      </Box>

      <Box sx={{ background: '#0f2a4d' }}>
        <Container maxWidth="lg" sx={{ py: 3 }}>
          <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)' }} textAlign="center">
            Terraform Review Assistant — uploaded infrastructure is parsed only, never executed.
          </Typography>
        </Container>
      </Box>
    </Box>
  );
}
