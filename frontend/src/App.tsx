import { useState } from 'react';
import { useCase } from './hooks/useCase';
import {
  PatientIntakeForm,
  BiomechanicalAnalysis,
  SuggestionsDisplay,
  CaseStatus,
  Visualization3D,
} from './components';
import type { CreateCaseRequest, AnalyzeRequest } from './types';
import './App.css';

type WorkflowStep = 'intake' | 'analysis' | 'suggestions' | 'geometry' | 'completed';

function App() {
  const [step, setStep] = useState<WorkflowStep>('intake');
  const {
    currentCase,
    loading,
    error,
    createCase,
    analyzeBiomechanical,
    generateSuggestions,
    applyAdjustments,
    generateGeometry,
  } = useCase();

  const handleCreateCase = async (patientData: CreateCaseRequest) => {
    try {
      await createCase(patientData);
      setStep('analysis');
    } catch (err) {
      console.error('Erro ao criar caso:', err);
    }
  };

  const handleAnalyze = async (biomechanicalData: AnalyzeRequest) => {
    try {
      await analyzeBiomechanical(biomechanicalData);
      await generateSuggestions();
      setStep('suggestions');
    } catch (err) {
      console.error('Erro na análise:', err);
    }
  };

  const handleApplySuggestions = async () => {
    try {
      if (currentCase?.suggestions.length && currentCase.suggestions[0].parameter_adjustments) {
        const adjustments: Record<string, any> = {};
        currentCase.suggestions.forEach((suggestion) => {
          suggestion.parameter_adjustments.forEach((adj) => {
            adjustments[adj.parameter_name] = adj.suggested_value;
          });
        });

        await applyAdjustments(adjustments);
        setStep('geometry');
      }
    } catch (err) {
      console.error('Erro ao aplicar ajustes:', err);
    }
  };

  const handleGenerateGeometry = async () => {
    try {
      await generateGeometry();
      setStep('completed');
    } catch (err) {
      console.error('Erro ao gerar geometria:', err);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-4xl font-bold text-gray-800">
            🦶 Motor Biomecânico
          </h1>
          <p className="text-gray-600 mt-2">
            Sistema de Análise e Personalização de Palmilhas Ortopédicas
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Progress Indicator */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            {(['intake', 'analysis', 'suggestions', 'geometry', 'completed'] as WorkflowStep[]).map(
              (s, idx) => (
                <div key={s} className="flex items-center">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                      step === s
                        ? 'bg-blue-600 text-white'
                        : step > s
                          ? 'bg-green-600 text-white'
                          : 'bg-gray-300 text-gray-600'
                    }`}
                  >
                    {idx + 1}
                  </div>
                  {idx < 4 && (
                    <div
                      className={`h-1 w-12 mx-2 ${
                        step > s ? 'bg-green-600' : 'bg-gray-300'
                      }`}
                    />
                  )}
                </div>
              )
            )}
          </div>
          <div className="flex justify-between text-sm text-gray-600">
            <span>Cadastro</span>
            <span>Análise</span>
            <span>Sugestões</span>
            <span>Geometria 3D</span>
            <span>Conclusão</span>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-100 border border-red-400 rounded-lg">
            <p className="text-red-800 font-semibold">Erro:</p>
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            {step === 'intake' && (
              <PatientIntakeForm
                onSubmit={handleCreateCase}
                loading={loading}
              />
            )}

            {step === 'analysis' && currentCase && (
              <BiomechanicalAnalysis
                onSubmit={handleAnalyze}
                loading={loading}
              />
            )}

            {step === 'suggestions' && currentCase && (
              <SuggestionsDisplay
                suggestions={currentCase.suggestions}
                onApply={handleApplySuggestions}
                loading={loading}
              />
            )}

            {step === 'geometry' && currentCase && (
              <div className="space-y-6">
                <Visualization3D
                  title="Visualização 3D da Palmilha"
                  stlUrl={currentCase.stl_file_path || undefined}
                />

                <button
                  onClick={handleGenerateGeometry}
                  disabled={loading}
                  className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-bold py-3 px-4 rounded-md transition duration-200"
                >
                  {loading ? 'Gerando...' : 'Prosseguir para Conclusão'}
                </button>
              </div>
            )}

            {step === 'completed' && currentCase && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="text-center mb-6">
                  <div className="text-6xl mb-4">✅</div>
                  <h2 className="text-3xl font-bold text-green-600 mb-2">
                    Caso Processado com Sucesso!
                  </h2>
                  <p className="text-gray-600">
                    Os parâmetros da palmilha foram aplicados. Próxima etapa: exportação 3D.
                  </p>
                </div>

                <div className="bg-green-50 border-2 border-green-200 rounded-lg p-6 mb-6">
                  <h3 className="font-semibold text-green-900 mb-3">Próximos Passos:</h3>
                  <ul className="list-disc list-inside space-y-2 text-green-800">
                    <li>Exportar geometria 3D (STL)</li>
                    <li>Revisar com o paciente</li>
                    <li>Encaminhar para impressão 3D</li>
                    <li>Agendar ajustes finais</li>
                  </ul>
                </div>

                <button
                  onClick={() => setStep('intake')}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-md transition duration-200"
                >
                  Iniciar Novo Caso
                </button>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <CaseStatus caseData={currentCase} />

            {/* Quick Stats */}
            {currentCase && (
              <div className="mt-6 bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-bold text-gray-800 mb-4">Resumo Rápido</h3>
                <div className="space-y-3">
                  <div>
                    <p className="text-xs text-gray-600">Status do Caso</p>
                    <p className="font-semibold text-gray-800">
                      {currentCase.status.replace(/_/g, ' ').toUpperCase()}
                    </p>
                  </div>
                  {currentCase.primary_condition && (
                    <div>
                      <p className="text-xs text-gray-600">Condição Primária</p>
                      <p className="font-semibold text-gray-800">
                        {currentCase.primary_condition.replace(/_/g, ' ').toUpperCase()}
                      </p>
                    </div>
                  )}
                  {currentCase.suggestions.length > 0 && (
                    <div>
                      <p className="text-xs text-gray-600">Sugestões Disponíveis</p>
                      <p className="font-semibold text-gray-800">
                        {currentCase.suggestions.length} sugestão(s)
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 py-6 text-center text-gray-600">
          <p>Quiropraxia Pinheiros © 2026 | Motor Biomecânico v1.0</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
