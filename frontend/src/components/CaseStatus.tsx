import type { ClinicalCase } from '../types';

interface CaseStatusProps {
  caseData: ClinicalCase | null;
}

const statusColors: Record<string, string> = {
  created: 'bg-gray-100 text-gray-800',
  analyzed: 'bg-blue-100 text-blue-800',
  suggestions_generated: 'bg-purple-100 text-purple-800',
  suggestions_confirmed: 'bg-indigo-100 text-indigo-800',
  adjustments_confirmed: 'bg-green-100 text-green-800',
  geometry_generated: 'bg-teal-100 text-teal-800',
  stl_exported: 'bg-emerald-100 text-emerald-800',
  feedback_collected: 'bg-cyan-100 text-cyan-800',
};

export const CaseStatus = ({ caseData }: CaseStatusProps) => {
  if (!caseData) {
    return (
      <div className="bg-gray-50 rounded-lg p-6 text-center">
        <p className="text-gray-500">Nenhum caso selecionado</p>
      </div>
    );
  }

  const statusColor = statusColors[caseData.status] || 'bg-gray-100 text-gray-800';

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">Informações do Caso</h2>

      {/* Case ID and Status */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div>
          <p className="text-sm text-gray-600">ID do Caso</p>
          <p className="text-lg font-semibold text-gray-800">{caseData.case_id}</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Status</p>
          <span className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${statusColor}`}>
            {caseData.status.replace(/_/g, ' ').toUpperCase()}
          </span>
        </div>
      </div>

      {/* Patient Info */}
      <div className="mb-6 pb-6 border-b">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">Informações do Paciente</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600">Nome</p>
            <p className="text-gray-800">{caseData.patient.name}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Idade / Gênero</p>
            <p className="text-gray-800">{caseData.patient.age} anos - {caseData.patient.gender === 'M' ? 'Masculino' : 'Feminino'}</p>
          </div>
          <div className="col-span-2">
            <p className="text-sm text-gray-600">Queixa Principal</p>
            <p className="text-gray-800">{caseData.patient.main_complaint}</p>
          </div>
        </div>
      </div>

      {/* Analysis Results */}
      {caseData.biomechanical_profile && (
        <div className="mb-6 pb-6 border-b">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">Análise Biomecânica</h3>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-gray-600">Índice do Arco</p>
              <p className="text-2xl font-bold text-blue-600">
                {caseData.biomechanical_profile.arch_index.toFixed(2)}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {caseData.biomechanical_profile.arch_index < 0.21 && '→ Pé Plano'}
                {caseData.biomechanical_profile.arch_index > 0.26 && '→ Pé Cavo'}
                {caseData.biomechanical_profile.arch_index >= 0.21 && caseData.biomechanical_profile.arch_index <= 0.26 && '→ Normal'}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Confiança da Análise</p>
              <p className="text-2xl font-bold text-green-600">
                {caseData.analysis_confidence ? (caseData.analysis_confidence * 100).toFixed(0) : '0'}%
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Qualidade do Scan</p>
              <p className="text-2xl font-bold text-purple-600">
                {caseData.biomechanical_profile.scan_quality ? (caseData.biomechanical_profile.scan_quality * 100).toFixed(0) : '0'}%
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Conditions Detected */}
      {caseData.primary_condition && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">Condição Detectada</h3>
          <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4">
            <p className="font-semibold text-blue-900">
              {caseData.primary_condition.replace(/_/g, ' ').toUpperCase()}
            </p>
            {caseData.suggestions.length > 0 && (
              <p className="text-sm text-blue-700 mt-1">
                Confiança: {(caseData.suggestions[0].confidence * 100).toFixed(0)}%
              </p>
            )}
          </div>
        </div>
      )}

      {/* Timestamps */}
      <div className="text-xs text-gray-500">
        <p>Criado em: {new Date(caseData.created_at).toLocaleString('pt-BR')}</p>
        <p>Atualizado em: {new Date(caseData.updated_at).toLocaleString('pt-BR')}</p>
      </div>
    </div>
  );
};
