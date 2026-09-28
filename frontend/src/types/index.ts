// ========== API Response Types ==========

export interface PatientInfo {
  patient_id: string;
  name: string;
  age: number;
  gender: 'M' | 'F';
  main_complaint: string;
  medical_history?: string;
  current_medications?: string;
  phone?: string;
  email?: string;
}

export interface LoadDistribution {
  hallux_zone: number;
  medial_metatarsal: number;
  central_metatarsal: number;
  lateral_metatarsal: number;
  heel_zone: number;
}

export interface BiomechanicalFootProfile {
  foot_length: number;
  arch_length_midfoot: number;
  forefoot_width: number;
  midfoot_width: number;
  hindfoot_width: number;
  arch_height_at_50pct: number;
  arch_height_at_midfoot: number;
  arch_index: number;
  hallux_valgus_angle: number;
  intermetatarsal_angle: number;
  subtalar_inversion_angle: number;
  tibial_torsion_asymmetry: number;
  load_distribution: LoadDistribution;
  left_right_asymmetry: number;
  scan_quality: number;
}

export interface ParameterAdjustment {
  parameter_name: string;
  suggested_value: number;
  min_safe_value: number;
  max_safe_value: number;
  reason: string;
  priority: number;
}

export interface ClinicalSuggestion {
  suggestion_id: string;
  condition_type: string;
  condition_name: string;
  confidence: number;
  clinical_rationale: string;
  parameter_adjustments: ParameterAdjustment[];
  applied_rules: string[];
  is_confirmed: boolean;
  requires_confirmation: boolean;
  confirmation_notes?: string;
}

export interface ClinicalCase {
  case_id: string;
  patient: PatientInfo;
  status: string;
  created_at: string;
  updated_at: string;
  biomechanical_profile?: BiomechanicalFootProfile;
  analysis_confidence?: number;
  suggestions: ClinicalSuggestion[];
  primary_condition?: string;
  insole_parameters?: Record<string, any>;
  stl_file_path?: string;
  clinical_feedback?: string;
  patient_feedback?: string;
}

export interface CreateCaseRequest {
  patient_id: string;
  name: string;
  age: number;
  gender: string;
  main_complaint: string;
}

export interface AnalyzeRequest {
  foot_length: number;
  arch_length_midfoot: number;
  forefoot_width: number;
  midfoot_width: number;
  hindfoot_width: number;
  arch_height_at_50pct: number;
  arch_height_at_midfoot: number;
  arch_index: number;
  hallux_valgus_angle: number;
  intermetatarsal_angle: number;
  subtalar_inversion_angle: number;
  tibial_torsion_asymmetry: number;
  load_distribution: LoadDistribution;
  left_right_asymmetry: number;
  scan_quality: number;
}

export interface ApplyAdjustmentsRequest {
  [key: string]: any;
}

export interface FeedbackRequest {
  clinical_feedback?: string;
  patient_feedback?: string;
  effectiveness_score?: number;
  comfort_score?: number;
  should_be_learning_case?: boolean;
}
