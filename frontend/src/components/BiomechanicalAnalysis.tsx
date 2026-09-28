import { useState } from 'react';
import type { AnalyzeRequest } from '../types';

interface BiomechanicalAnalysisProps {
  onSubmit: (data: AnalyzeRequest) => void;
  loading: boolean;
}

export const BiomechanicalAnalysis = ({ onSubmit, loading }: BiomechanicalAnalysisProps) => {
  const [formData, setFormData] = useState<AnalyzeRequest>({
    foot_length: 250.0,
    arch_length_midfoot: 120.0,
    forefoot_width: 95.0,
    midfoot_width: 85.0,
    hindfoot_width: 65.0,
    arch_height_at_50pct: 20.0,
    arch_height_at_midfoot: 22.0,
    arch_index: 0.22,
    hallux_valgus_angle: 0.0,
    intermetatarsal_angle: 0.0,
    subtalar_inversion_angle: 0.0,
    tibial_torsion_asymmetry: 0.0,
    load_distribution: {
      hallux_zone: 0.15,
      medial_metatarsal: 0.20,
      central_metatarsal: 0.25,
      lateral_metatarsal: 0.15,
      heel_zone: 0.25,
    },
    left_right_asymmetry: 0.0,
    scan_quality: 0.95,
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    const numValue = parseFloat(value);
    setFormData(prev => ({
      ...prev,
      [name]: numValue,
    }));
  };

  const handleLoadDistributionChange = (zone: keyof typeof formData.load_distribution, value: string) => {
    setFormData(prev => ({
      ...prev,
      load_distribution: {
        ...prev.load_distribution,
        [zone]: parseFloat(value),
      },
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Análise Biomecânica</h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Medidas do Pé */}
        <div>
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Medidas do Pé (mm)</h3>
          <div className="grid grid-cols-3 gap-4">
            {[
              { name: 'foot_length', label: 'Comprimento do Pé' },
              { name: 'arch_length_midfoot', label: 'Comprimento do Arco' },
              { name: 'forefoot_width', label: 'Largura Antepé' },
              { name: 'midfoot_width', label: 'Largura Médio Pé' },
              { name: 'hindfoot_width', label: 'Largura Retropé' },
            ].map(({ name, label }) => (
              <div key={name}>
                <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
                <input
                  type="number"
                  name={name}
                  value={(formData as any)[name]}
                  onChange={handleChange}
                  step="0.1"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            ))}
          </div>
        </div>

        {/* Altura do Arco */}
        <div>
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Altura do Arco (mm)</h3>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Altura @ 50%</label>
              <input
                type="number"
                name="arch_height_at_50pct"
                value={formData.arch_height_at_50pct}
                onChange={handleChange}
                step="0.1"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Altura @ Midfoot</label>
              <input
                type="number"
                name="arch_height_at_midfoot"
                value={formData.arch_height_at_midfoot}
                onChange={handleChange}
                step="0.1"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Índice do Arco</label>
              <input
                type="number"
                name="arch_index"
                value={formData.arch_index}
                onChange={handleChange}
                step="0.01"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Ângulos */}
        <div>
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Ângulos (graus)</h3>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Ângulo Hálux Valgo</label>
              <input
                type="number"
                name="hallux_valgus_angle"
                value={formData.hallux_valgus_angle}
                onChange={handleChange}
                step="0.1"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Ângulo Intermetatarsiano</label>
              <input
                type="number"
                name="intermetatarsal_angle"
                value={formData.intermetatarsal_angle}
                onChange={handleChange}
                step="0.1"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Ângulo Subtalar</label>
              <input
                type="number"
                name="subtalar_inversion_angle"
                value={formData.subtalar_inversion_angle}
                onChange={handleChange}
                step="0.1"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Distribuição de Carga */}
        <div>
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Distribuição de Carga (%)</h3>
          <div className="grid grid-cols-5 gap-4">
            {Object.entries(formData.load_distribution).map(([zone, value]) => (
              <div key={zone}>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {zone.replace(/_/g, ' ').toUpperCase()}
                </label>
                <input
                  type="number"
                  value={value}
                  onChange={(e) => handleLoadDistributionChange(zone as any, e.target.value)}
                  step="0.01"
                  min="0"
                  max="1"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            ))}
          </div>
        </div>

        {/* Qualidade do Scan */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Qualidade do Scan (0-1)</label>
          <input
            type="number"
            name="scan_quality"
            value={formData.scan_quality}
            onChange={handleChange}
            step="0.01"
            min="0"
            max="1"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-bold py-2 px-4 rounded-md transition duration-200"
        >
          {loading ? 'Analisando...' : 'Analisar Biomecânica'}
        </button>
      </form>
    </div>
  );
};
