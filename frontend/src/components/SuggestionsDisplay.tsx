import type { ClinicalSuggestion } from '../types';

interface SuggestionsDisplayProps {
  suggestions: ClinicalSuggestion[];
  onApply: () => void;
  loading: boolean;
}

const conditionColors: Record<string, string> = {
  flatfoot: 'bg-red-50 border-red-200',
  cavusfoot: 'bg-blue-50 border-blue-200',
  hallux_valgus: 'bg-purple-50 border-purple-200',
  excessive_pronation: 'bg-yellow-50 border-yellow-200',
  metatarsalgia: 'bg-orange-50 border-orange-200',
};

const conditionNames: Record<string, string> = {
  flatfoot: 'Pé Plano',
  cavusfoot: 'Pé Cavo',
  hallux_valgus: 'Joanete (Hálux Valgo)',
  excessive_pronation: 'Pronação Excessiva',
  metatarsalgia: 'Metatarsalgia',
};

export const SuggestionsDisplay = ({ suggestions, onApply, loading }: SuggestionsDisplayProps) => {
  if (!suggestions.length) {
    return (
      <div className="bg-gray-50 rounded-lg p-6 text-center text-gray-500">
        <p>Nenhuma sugestão disponível</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-2xl font-bold text-gray-800">Sugestões Clínicas</h3>

      {suggestions.map((suggestion) => {
        const colorClass = conditionColors[suggestion.condition_type] || 'bg-gray-50 border-gray-200';
        const displayName = conditionNames[suggestion.condition_type] || suggestion.condition_name;

        return (
          <div key={suggestion.suggestion_id} className={`border-2 rounded-lg p-6 ${colorClass}`}>
            {/* Header */}
            <div className="flex justify-between items-start mb-4">
              <div>
                <h4 className="text-xl font-bold text-gray-800">{displayName}</h4>
                <p className="text-sm text-gray-600">Regra: {suggestion.applied_rules.join(', ')}</p>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-blue-600">{(suggestion.confidence * 100).toFixed(0)}%</div>
                <p className="text-xs text-gray-600">Confiança</p>
              </div>
            </div>

            {/* Rationale */}
            <div className="mb-4 p-3 bg-white bg-opacity-50 rounded">
              <p className="text-sm text-gray-700">{suggestion.clinical_rationale}</p>
            </div>

            {/* Parameter Adjustments */}
            <div className="mb-4">
              <h5 className="font-semibold text-gray-800 mb-3">Ajustes de Parâmetros Recomendados:</h5>
              <div className="space-y-2">
                {suggestion.parameter_adjustments.map((adjustment, idx) => (
                  <div key={idx} className="bg-white bg-opacity-50 p-3 rounded border-l-4 border-blue-400">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <p className="font-medium text-gray-800">
                          {adjustment.parameter_name.replace(/_/g, ' ').toUpperCase()}
                        </p>
                        <p className="text-sm text-gray-600">{adjustment.reason}</p>
                      </div>
                      <div className="text-right ml-4">
                        <p className="text-lg font-bold text-green-600">{adjustment.suggested_value}</p>
                        <p className="text-xs text-gray-500">
                          Range: {adjustment.min_safe_value} - {adjustment.max_safe_value}
                        </p>
                      </div>
                    </div>
                    <div className="mt-2">
                      <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                        Prioridade {adjustment.priority}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        );
      })}

      <button
        onClick={onApply}
        disabled={loading}
        className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-bold py-3 px-4 rounded-md transition duration-200"
      >
        {loading ? 'Aplicando ajustes...' : 'Aplicar Sugestões'}
      </button>
    </div>
  );
};
