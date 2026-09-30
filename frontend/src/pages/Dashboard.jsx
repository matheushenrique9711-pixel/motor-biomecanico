/**
 * Dashboard principal do Motor Biomecânico
 * Permite gerenciar casos clínicos e aplicar presets de condições de pé
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Dashboard.css';

const API_ORIGIN = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/+$/, '');
const API_URL = `${API_ORIGIN}/api`;

export default function Dashboard() {
  // Estado da aplicação
  const [activeTab, setActiveTab] = useState('presets');
  const [presets, setPresets] = useState([]);
  const [cases, setCases] = useState([]);
  const [selectedPreset, setSelectedPreset] = useState(null);
  const [selectedCase, setSelectedCase] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Carregar presets ao iniciar
  useEffect(() => {
    fetchPresets();
    fetchCases();
  }, []);

  // Buscar todos os presets
  const fetchPresets = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/presets/`);
      setPresets(response.data);
      setError(null);
    } catch (err) {
      setError(`Erro ao carregar presets: ${err.message}`);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Buscar todos os casos
  const fetchCases = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/cases/`);
      setCases(response.data.cases || []);
      setError(null);
    } catch (err) {
      setError(`Erro ao carregar casos: ${err.message}`);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Aplicar preset a um caso
  const applyPresetToCase = async (caseId, conditionName) => {
    setLoading(true);
    try {
      const response = await axios.post(
        `${API_URL}/presets/apply/${caseId}?condition_name=${encodeURIComponent(conditionName)}`
      );
      setSuccess(`Preset "${conditionName}" aplicado com sucesso ao caso ${caseId}`);
      fetchCases(); // Recarregar casos
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(`Erro ao aplicar preset: ${err.message}`);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Renderizar lista de presets
  const renderPresets = () => {
    if (loading) return <div className="loading">Carregando presets...</div>;
    if (presets.length === 0) return <div className="empty">Nenhum preset disponível</div>;

    // Agrupar por severidade
    const bySeverity = {};
    presets.forEach(preset => {
      if (!bySeverity[preset.severity_level]) {
        bySeverity[preset.severity_level] = [];
      }
      bySeverity[preset.severity_level].push(preset);
    });

    const severityOrder = ['leve', 'moderada', 'severa', 'máximo'];
    const severityLabels = {
      'leve': 'Leve',
      'moderada': 'Moderada',
      'severa': 'Severa',
      'máximo': 'Máximo'
    };

    return (
      <div className="presets-container">
        {severityOrder.map(severity =>
          bySeverity[severity] && (
            <div key={severity} className="severity-group">
              <h3 className={`severity-title severity-${severity}`}>
                {severityLabels[severity]}
              </h3>
              <div className="presets-grid">
                {bySeverity[severity].map(preset => (
                  <div
                    key={preset.id}
                    className={`preset-card ${selectedPreset?.id === preset.id ? 'active' : ''}`}
                    onClick={() => setSelectedPreset(preset)}
                  >
                    <div className="preset-header">
                      <h4>{preset.condition_name}</h4>
                      <span className={`severity-badge severity-${severity}`}>
                        {severityLabels[severity]}
                      </span>
                    </div>
                    <p className="preset-description">{preset.description}</p>

                    <div className="preset-details">
                      <div className="detail-item">
                        <span className="label">Suporte de Arco:</span>
                        <span className="value">{preset.arch_support_level}</span>
                      </div>
                      <div className="detail-item">
                        <span className="label">Altura Calcanhar:</span>
                        <span className="value">{preset.heel_height_mm}mm</span>
                      </div>
                      <div className="detail-item">
                        <span className="label">Material:</span>
                        <span className="value">{preset.material_recommendation}</span>
                      </div>
                    </div>

                    <div className="clinical-info">
                      <div className="info-section">
                        <h5>Indicadores Clínicos</h5>
                        <ul>
                          {preset.clinical_indicators.slice(0, 3).map((indicator, i) => (
                            <li key={i}>{indicator}</li>
                          ))}
                        </ul>
                      </div>
                      <div className="info-section">
                        <h5>Queixas Comuns</h5>
                        <ul>
                          {preset.common_complaints.slice(0, 3).map((complaint, i) => (
                            <li key={i}>{complaint}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )
        )}
      </div>
    );
  };

  // Renderizar lista de casos
  const renderCases = () => {
    if (loading) return <div className="loading">Carregando casos...</div>;
    if (cases.length === 0) return <div className="empty">Nenhum caso disponível</div>;

    return (
      <div className="cases-container">
        <div className="cases-list">
          {cases.map(caseItem => (
            <div
              key={caseItem.id}
              className={`case-card ${selectedCase?.id === caseItem.id ? 'active' : ''}`}
              onClick={() => setSelectedCase(caseItem)}
            >
              <div className="case-header">
                <h4>{caseItem.case_id}</h4>
                <span className={`status-badge status-${caseItem.status}`}>
                  {caseItem.status}
                </span>
              </div>
              <p className="case-patient">Paciente: {caseItem.patient_name || 'N/A'}</p>
              <p className="case-date">
                Criado em: {new Date(caseItem.created_at).toLocaleDateString('pt-BR')}
              </p>
            </div>
          ))}
        </div>

        {selectedCase && (
          <div className="case-details">
            <h3>Detalhes do Caso</h3>
            <div className="details-content">
              <div className="detail-row">
                <span className="label">ID do Caso:</span>
                <span className="value">{selectedCase.case_id}</span>
              </div>
              <div className="detail-row">
                <span className="label">Paciente:</span>
                <span className="value">{selectedCase.patient_name}</span>
              </div>
              <div className="detail-row">
                <span className="label">Status:</span>
                <span className={`status-badge status-${selectedCase.status}`}>
                  {selectedCase.status}
                </span>
              </div>
              <div className="detail-row">
                <span className="label">Condição Primária:</span>
                <span className="value">{selectedCase.primary_condition || 'Não definida'}</span>
              </div>

              <div className="apply-preset-section">
                <h4>Aplicar Preset de Condição</h4>
                <div className="preset-select">
                  {presets.map(preset => (
                    <button
                      key={preset.id}
                      className="preset-btn"
                      onClick={() => applyPresetToCase(selectedCase.case_id, preset.condition_name)}
                    >
                      {preset.condition_name}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  // Renderizar informações gerais
  const renderInfo = () => {
    return (
      <div className="info-page">
        <div className="info-card">
          <h3>📋 Presets de Condições de Pé</h3>
          <p>
            O sistema Motor Biomecânico possui {presets.length} presets pré-configurados para as
            condições de pé mais comuns. Cada preset contém:
          </p>
          <ul>
            <li>Descrição detalhada da condição</li>
            <li>Indicadores clínicos e queixas comuns</li>
            <li>Parâmetros de palmilha recomendados</li>
            <li>Altura de calcanhar otimizada</li>
            <li>Recomendação de material</li>
          </ul>
        </div>

        <div className="info-card">
          <h3>📊 Casos Clínicos</h3>
          <p>
            Gerencie todos os seus casos clínicos em um só lugar. Para cada caso você pode:
          </p>
          <ul>
            <li>Aplicar um preset de condição de pé</li>
            <li>Visualizar e editar parâmetros</li>
            <li>Acompanhar o status do caso</li>
            <li>Gerar geometria 3D</li>
            <li>Exportar arquivos STL</li>
          </ul>
        </div>

        <div className="info-card">
          <h3>🎯 Como Usar</h3>
          <ol>
            <li>Acesse a aba "Presets" para ver todas as condições disponíveis</li>
            <li>Clique em um preset para ver seus detalhes</li>
            <li>Vá para a aba "Casos" para ver seus casos clínicos</li>
            <li>Selecione um caso e aplique o preset apropriado</li>
            <li>Os parâmetros serão aplicados automaticamente</li>
          </ol>
        </div>

        <div className="stats">
          <div className="stat-card">
            <div className="stat-number">{presets.length}</div>
            <div className="stat-label">Presets Disponíveis</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{cases.length}</div>
            <div className="stat-label">Casos Clínicos</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">13</div>
            <div className="stat-label">Estados de Workflow</div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-content">
          <h1>🦵 Motor Biomecânico</h1>
          <p>Sistema de Palmilhas Ortopédicas 3D Customizadas</p>
        </div>
      </header>

      {/* Messages */}
      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      {/* Navigation */}
      <nav className="dashboard-nav">
        <button
          className={`nav-btn ${activeTab === 'info' ? 'active' : ''}`}
          onClick={() => setActiveTab('info')}
        >
          ℹ️ Informações
        </button>
        <button
          className={`nav-btn ${activeTab === 'presets' ? 'active' : ''}`}
          onClick={() => setActiveTab('presets')}
        >
          📋 Presets ({presets.length})
        </button>
        <button
          className={`nav-btn ${activeTab === 'cases' ? 'active' : ''}`}
          onClick={() => setActiveTab('cases')}
        >
          📊 Casos ({cases.length})
        </button>
      </nav>

      {/* Content */}
      <main className="dashboard-content">
        {activeTab === 'info' && renderInfo()}
        {activeTab === 'presets' && renderPresets()}
        {activeTab === 'cases' && renderCases()}
      </main>

      {/* Footer */}
      <footer className="dashboard-footer">
        <p>Motor Biomecânico v1.0 | Desenvolvido para otimizar o cuidado com os pés</p>
      </footer>
    </div>
  );
}
