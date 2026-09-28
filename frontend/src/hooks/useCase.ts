import { useState, useCallback } from 'react';
import { apiClient } from '../services/api';
import type { ClinicalCase, CreateCaseRequest } from '../types';

export const useCase = () => {
  const [currentCase, setCurrentCase] = useState<ClinicalCase | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createCase = useCallback(async (patientData: CreateCaseRequest) => {
    setLoading(true);
    setError(null);
    try {
      const newCase = await apiClient.createCase(patientData);
      setCurrentCase(newCase);
      return newCase;
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Erro ao criar caso';
      setError(errorMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getCase = useCallback(async (caseId: string) => {
    setLoading(true);
    setError(null);
    try {
      const caseData = await apiClient.getCase(caseId);
      setCurrentCase(caseData);
      return caseData;
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Erro ao carregar caso';
      setError(errorMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const analyzeBiomechanical = useCallback(
    async (biomechanicalData: any) => {
      if (!currentCase) throw new Error('Nenhum caso selecionado');
      setLoading(true);
      setError(null);
      try {
        const updatedCase = await apiClient.analyzeBiomechanical(currentCase.case_id, biomechanicalData);
        setCurrentCase(updatedCase);
        return updatedCase;
      } catch (err: any) {
        const errorMsg = err.response?.data?.detail || err.message || 'Erro na análise';
        setError(errorMsg);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [currentCase]
  );

  const generateSuggestions = useCallback(async () => {
    if (!currentCase) throw new Error('Nenhum caso selecionado');
    setLoading(true);
    setError(null);
    try {
      const updatedCase = await apiClient.generateSuggestions(currentCase.case_id);
      setCurrentCase(updatedCase);
      return updatedCase;
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Erro ao gerar sugestões';
      setError(errorMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [currentCase]);

  const applyAdjustments = useCallback(
    async (adjustments: any) => {
      if (!currentCase) throw new Error('Nenhum caso selecionado');
      setLoading(true);
      setError(null);
      try {
        const updatedCase = await apiClient.applyAdjustments(currentCase.case_id, adjustments);
        setCurrentCase(updatedCase);
        return updatedCase;
      } catch (err: any) {
        const errorMsg = err.response?.data?.detail || err.message || 'Erro ao aplicar ajustes';
        setError(errorMsg);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [currentCase]
  );

  const generateGeometry = useCallback(async () => {
    if (!currentCase) throw new Error('Nenhum caso selecionado');
    setLoading(true);
    setError(null);
    try {
      const result = await apiClient.generateGeometry(currentCase.case_id);
      // Atualiza o caso com o path do STL gerado
      const updatedCase = { ...currentCase, stl_file_path: result.stl_file_path };
      setCurrentCase(updatedCase);
      return result;
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Erro ao gerar geometria';
      setError(errorMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [currentCase]);

  const exportSTL = useCallback(async () => {
    if (!currentCase) throw new Error('Nenhum caso selecionado');
    setLoading(true);
    setError(null);
    try {
      const result = await apiClient.exportSTL(currentCase.case_id);
      return result;
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Erro ao exportar STL';
      setError(errorMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [currentCase]);

  return {
    currentCase,
    setCurrentCase,
    loading,
    error,
    createCase,
    getCase,
    analyzeBiomechanical,
    generateSuggestions,
    applyAdjustments,
    generateGeometry,
    exportSTL,
  };
};
