import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { doc, getDoc } from 'firebase/firestore';
import {
  Box,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Grid,
  Chip,
  Divider,
  Button,
  Rating,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  Phone as PhoneIcon,
  Email as EmailIcon,
  Language as WebsiteIcon,
  LocationOn as LocationIcon,
  Business as BusinessIcon,
  Star as StarIcon,
  AccessTime as TimeIcon,
  Facebook as FacebookIcon,
  Twitter as TwitterIcon,
  Instagram as InstagramIcon,
  LinkedIn as LinkedInIcon,
} from '@mui/icons-material';
import { db } from '../config/firebase';
import { Lead } from '../types/leads';

const LeadDetails: React.FC = () => {
  const { city, businessType, leadId } = useParams<{ city: string; businessType: string; leadId: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [lead, setLead] = useState<Lead | null>(null);

  useEffect(() => {
    if (!city || !businessType || !leadId) {
      navigate('/leads');
      return;
    }

    const fetchLead = async () => {
      try {
        const docRef = doc(db, 'phoneLeads', city, businessType, 'leads', leadId);
        const docSnap = await getDoc(docRef);
        
        if (docSnap.exists()) {
          const leadData = docSnap.data() as Lead;
          setLead({
            ...leadData,
            city,
            category: businessType,
          });
        }
      } catch (error) {
        console.error('Error fetching lead:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchLead();
  }, [city, businessType, leadId, navigate]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  if (!lead) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          Lead Not Found
        </Typography>
        <Button variant="contained" onClick={() => navigate('/leads')}>
          Back to Leads
        </Button>
      </Box>
    );
  }

  return (
    <Box>
      <Button variant="outlined" onClick={() => navigate('/leads')} sx={{ mb: 3 }}>
        Back to Leads
      </Button>

      <Typography variant="h4" gutterBottom>
        {lead.name}
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Contact Information
              </Typography>
              <List>
                <ListItem>
                  <ListItemIcon>
                    <PhoneIcon />
                  </ListItemIcon>
                  <ListItemText primary="Phone" secondary={lead.phone} />
                </ListItem>
                {lead.email && (
                  <ListItem>
                    <ListItemIcon>
                      <EmailIcon />
                    </ListItemIcon>
                    <ListItemText primary="Email" secondary={lead.email} />
                  </ListItem>
                )}
                {lead.website && (
                  <ListItem>
                    <ListItemIcon>
                      <WebsiteIcon />
                    </ListItemIcon>
                    <ListItemText primary="Website" secondary={lead.website} />
                  </ListItem>
                )}
                {lead.address && (
                  <ListItem>
                    <ListItemIcon>
                      <LocationIcon />
                    </ListItemIcon>
                    <ListItemText primary="Address" secondary={lead.address} />
                  </ListItem>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Business Information
              </Typography>
              <List>
                <ListItem>
                  <ListItemIcon>
                    <BusinessIcon />
                  </ListItemIcon>
                  <ListItemText primary="Category" secondary={lead.category} />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <StarIcon />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Overall Score" 
                    secondary={
                      <Rating value={lead.overall_score / 20} readOnly />
                    } 
                  />
                </ListItem>
                {lead.rating && (
                  <ListItem>
                    <ListItemIcon>
                      <StarIcon />
                    </ListItemIcon>
                    <ListItemText 
                      primary="Rating" 
                      secondary={
                        <Rating value={lead.rating} readOnly />
                      } 
                    />
                  </ListItem>
                )}
                {lead.reviews_count && (
                  <ListItem>
                    <ListItemIcon>
                      <StarIcon />
                    </ListItemIcon>
                    <ListItemText 
                      primary="Reviews" 
                      secondary={`${lead.reviews_count} reviews`} 
                    />
                  </ListItem>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {lead.social_links && Object.keys(lead.social_links).length > 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Social Media
                </Typography>
                <Box display="flex" gap={2}>
                  {lead.social_links.facebook && (
                    <Button
                      variant="outlined"
                      startIcon={<FacebookIcon />}
                      href={lead.social_links.facebook}
                      target="_blank"
                    >
                      Facebook
                    </Button>
                  )}
                  {lead.social_links.twitter && (
                    <Button
                      variant="outlined"
                      startIcon={<TwitterIcon />}
                      href={lead.social_links.twitter}
                      target="_blank"
                    >
                      Twitter
                    </Button>
                  )}
                  {lead.social_links.instagram && (
                    <Button
                      variant="outlined"
                      startIcon={<InstagramIcon />}
                      href={lead.social_links.instagram}
                      target="_blank"
                    >
                      Instagram
                    </Button>
                  )}
                  {lead.social_links.linkedin && (
                    <Button
                      variant="outlined"
                      startIcon={<LinkedInIcon />}
                      href={lead.social_links.linkedin}
                      target="_blank"
                    >
                      LinkedIn
                    </Button>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        )}

        {lead.business_hours && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Business Hours
                </Typography>
                <List>
                  {Object.entries(lead.business_hours).map(([day, hours]) => (
                    <ListItem key={day}>
                      <ListItemIcon>
                        <TimeIcon />
                      </ListItemIcon>
                      <ListItemText 
                        primary={day.charAt(0).toUpperCase() + day.slice(1)} 
                        secondary={`${hours.open} - ${hours.close}`} 
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
        )}

        {lead.description && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Description
                </Typography>
                <Typography>
                  {lead.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        )}

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Analysis
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle1" gutterBottom>
                    Tech Stack
                  </Typography>
                  <List>
                    <ListItem>
                      <ListItemText 
                        primary="Current Systems" 
                        secondary={lead.analysis.tech_stack.current_systems.join(', ')} 
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText 
                        primary="System Age" 
                        secondary={lead.analysis.tech_stack.system_age} 
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText 
                        primary="Score" 
                        secondary={
                          <Rating value={lead.analysis.tech_stack.score / 20} readOnly />
                        } 
                      />
                    </ListItem>
                  </List>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle1" gutterBottom>
                    Operations
                  </Typography>
                  <List>
                    <ListItem>
                      <ListItemText 
                        primary="Scale" 
                        secondary={lead.analysis.operations.scale} 
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText 
                        primary="Complexity" 
                        secondary={lead.analysis.operations.complexity} 
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText 
                        primary="Score" 
                        secondary={
                          <Rating value={lead.analysis.operations.score / 20} readOnly />
                        } 
                      />
                    </ListItem>
                  </List>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default LeadDetails; 