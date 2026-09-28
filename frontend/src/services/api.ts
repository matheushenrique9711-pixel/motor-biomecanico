import axios, { AxiosInstance } from 'axios';
import type {
  CreateCaseRequest,
  AnalyzeRequest,
  ApplyAdjustmentsRequest,
  FeedbackRequest,
  ClinicalCase,
} from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // ========== Cases ==========

  async createCase(data: CreateCaseRequest): Promise<ClinicalCase> {
    const response = await this.client.post('/cases/', data);
    return response.data;
  }

  async getCase(caseId: string): Promise<ClinicalCase> {
    const response = await this.client.get(`/cases/${caseId}`);
    return response.data;
  }

  async listCases(): Promise<ClinicalCase[]> {
    const response = await this.client.get('/cases/');
    return response.data;
  }

  async getPatientCases(patientId: string): Promise<ClinicalCase[]> {
    const response = await this.client.get(`/cases/patient/${patientId}/cases`);
    return response.data;
  }

  // ========== Analysis ==========

  async analyzeBiomechanical(caseId: string, data: AnalyzeRequest): Promise<ClinicalCase> {
    const response = await this.client.post(`/cases/${caseId}/analyze`, data);
    return response.data;
  }

  // ========== Suggestions ==========

  async generateSuggestions(caseId: string): Promise<ClinicalCase> {
    const response = await this.client.post(`/cases/${caseId}/suggestions`);
    return response.data;
  }

  async confirmSuggestions(
    caseId: string,
    clinicianId: string,
    clinicianNotes: string
  ): Promise<ClinicalCase> {
    const response = await this.client.post(`/cases/${caseId}/confirm-suggestions`, {
      clinician_id: clinicianId,
      clinician_notes: clinicianNotes,
    });
    return response.data;
  }

  // ========== Parameters & Adjustments ==========

  async applyAdjustments(
    caseId: string,
    adjustments: ApplyAdjustmentsRequest
  ): Promise<ClinicalCase> {
    const response = await this.client.post(`/cases/${caseId}/apply-adjustments`, adjustments);
    return response.data;
  }

  // ========== Geometry Generation ==========

  async generateGeometry(caseId: string): Promise<any> {
    const response = await this.client.post(`/cases/${caseId}/generate-geometry`);
    return response.data;
  }

  async exportSTL(caseId: string): Promise<any> {
    const response = await this.client.post(`/cases/${caseId}/export-stl`);
    return response.data;
  }

  // ========== Feedback ==========

  async submitFeedback(caseId: string, feedback: FeedbackRequest): Promise<ClinicalCase> {
    const response = await this.client.post(`/cases/${caseId}/feedback`, feedback);
    return response.data;
  }

  // ========== Analytics ==========

  async getStatistics(): Promise<any> {
    const response = await this.client.get('/cases/statistics/summary');
    return response.data;
  }

  async getHealth(): Promise<any> {
    const response = await this.client.get('/cases/health');
    return response.data;
  }
}

export const apiClient = new ApiClient();
export default apiClient;
