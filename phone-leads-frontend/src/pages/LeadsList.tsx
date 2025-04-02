import React, { useEffect, useState } from 'react';
import { collection, getDocs } from 'firebase/firestore';
import {
  Box,
  Typography,
  TextField,
  MenuItem,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TablePagination,
  Rating,
} from '@mui/material';
import { db } from '../config/firebase';
import { Lead, PhoneLeadsData } from '../types/leads';
import { useNavigate } from 'react-router-dom';

const LeadsList: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [filteredLeads, setFilteredLeads] = useState<Lead[]>([]);
  const [cities, setCities] = useState<string[]>([]);
  const [businessTypes, setBusinessTypes] = useState<string[]>([]);
  
  // Filters
  const [selectedCity, setSelectedCity] = useState('all');
  const [selectedBusinessType, setSelectedBusinessType] = useState('all');
  const [minScore, setMinScore] = useState(0);
  
  // Pagination
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  useEffect(() => {
    const fetchLeads = async () => {
      try {
        console.log('🔍 Starting to fetch leads from Firestore...');
        const querySnapshot = await getDocs(collection(db, 'phoneLeads'));
        const data: PhoneLeadsData = {};
        
        querySnapshot.forEach((doc) => {
          data[doc.id] = doc.data() as any;
        });
        
        console.log('📥 Received data from Firestore');
        const allLeads: Lead[] = [];
        const uniqueCities = new Set<string>();
        const uniqueBusinessTypes = new Set<string>();

        Object.entries(data).forEach(([city, cityData]) => {
          console.log(`🏙️ Processing city: ${city}`);
          uniqueCities.add(city);
          
          Object.entries(cityData).forEach(([businessType, businessData]) => {
            console.log(`🏢 Processing business type: ${businessType}`);
            uniqueBusinessTypes.add(businessType);
            
            Object.values(businessData.leads).forEach((batch) => {
              console.log(`📦 Processing batch with ${batch.leads.length} leads`);
              batch.leads.forEach((lead) => {
                allLeads.push({
                  ...lead,
                  city,
                  category: businessType,
                });
              });
            });
          });
        });

        console.log(`✅ Total leads loaded: ${allLeads.length}`);
        console.log(`🏙️ Cities found: ${Array.from(uniqueCities).join(', ')}`);
        console.log(`🏢 Business types found: ${Array.from(uniqueBusinessTypes).join(', ')}`);

        setLeads(allLeads);
        setFilteredLeads(allLeads);
        setCities(Array.from(uniqueCities));
        setBusinessTypes(Array.from(uniqueBusinessTypes));
      } catch (error) {
        console.error('Error fetching leads:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchLeads();
  }, []);

  useEffect(() => {
    console.log('🔍 Applying filters...');
    let filtered = [...leads];
    
    if (selectedCity !== 'all') {
      filtered = filtered.filter((lead) => lead.city === selectedCity);
      console.log(`🏙️ Filtered by city: ${selectedCity}, remaining leads: ${filtered.length}`);
    }
    
    if (selectedBusinessType !== 'all') {
      filtered = filtered.filter((lead) => lead.category === selectedBusinessType);
      console.log(`🏢 Filtered by business type: ${selectedBusinessType}, remaining leads: ${filtered.length}`);
    }
    
    filtered = filtered.filter((lead) => lead.overall_score >= minScore);
    console.log(`⭐ Filtered by minimum score: ${minScore}, remaining leads: ${filtered.length}`);
    
    setFilteredLeads(filtered);
    setPage(0);
  }, [leads, selectedCity, selectedBusinessType, minScore]);

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
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
        Phone Leads
      </Typography>
      
      <Box display="flex" gap={2} mb={3}>
        <TextField
          select
          label="City"
          value={selectedCity}
          onChange={(e) => setSelectedCity(e.target.value)}
          sx={{ minWidth: 200 }}
        >
          <MenuItem value="all">All Cities</MenuItem>
          {cities.map((city) => (
            <MenuItem key={city} value={city}>
              {city}
            </MenuItem>
          ))}
        </TextField>
        
        <TextField
          select
          label="Business Type"
          value={selectedBusinessType}
          onChange={(e) => setSelectedBusinessType(e.target.value)}
          sx={{ minWidth: 200 }}
        >
          <MenuItem value="all">All Types</MenuItem>
          {businessTypes.map((type) => (
            <MenuItem key={type} value={type}>
              {type}
            </MenuItem>
          ))}
        </TextField>
        
        <TextField
          label="Minimum Score"
          type="number"
          value={minScore}
          onChange={(e) => setMinScore(Number(e.target.value))}
          sx={{ minWidth: 150 }}
        />
      </Box>

      <Typography variant="subtitle1" gutterBottom>
        Showing {filteredLeads.length} leads
      </Typography>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>City</TableCell>
              <TableCell>Category</TableCell>
              <TableCell>Phone</TableCell>
              <TableCell>Score</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredLeads
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((lead) => (
                <TableRow
                  key={`${lead.city}-${lead.category}-${lead.name}`}
                  hover
                  onClick={() => navigate(`/leads/${lead.city}/${lead.category}/${lead.name}`)}
                  sx={{ cursor: 'pointer' }}
                >
                  <TableCell>{lead.name}</TableCell>
                  <TableCell>{lead.city}</TableCell>
                  <TableCell>{lead.category}</TableCell>
                  <TableCell>{lead.phone}</TableCell>
                  <TableCell>
                    <Rating value={lead.overall_score / 20} readOnly />
                  </TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
      </TableContainer>

      <TablePagination
        component="div"
        count={filteredLeads.length}
        page={page}
        onPageChange={handleChangePage}
        rowsPerPage={rowsPerPage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        rowsPerPageOptions={[5, 10, 25]}
      />
    </Box>
  );
}

export default LeadsList; 