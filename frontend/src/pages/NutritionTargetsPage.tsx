import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { NutritionTargets } from '../types';
import { nutritionService } from '../services/api';
import { toast } from 'react-hot-toast';
import { Loader2, AlertCircle, Info, Calculator, TrendingUp, Target, Leaf, Flame, Dumbbell } from 'lucide-react';
import { Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';

const MACRO_COLORS = {
  protein: '#ef4444',
  fat: '#f59e0b',
  carbohydrate: '#3b82f6',
  fibre: '#22c55e',
};

export function NutritionTargetsPage() {
  const { profile } = useAuth();
  const [targets, setTargets] = useState<NutritionTargets | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isCalculating, setIsCalculating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTargets();
  }, []);

  const loadTargets = async () => {
    try {
      setIsLoading(true);
      const data = await nutritionService.getTargets();
      setTargets(data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load nutrition targets');
    } finally {
      setIsLoading(false);
    }
  };

  const recalculateTargets = async () => {
    if (!profile) return;
    try {
      setIsCalculating(true);
      const data = await nutritionService.calculateTargets({
        age_years: profile.age_years,
        sex: profile.sex,
        height_cm: profile.height_cm,
        weight_kg: profile.weight_kg,
        activity_level: profile.activity_level,
        weight_goal: profile.weight_goal,
        weight_change_rate_kg_per_week: profile.weight_change_rate_kg_per_week,
      });
      setTargets(data);
      toast.success('Nutrition targets recalculated');
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to recalculate targets');
    } finally {
      setIsCalculating(false);
    }
  };

  if (isLoading) {
    return (
      <div className="page-container">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="animate-spin h-8 w-8 text-primary-600" />
        </div>
      </div>
    );
  }

  if (error || !targets) {
    return (
      <div className="page-container">
        <div className="max-w-2xl mx-auto text-center py-16">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-neutral-900 mb-2">Unable to Load Nutrition Targets</h2>
          <p className="text-neutral-600 mb-6">{error || 'Please complete your profile to calculate nutrition targets.'}</p>
          <button onClick={loadTargets} className="btn-primary">
            Retry
          </button>
        </div>
      </div>
    );
  }

  const macroData = [
    { name: 'Protein', value: targets.protein_g, color: MACRO_COLORS.protein, calories: targets.protein_g * 4 },
    { name: 'Fat', value: targets.fat_g, color: MACRO_COLORS.fat, calories: targets.fat_g * 9 },
    { name: 'Carbohydrates', value: targets.carbohydrate_g, color: MACRO_COLORS.carbohydrate, calories: targets.carbohydrate_g * 4 },
  ];

  const totalMacroCalories = macroData.reduce((sum, m) => sum + m.calories, 0);
  const macroPercentages = macroData.map(m => ({
    ...m,
    percentage: totalMacroCalories > 0 ? ((m.calories / totalMacroCalories) * 100).toFixed(1) : '0',
  }));

  return (
    <div className="page-container">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900">Nutrition Targets</h1>
          <p className="text-neutral-600 mt-1">Your personalized daily nutrition goals based on ICMR 2020 guidelines</p>
        </div>
        <button
          onClick={recalculateTargets}
          disabled={isCalculating}
          className="btn-secondary"
        >
          <Calculator className="w-4 h-4 mr-2" />
          {isCalculating ? 'Calculating...' : 'Recalculate'}
        </button>
      </div>

      {/* Energy Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <EnergyCard
          icon={<Flame className="w-6 h-6 text-orange-600" />}
          label="BMR"
          value={`${targets.bmr_kcal.toFixed(0)} kcal`}
          description="Basal Metabolic Rate"
        />
        <EnergyCard
          icon={<TrendingUp className="w-6 h-6 text-red-600" />}
          label="TDEE"
          value={`${targets.tdee_kcal.toFixed(0)} kcal`}
          description="Total Daily Energy Expenditure"
        />
        <EnergyCard
          icon={<Target className="w-6 h-6 text-green-600" />}
          label="Daily Target"
          value={`${targets.target_energy_kcal.toFixed(0)} kcal`}
          description="Adjusted for weight goal"
        />
        <EnergyCard
          icon={<Dumbbell className="w-6 h-6 text-purple-600" />}
          label="Protein Target"
          value={`${targets.protein_g.toFixed(0)} g`}
          description={`~${((targets.protein_g * 4 / targets.target_energy_kcal) * 100).toFixed(0)}% of calories`}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Macro Distribution Chart */}
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
            <Leaf className="w-5 h-5 text-green-600" />
            Macronutrient Distribution
          </h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={macroPercentages}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                  dataKey="value"
                  nameKey="name"
                  label={({ name, percentage }) => `${name}: ${percentage}%`}
                  labelLine={false}
                >
                  {macroPercentages.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value: number) => [`${value}g`, 'Grams']} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-4 gap-4 mt-6">
            {macroPercentages.map(m => (
              <div key={m.name} className="text-center p-3 bg-neutral-50 rounded-lg">
                <div className="w-3 h-3 rounded-full mx-auto mb-1" style={{ backgroundColor: m.color }} />
                <p className="text-sm font-medium text-neutral-900">{m.name}</p>
                <p className="text-lg font-bold text-neutral-900">{m.value}g</p>
                <p className="text-xs text-neutral-500">{m.percentage}% kcal</p>
              </div>
            ))}
          </div>
        </div>

        {/* Micronutrients */}
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
            <Leaf className="w-5 h-5 text-green-600" />
            Micronutrient Targets
          </h2>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {Object.entries(targets.micronutrients).map(([nutrient, data]) => (
              <div key={nutrient} className="flex items-center justify-between p-3 bg-neutral-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-green-500" />
                  <span className="font-medium text-neutral-900 capitalize">{nutrient.replace('_', ' ')}</span>
                </div>
                <div className="text-right">
                  <p className="font-bold text-neutral-900">{data.target} {data.unit}</p>
                  <p className="text-xs text-neutral-500">ICMR 2020 RDA</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Detailed Targets Table */}
      <div className="card overflow-hidden mb-8">
        <div className="p-6 border-b border-neutral-200">
          <h2 className="text-lg font-semibold text-neutral-900">Detailed Targets</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-neutral-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-500 uppercase tracking-wider">Nutrient</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-500 uppercase tracking-wider">Target</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-500 uppercase tracking-wider">Unit</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-500 uppercase tracking-wider">% of Calories</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-200">
              <tr className="hover:bg-neutral-50">
                <td className="px-6 py-4">Energy</td>
                <td className="px-6 py-4 font-medium">{targets.target_energy_kcal.toFixed(0)}</td>
                <td className="px-6 py-4">kcal</td>
                <td className="px-6 py-4">100%</td>
              </tr>
              <tr className="hover:bg-neutral-50">
                <td className="px-6 py-4">Protein</td>
                <td className="px-6 py-4 font-medium">{targets.protein_g.toFixed(1)}</td>
                <td className="px-6 py-4">g</td>
                <td className="px-6 py-4">{((targets.protein_g * 4 / targets.target_energy_kcal) * 100).toFixed(1)}%</td>
              </tr>
              <tr className="hover:bg-neutral-50">
                <td className="px-6 py-4">Fat</td>
                <td className="px-6 py-4 font-medium">{targets.fat_g.toFixed(1)}</td>
                <td className="px-6 py-4">g</td>
                <td className="px-6 py-4">{((targets.fat_g * 9 / targets.target_energy_kcal) * 100).toFixed(1)}%</td>
              </tr>
              <tr className="hover:bg-neutral-50">
                <td className="px-6 py-4">Carbohydrates</td>
                <td className="px-6 py-4 font-medium">{targets.carbohydrate_g.toFixed(1)}</td>
                <td className="px-6 py-4">g</td>
                <td className="px-6 py-4">{((targets.carbohydrate_g * 4 / targets.target_energy_kcal) * 100).toFixed(1)}%</td>
              </tr>
              <tr className="hover:bg-neutral-50">
                <td className="px-6 py-4">Fibre</td>
                <td className="px-6 py-4 font-medium">{targets.fibre_g.toFixed(1)}</td>
                <td className="px-6 py-4">g</td>
                <td className="px-6 py-4">—</td>
              </tr>
              <tr className="hover:bg-neutral-50">
                <td className="px-6 py-4">Sodium</td>
                <td className="px-6 py-4 font-medium">{targets.sodium_mg.toFixed(0)}</td>
                <td className="px-6 py-4">mg</td>
                <td className="px-6 py-4">—</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Calculation Methodology */}
      <div className="card p-6 mb-8">
        <h2 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
          <Info className="w-5 h-5 text-blue-600" />
          Calculation Methodology & Limitations
        </h2>
        <div className="prose prose-neutral max-w-none text-sm">
          <h4 className="font-semibold text-neutral-900 mb-2">Methodology</h4>
          <ul className="list-disc list-inside space-y-1 text-neutral-600 mb-4">
            <li><strong>BMR:</strong> Mifflin-St Jeor equation (gold standard)</li>
            <li><strong>TDEE:</strong> BMR × Physical Activity Level (PAL) factor</li>
            <li><strong>Target Energy:</strong> TDEE adjusted for weight goal (±500 kcal for 0.5 kg/week)</li>
            <li><strong>Protein:</strong> ICMR 2020 RDA (0.83 g/kg) adjusted for activity and goals</li>
            <li><strong>Fat:</strong> 25-30% of total calories (ICMR range)</li>
            <li><strong>Carbohydrates:</strong> Remainder after protein and fat</li>
            <li><strong>Fibre:</strong> ICMR 2020 (25g/day women, 30g/day men)</li>
            <li><strong>Micronutrients:</strong> ICMR 2020 RDA values</li>
          </ul>
          <h4 className="font-semibold text-neutral-900 mb-2">Limitations</h4>
          <ul className="list-disc list-inside space-y-1 text-neutral-600">
            {targets.limitations.map((limitation, i) => (
              <li key={i}>{limitation}</li>
            ))}
            <li>Individual requirements may vary based on genetics, health conditions, and metabolic factors</li>
            <li>Consult a registered dietitian or healthcare provider for personalized advice</li>
          </ul>
        </div>
      </div>

      {/* Profile Completeness Warning */}
      {!profile?.age_years || !profile?.sex || !profile?.height_cm || !profile?.weight_kg || !profile?.activity_level ? (
        <div className="card p-6 border-yellow-200 bg-yellow-50">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5" />
            <div>
              <h3 className="font-semibold text-yellow-800 mb-1">Profile Incomplete</h3>
              <p className="text-yellow-700">
                Nutrition targets are based on default assumptions. Please complete your profile
                (age, sex, height, weight, activity level) for accurate personalized targets.
              </p>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}

function EnergyCard({ icon, label, value, description }: {
  icon: React.ReactNode;
  label: string;
  value: string;
  description: string;
}) {
  return (
    <div className="card p-6">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-neutral-500">{label}</p>
          <p className="text-2xl font-bold text-neutral-900 mt-1">{value}</p>
          <p className="text-sm text-neutral-500 mt-1">{description}</p>
        </div>
        <div className="w-12 h-12 rounded-xl bg-primary-100 flex items-center justify-center">
          {icon}
        </div>
      </div>
    </div>
  );
}

export default NutritionTargetsPage;