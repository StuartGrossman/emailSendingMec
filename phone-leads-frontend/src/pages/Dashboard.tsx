import React, { useEffect, useState } from 'react';
import { collection, getDocs } from 'firebase/firestore';
import {
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
} from '@mui/material';
import {
  Phone as PhoneIcon,
  Email as EmailIcon,
  Language as WebsiteIcon,
  LocationOn as LocationIcon,
  Business as BusinessIcon,
  Star as StarIcon,
  Assessment as AssessmentIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material';
import { db } from '../config/firebase';
import { PhoneLeadsData, Lead } from '../types/leads';
import { Bar, Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

interface Stats {
  totalLeads: number;
  averageScore: number;
  citiesCount: number;
  businessTypesCount: number;
  validationStats: {
    proceed: number;
    investigate: number;
    reject: number;
  };
  scoreDistribution: {
    [key: string]: number;
  };
  leadsByBusinessType: {
    [key: string]: number;
  };
  allLeads: Lead[];
}

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [stats, setStats] = useState<Stats>({
    totalLeads: 0,
    averageScore: 0,
    citiesCount: 0,
    businessTypesCount: 0,
    validationStats: {
      proceed: 0,
      investigate: 0,
      reject: 0,
    },
    scoreDistribution: {
      '0-20': 0,
      '21-40': 0,
      '41-60': 0,
      '61-80': 0,
      '81-100': 0,
    },
    leadsByBusinessType: {},
    allLeads: [],
  });
  const [chartData, setChartData] = useState<any>(null);
  const [validationChartData, setValidationChartData] = useState<any>(null);
  const [scoreChartData, setScoreChartData] = useState<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        console.log('📊 Starting to fetch dashboard data...');
        const querySnapshot = await getDocs(collection(db, 'phoneLeads'));
        console.log('📥 Raw Firestore query snapshot:', querySnapshot);
        console.log('📥 Number of documents:', querySnapshot.size);
        
        const data: PhoneLeadsData = {};
        const allLeads: Lead[] = [];
        
        querySnapshot.forEach((doc) => {
          console.log('📄 Document ID:', doc.id);
          console.log('📄 Document data:', doc.data());
          data[doc.id] = doc.data() as any;
        });
        
        console.log('📥 Processed data object:', data);
        
        let totalLeads = 0;
        let totalScore = 0;
        const cities = new Set<string>();
        const businessTypes = new Set<string>();
        const leadsByCity: { [key: string]: number } = {};
        const leadsByBusinessType: { [key: string]: number } = {};
        const validationStats = {
          proceed: 0,
          investigate: 0,
          reject: 0,
        };
        const scoreDistribution = {
          '0-20': 0,
          '21-40': 0,
          '41-60': 0,
          '61-80': 0,
          '81-100': 0,
        };

        Object.entries(data).forEach(([docId, docData]) => {
          const [city, ...businessTypeParts] = docId.split('_');
          const businessType = businessTypeParts.join('_');
          
          console.log(`Processing document: ${docId}`);
          console.log(`City: ${city}, Business Type: ${businessType}`);
          
          cities.add(city);
          businessTypes.add(businessType);
          
          if (docData.leads) {
            Object.values(docData.leads).forEach((batch: any) => {
              if (batch.leads) {
                batch.leads.forEach((lead: Lead) => {
                  totalLeads++;
                  totalScore += lead.overall_score;
                  leadsByCity[city] = (leadsByCity[city] || 0) + 1;
                  leadsByBusinessType[businessType] = (leadsByBusinessType[businessType] || 0) + 1;
                  
                  allLeads.push(lead);
                  
                  validationStats[lead.validation.recommendation]++;
                  
                  if (lead.overall_score <= 20) scoreDistribution['0-20']++;
                  else if (lead.overall_score <= 40) scoreDistribution['21-40']++;
                  else if (lead.overall_score <= 60) scoreDistribution['41-60']++;
                  else if (lead.overall_score <= 80) scoreDistribution['61-80']++;
                  else scoreDistribution['81-100']++;
                });
              }
            });
          }
        });

        const averageScore = totalLeads > 0 ? totalScore / totalLeads : 0;
        
        console.log('📈 Calculating dashboard statistics:', {
          totalLeads,
          averageScore,
          citiesCount: cities.size,
          businessTypesCount: businessTypes.size,
          validationStats,
          scoreDistribution,
          leadsByBusinessType,
        });

        setStats({
          totalLeads,
          averageScore,
          citiesCount: cities.size,
          businessTypesCount: businessTypes.size,
          validationStats,
          scoreDistribution,
          leadsByBusinessType,
          allLeads,
        });

        // Prepare chart data
        setChartData({
          labels: Object.keys(leadsByCity),
          datasets: [
            {
              label: 'Leads by City',
              data: Object.values(leadsByCity),
              backgroundColor: 'rgba(54, 162, 235, 0.5)',
            },
          ],
        });

        // Prepare validation chart data
        setValidationChartData({
          labels: ['Proceed', 'Investigate', 'Reject'],
          datasets: [
            {
              data: [
                validationStats.proceed,
                validationStats.investigate,
                validationStats.reject,
              ],
              backgroundColor: [
                'rgba(75, 192, 192, 0.5)',
                'rgba(255, 206, 86, 0.5)',
                'rgba(255, 99, 132, 0.5)',
              ],
            },
          ],
        });

        // Prepare score distribution chart data
        setScoreChartData({
          labels: Object.keys(scoreDistribution),
          datasets: [
            {
              label: 'Score Distribution',
              data: Object.values(scoreDistribution),
              backgroundColor: 'rgba(153, 102, 255, 0.5)',
            },
          ],
        });
      } catch (error) {
        console.error('❌ Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleLeadClick = (lead: Lead) => {
    setSelectedLead(lead);
  };

  const handleCloseDialog = () => {
    setSelectedLead(null);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {/* Summary Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Leads
              </Typography>
              <Typography variant="h4">
                {stats.totalLeads}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Average Score
              </Typography>
              <Typography variant="h4">
                {stats.averageScore.toFixed(1)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Cities
              </Typography>
              <Typography variant="h4">
                {stats.citiesCount}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Business Types
              </Typography>
              <Typography variant="h4">
                {stats.businessTypesCount}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Charts */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Leads by City
              </Typography>
              {chartData && (
                <Box height={300}>
                  <Bar
                    data={chartData}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                    }}
                  />
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Validation Distribution
              </Typography>
              {validationChartData && (
                <Box height={300}>
                  <Pie
                    data={validationChartData}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                    }}
                  />
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Score Distribution
              </Typography>
              {scoreChartData && (
                <Box height={300}>
                  <Bar
                    data={scoreChartData}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                    }}
                  />
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Business Type Breakdown */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Leads by Business Type
              </Typography>
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Business Type</TableCell>
                      <TableCell align="right">Number of Leads</TableCell>
                      <TableCell align="right">Percentage</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {Object.entries(stats.leadsByBusinessType).map(([type, count]) => (
                      <TableRow key={type}>
                        <TableCell component="th" scope="row">
                          {type}
                        </TableCell>
                        <TableCell align="right">{count}</TableCell>
                        <TableCell align="right">
                          {((count / stats.totalLeads) * 100).toFixed(1)}%
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Lead Cards */}
        <Grid item xs={12}>
          <Typography variant="h6" gutterBottom>
            All Leads
          </Typography>
          <Grid container spacing={2}>
            {stats.allLeads.map((lead, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <Card 
                  sx={{ 
                    cursor: 'pointer',
                    '&:hover': {
                      boxShadow: 6,
                    },
                  }}
                  onClick={() => handleLeadClick(lead)}
                >
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {lead.name}
                    </Typography>
                    <Box display="flex" alignItems="center" mb={1}>
                      <LocationIcon sx={{ mr: 1, color: 'text.secondary' }} />
                      <Typography variant="body2" color="text.secondary">
                        {lead.city}
                      </Typography>
                    </Box>
                    <Box display="flex" alignItems="center" mb={1}>
                      <BusinessIcon sx={{ mr: 1, color: 'text.secondary' }} />
                      <Typography variant="body2" color="text.secondary">
                        {lead.category}
                      </Typography>
                    </Box>
                    <Box display="flex" alignItems="center">
                      <StarIcon sx={{ mr: 1, color: 'text.secondary' }} />
                      <Typography variant="body2" color="text.secondary">
                        Score: {lead.overall_score.toFixed(1)}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Grid>
      </Grid>

      {/* Lead Details Dialog */}
      <Dialog
        open={!!selectedLead}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        {selectedLead && (
          <>
            <DialogTitle>
              <Typography variant="h6">{selectedLead.name}</Typography>
            </DialogTitle>
            <DialogContent>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <Typography variant="subtitle1" gutterBottom>
                    Contact Information
                  </Typography>
                  <List>
                    <ListItem>
                      <ListItemIcon>
                        <PhoneIcon />
                      </ListItemIcon>
                      <ListItemText primary="Phone" secondary={selectedLead.phone} />
                    </ListItem>
                    {selectedLead.email && (
                      <ListItem>
                        <ListItemIcon>
                          <EmailIcon />
                        </ListItemIcon>
                        <ListItemText primary="Email" secondary={selectedLead.email} />
                      </ListItem>
                    )}
                    {selectedLead.website && (
                      <ListItem>
                        <ListItemIcon>
                          <WebsiteIcon />
                        </ListItemIcon>
                        <ListItemText primary="Website" secondary={selectedLead.website} />
                      </ListItem>
                    )}
                    {selectedLead.address && (
                      <ListItem>
                        <ListItemIcon>
                          <LocationIcon />
                        </ListItemIcon>
                        <ListItemText primary="Address" secondary={selectedLead.address} />
                      </ListItem>
                    )}
                  </List>
                </Grid>

                <Grid item xs={12}>
                  <Divider />
                </Grid>

                <Grid item xs={12}>
                  <Typography variant="subtitle1" gutterBottom>
                    Analysis Scores
                  </Typography>
                  <List>
                    <ListItem>
                      <ListItemIcon>
                        <StarIcon />
                      </ListItemIcon>
                      <ListItemText 
                        primary="Overall Score" 
                        secondary={selectedLead.overall_score.toFixed(1)} 
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon>
                        <AssessmentIcon />
                      </ListItemIcon>
                      <ListItemText 
                        primary="Tech Stack Score" 
                        secondary={selectedLead.analysis.tech_stack.score.toFixed(1)} 
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon>
                        <AssessmentIcon />
                      </ListItemIcon>
                      <ListItemText 
                        primary="Operations Score" 
                        secondary={selectedLead.analysis.operations.score.toFixed(1)} 
                      />
                    </ListItem>
                  </List>
                </Grid>

                <Grid item xs={12}>
                  <Divider />
                </Grid>

                <Grid item xs={12}>
                  <Typography variant="subtitle1" gutterBottom>
                    Validation
                  </Typography>
                  <List>
                    <ListItem>
                      <ListItemIcon>
                        {selectedLead.validation.recommendation === 'proceed' ? (
                          <CheckCircleIcon color="success" />
                        ) : selectedLead.validation.recommendation === 'investigate' ? (
                          <WarningIcon color="warning" />
                        ) : (
                          <CancelIcon color="error" />
                        )}
                      </ListItemIcon>
                      <ListItemText 
                        primary="Recommendation" 
                        secondary={selectedLead.validation.recommendation.charAt(0).toUpperCase() + 
                                  selectedLead.validation.recommendation.slice(1)} 
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon>
                        <AssessmentIcon />
                      </ListItemIcon>
                      <ListItemText 
                        primary="Confidence Score" 
                        secondary={selectedLead.validation.confidence_score.toFixed(1)} 
                      />
                    </ListItem>
                  </List>
                </Grid>

                {selectedLead.analysis.tech_stack.current_systems.length > 0 && (
                  <>
                    <Grid item xs={12}>
                      <Divider />
                    </Grid>
                    <Grid item xs={12}>
                      <Typography variant="subtitle1" gutterBottom>
                        Tech Stack
                      </Typography>
                      <List>
                        <ListItem>
                          <ListItemText 
                            primary="Current Systems" 
                            secondary={selectedLead.analysis.tech_stack.current_systems.join(', ')} 
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemText 
                            primary="System Age" 
                            secondary={selectedLead.analysis.tech_stack.system_age} 
                          />
                        </ListItem>
                        {selectedLead.analysis.tech_stack.limitations.length > 0 && (
                          <ListItem>
                            <ListItemText 
                              primary="Limitations" 
                              secondary={selectedLead.analysis.tech_stack.limitations.join(', ')} 
                            />
                          </ListItem>
                        )}
                      </List>
                    </Grid>
                  </>
                )}
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleCloseDialog}>Close</Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
}

export default Dashboard; 