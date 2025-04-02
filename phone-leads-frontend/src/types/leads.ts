export interface Analysis {
  tech_stack: {
    current_systems: string[];
    system_age: string;
    limitations: string[];
    integration_challenges: string[];
    score: number;
  };
  operations: {
    scale: string;
    complexity: string;
    efficiency_level: string;
    manual_processes: string[];
    score: number;
  };
  growth_potential: {
    market_position: string;
    growth_indicators: string[];
    tech_readiness: string;
    score: number;
  };
  software_opportunity: {
    pain_points: string[];
    roi_areas: string[];
    integration_requirements: string[];
    score: number;
  };
  decision_maker: {
    stakeholders: string[];
    investment_signals: string[];
    contact_approach: string;
    score: number;
  };
  sales_conversation: {
    opening_points: string[];
    pain_points_to_discuss: string[];
    roi_examples: string[];
    solutions_to_propose: string[];
    questions_to_ask: string[];
  };
}

export interface Validation {
  is_legitimate: boolean;
  confidence_score: number;
  validation_points: string[];
  red_flags: string[];
  analysis_accuracy: {
    tech_stack: number;
    operations: number;
    growth_potential: number;
    software_opportunity: number;
  };
  recommendation: 'proceed' | 'investigate' | 'reject';
}

export interface Lead {
  name: string;
  phone: string;
  website?: string;
  email?: string;
  city: string;
  category: string;
  overall_score: number;
  address?: string;
  description?: string;
  reviews_count?: number;
  rating?: number;
  photos?: string[];
  social_links?: {
    facebook?: string;
    twitter?: string;
    instagram?: string;
    linkedin?: string;
  };
  business_hours?: {
    [key: string]: {
      open: string;
      close: string;
    };
  };
  analysis: Analysis;
  validation: Validation;
}

export interface LeadBatch {
  leads: Lead[];
  timestamp: number;
  status: string;
}

export interface BusinessTypeData {
  leads: {
    [batchId: string]: LeadBatch;
  };
}

export interface CityData {
  [businessType: string]: BusinessTypeData;
}

export interface PhoneLeadsData {
  [city: string]: CityData;
} 