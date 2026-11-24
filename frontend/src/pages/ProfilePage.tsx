import React, { useEffect, useState } from 'react';

import { UserProfile } from '../types';
import { profileService } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { toast } from 'react-hot-toast';
import { Save, Loader2, CheckCircle2 } from 'lucide-react';

const SEX_OPTIONS = [
  { value: 'MALE', label: 'Male' },
  { value: 'FEMALE', label: 'Female' },
];

const ACTIVITY_LEVELS = [
  { value: 'SEDENTARY', label: 'Sedentary (little or no exercise)' },
  { value: 'LIGHTLY_ACTIVE', label: 'Lightly Active (light exercise 1-3 days/week)' },
  { value: 'MODERATELY_ACTIVE', label: 'Moderately Active (moderate exercise 3-5 days/week)' },
  { value: 'VERY_ACTIVE', label: 'Very Active (hard exercise 6-7 days/week)' },
  { value: 'EXTREMELY_ACTIVE', label: 'Extremely Active (very hard exercise, physical job)' },
];

const DIETARY_PREFERENCES = [
  { value: 'VEGETARIAN', label: 'Vegetarian' },
  { value: 'VEGAN', label: 'Vegan' },
  { value: 'EGGETARIAN', label: 'Eggetarian (Vegetarian + eggs)' },
  { value: 'NON_VEGETARIAN', label: 'Non-Vegetarian' },
];

const WEIGHT_GOALS = [
  { value: 'MAINTAIN', label: 'Maintain Weight' },
  { value: 'LOSE', label: 'Lose Weight' },
  { value: 'GAIN', label: 'Gain Weight' },
];

const COOKING_SKILLS = [
  { value: 'BEGINNER', label: 'Beginner' },
  { value: 'INTERMEDIATE', label: 'Intermediate' },
  { value: 'ADVANCED', label: 'Advanced' },
];

const BUDGET_OPTIONS = [
  { value: 'LOW', label: 'Low (budget-conscious)' },
  { value: 'MEDIUM', label: 'Medium' },
  { value: 'HIGH', label: 'High (premium ingredients)' },
];

const MEAL_FREQUENCY_OPTIONS = [
  { value: 3, label: '3 meals/day' },
  { value: 4, label: '4 meals/day' },
  { value: 5, label: '5 meals/day' },
  { value: 6, label: '6 meals/day' },
];

export function ProfilePage() {
  // Keeps the shared auth context (and the sidebar completeness notice) in sync
  // after a save here.
  const { refreshProfile } = useAuth();
  const [profile, setProfile] = useState<Partial<UserProfile>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const data = await profileService.getProfile();
      setProfile(data);
    } catch (error) {
      toast.error('Failed to load profile');
    } finally {
      setIsLoading(false);
    }
  };

  const validateField = (name: string, value: any): string => {
    switch (name) {
      case 'age_years':
        if (value !== undefined && value !== null && (value < 1 || value > 120)) return 'Age must be between 1 and 120';
        break;
      case 'height_cm':
        if (value !== undefined && value !== null && (value < 50 || value > 250)) return 'Height must be between 50 and 250 cm';
        break;
      case 'weight_kg':
        if (value !== undefined && value !== null && (value < 20 || value > 300)) return 'Weight must be between 20 and 300 kg';
        break;
      case 'weight_change_rate_kg_per_week':
        if (value !== undefined && value !== null && (value < -1 || value > 1)) return 'Weight change rate must be between -1 and 1 kg/week';
        break;
      case 'time_constraint_minutes':
        if (value !== undefined && value !== null && (value < 5 || value > 300)) return 'Time constraint must be between 5 and 300 minutes';
        break;
    }
    return '';
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    const parsedValue = type === 'number' ? (value ? parseFloat(value) : undefined) : value;
    setProfile(prev => ({ ...prev, [name]: parsedValue }));
    const error = validateField(name, parsedValue);
    setErrors(prev => ({ ...prev, [name]: error }));
    setSaved(false);
  };

  const handleArrayChange = (name: string, value: string[]) => {
    setProfile(prev => ({ ...prev, [name]: value }));
    setSaved(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      await profileService.updateProfile(profile);
      await refreshProfile();
      toast.success('Profile saved successfully');
      setSaved(true);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to save profile');
    } finally {
      setIsSaving(false);
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

  return (
    <div className="page-container">
      <div className="max-w-3xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-neutral-900">My Profile</h1>
          <p className="text-neutral-600 mt-1">Manage your personal information and nutrition preferences</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Basic Info */}
          <section className="card p-6">
            <h2 className="text-lg font-semibold text-neutral-900 mb-6 flex items-center gap-2">
              <span className="w-8 h-8 rounded-lg bg-primary-100 flex items-center justify-center">
                <svg className="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </span>
              Basic Information
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="age_years" className="label">Age (years)</label>
                <input
                  id="age_years"
                  name="age_years"
                  type="number"
                  min="1"
                  max="120"
                  value={profile.age_years || ''}
                  onChange={handleChange}
                  className={`input-field ${errors.age_years ? 'input-error' : ''}`}
                />
                {errors.age_years && <p className="error-message">{errors.age_years}</p>}
              </div>
              <div>
                <label htmlFor="sex" className="label">Sex</label>
                <select
                  id="sex"
                  name="sex"
                  value={profile.sex || ''}
                  onChange={handleChange}
                  className="input-field"
                >
                  <option value="">Select sex</option>
                  {SEX_OPTIONS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
                </select>
              </div>
              <div>
                <label htmlFor="height_cm" className="label">Height (cm)</label>
                <input
                  id="height_cm"
                  name="height_cm"
                  type="number"
                  min="50"
                  max="250"
                  step="0.1"
                  value={profile.height_cm || ''}
                  onChange={handleChange}
                  className={`input-field ${errors.height_cm ? 'input-error' : ''}`}
                />
                {errors.height_cm && <p className="error-message">{errors.height_cm}</p>}
              </div>
              <div>
                <label htmlFor="weight_kg" className="label">Weight (kg)</label>
                <input
                  id="weight_kg"
                  name="weight_kg"
                  type="number"
                  min="20"
                  max="300"
                  step="0.1"
                  value={profile.weight_kg || ''}
                  onChange={handleChange}
                  className={`input-field ${errors.weight_kg ? 'input-error' : ''}`}
                />
                {errors.weight_kg && <p className="error-message">{errors.weight_kg}</p>}
              </div>
              <div>
                <label htmlFor="activity_level" className="label">Activity Level</label>
                <select
                  id="activity_level"
                  name="activity_level"
                  value={profile.activity_level || ''}
                  onChange={handleChange}
                  className="input-field"
                >
                  <option value="">Select activity level</option>
                  {ACTIVITY_LEVELS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
                </select>
              </div>
              <div>
                <label htmlFor="dietary_preference" className="label">Dietary Preference</label>
                <select
                  id="dietary_preference"
                  name="dietary_preference"
                  value={profile.dietary_preference || ''}
                  onChange={handleChange}
                  className="input-field"
                >
                  <option value="">Select dietary preference</option>
                  {DIETARY_PREFERENCES.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
                </select>
              </div>
            </div>
          </section>

          {/* Allergies & Exclusions */}
          <section className="card p-6">
            <h2 className="text-lg font-semibold text-neutral-900 mb-6 flex items-center gap-2">
              <span className="w-8 h-8 rounded-lg bg-red-100 flex items-center justify-center">
                <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </span>
              Allergies & Exclusions
            </h2>
            <div className="space-y-6">
              <div>
                <label className="label">Allergies</label>
                <TagInput
                  name="allergies"
                  value={profile.allergies || []}
                  onChange={handleArrayChange}
                  placeholder="Add allergies (e.g., peanuts, shellfish, dairy)"
                  suggestions={['peanuts', 'tree nuts', 'shellfish', 'fish', 'dairy', 'eggs', 'soy', 'wheat', 'sesame']}
                />
              </div>
              <div>
                <label className="label">Ingredient Exclusions</label>
                <TagInput
                  name="ingredient_exclusions"
                  value={profile.ingredient_exclusions || []}
                  onChange={handleArrayChange}
                  placeholder="Add ingredients to exclude"
                  suggestions={['onion', 'garlic', 'ginger', 'tomato', 'potato', 'eggplant', 'mushroom']}
                />
              </div>
            </div>
          </section>

          {/* Cuisine Preferences */}
          <section className="card p-6">
            <h2 className="text-lg font-semibold text-neutral-900 mb-6 flex items-center gap-2">
              <span className="w-8 h-8 rounded-lg bg-green-100 flex items-center justify-center">
                <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </span>
              Cuisine Preferences
            </h2>
            <div className="space-y-4">
              <div>
                <label className="label">Preferred Cuisines</label>
                <TagInput
                  name="cuisine_preferences"
                  value={profile.cuisine_preferences || []}
                  onChange={handleArrayChange}
                  placeholder="Add preferred cuisines"
                  suggestions={['North Indian', 'South Indian', 'Gujarati', 'Maharashtrian', 'Bengali', 'Punjabi', 'Rajasthani', 'Kerala', 'Andhra', 'Tamil', 'Kashmiri', 'Goan', 'Hyderabadi', 'Awadhi', 'Chettinad', 'Malvani']}
                />
              </div>
              <div>
                <label className="label">Excluded Cuisines</label>
                <TagInput
                  name="cuisine_exclusions"
                  value={profile.cuisine_exclusions || []}
                  onChange={handleArrayChange}
                  placeholder="Add cuisines to exclude"
                  suggestions={['North Indian', 'South Indian', 'Gujarati', 'Maharashtrian', 'Bengali', 'Punjabi', 'Rajasthani', 'Kerala', 'Andhra', 'Tamil', 'Kashmiri', 'Goan', 'Hyderabadi', 'Awadhi', 'Chettinad', 'Malvani']}
                />
              </div>
            </div>
          </section>

          {/* Religious & Medical */}
          <section className="card p-6">
            <h2 className="text-lg font-semibold text-neutral-900 mb-6 flex items-center gap-2">
              <span className="w-8 h-8 rounded-lg bg-yellow-100 flex items-center justify-center">
                <svg className="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </span>
              Restrictions & Conditions
            </h2>
            <div className="space-y-4">
              <div>
                <label className="label">Religious Restrictions</label>
                <TagInput
                  name="religious_restrictions"
                  value={profile.religious_restrictions || []}
                  onChange={handleArrayChange}
                  placeholder="Add religious restrictions"
                  suggestions={['Jain', 'Halal', 'Kosher', 'No beef', 'No pork', 'No alcohol', 'Fasting days']}
                />
              </div>
              <div>
                <label className="label">Medical Conditions</label>
                <TagInput
                  name="medical_conditions"
                  value={profile.medical_conditions || []}
                  onChange={handleArrayChange}
                  placeholder="Add medical conditions (for nutrition guidance)"
                  suggestions={['Diabetes', 'Hypertension', 'High cholesterol', 'Thyroid', 'PCOS', 'Celiac disease', 'Lactose intolerance', 'Gout', 'Kidney disease']}
                />
              </div>
              <div>
                <label className="label">Disliked Ingredients</label>
                <TagInput
                  name="disliked_ingredients"
                  value={profile.disliked_ingredients || []}
                  onChange={handleArrayChange}
                  placeholder="Add ingredients you dislike"
                  suggestions={['bitter gourd', 'okra', 'bottle gourd', 'fenugreek leaves', 'curry leaves', 'tamarind', 'coconut']}
                />
              </div>
            </div>
          </section>

          {/* Goals & Preferences */}
          <section className="card p-6">
            <h2 className="text-lg font-semibold text-neutral-900 mb-6 flex items-center gap-2">
              <span className="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center">
                <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </span>
              Goals & Preferences
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="weight_goal" className="label">Weight Goal</label>
                <select
                  id="weight_goal"
                  name="weight_goal"
                  value={profile.weight_goal || ''}
                  onChange={handleChange}
                  className="input-field"
                >
                  {WEIGHT_GOALS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
                </select>
              </div>
              <div>
                <label htmlFor="weight_change_rate_kg_per_week" className="label">Weight Change Rate (kg/week)</label>
                <input
                  id="weight_change_rate_kg_per_week"
                  name="weight_change_rate_kg_per_week"
                  type="number"
                  min="-1"
                  max="1"
                  step="0.1"
                  value={profile.weight_change_rate_kg_per_week || ''}
                  onChange={handleChange}
                  className={`input-field ${errors.weight_change_rate_kg_per_week ? 'input-error' : ''}`}
                />
                {errors.weight_change_rate_kg_per_week && <p className="error-message">{errors.weight_change_rate_kg_per_week}</p>}
              </div>
              <div>
                <label htmlFor="meal_frequency" className="label">Meals per Day</label>
                <select
                  id="meal_frequency"
                  name="meal_frequency"
                  value={profile.meal_frequency || ''}
                  onChange={handleChange}
                  className="input-field"
                >
                  {MEAL_FREQUENCY_OPTIONS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
                </select>
              </div>
              <div>
                <label htmlFor="cooking_skill" className="label">Cooking Skill</label>
                <select
                  id="cooking_skill"
                  name="cooking_skill"
                  value={profile.cooking_skill || ''}
                  onChange={handleChange}
                  className="input-field"
                >
                  {COOKING_SKILLS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
                </select>
              </div>
              <div>
                <label htmlFor="budget_constraint" className="label">Budget Constraint</label>
                <select
                  id="budget_constraint"
                  name="budget_constraint"
                  value={profile.budget_constraint || ''}
                  onChange={handleChange}
                  className="input-field"
                >
                  <option value="">Select budget</option>
                  {BUDGET_OPTIONS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
                </select>
              </div>
              <div>
                <label htmlFor="time_constraint_minutes" className="label">Max Cooking Time (minutes)</label>
                <input
                  id="time_constraint_minutes"
                  name="time_constraint_minutes"
                  type="number"
                  min="5"
                  max="300"
                  value={profile.time_constraint_minutes || ''}
                  onChange={handleChange}
                  className={`input-field ${errors.time_constraint_minutes ? 'input-error' : ''}`}
                />
                {errors.time_constraint_minutes && <p className="error-message">{errors.time_constraint_minutes}</p>}
              </div>
            </div>
          </section>

          {/* Preferred Meal Times */}
          <section className="card p-6">
            <h2 className="text-lg font-semibold text-neutral-900 mb-6 flex items-center gap-2">
              <span className="w-8 h-8 rounded-lg bg-purple-100 flex items-center justify-center">
                <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </span>
              Preferred Meal Times
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {['breakfast', 'lunch', 'dinner', 'snack'].map(meal => (
                <div key={meal}>
                  <label htmlFor={`preferred_meal_times_${meal}`} className="label capitalize">{meal}</label>
                  <input
                    id={`preferred_meal_times_${meal}`}
                    name={`preferred_meal_times_${meal}`}
                    type="time"
                    value={profile.preferred_meal_times?.[meal] || ''}
                    onChange={(e) => handleChange({ ...e, target: { ...e.target, name: `preferred_meal_times.${meal}` } } as any)}
                    className="input-field"
                  />
                </div>
              ))}
            </div>
          </section>

          {/* Save Button */}
          <div className="flex justify-end gap-4">
            <button
              type="submit"
              disabled={isSaving}
              className="btn-primary"
            >
              {isSaving ? (
                <>
                  <Loader2 className="animate-spin mr-2 h-5 w-5" />
                  Saving...
                </>
              ) : saved ? (
                <>
                  <CheckCircle2 className="mr-2 h-5 w-5" />
                  Saved
                </>
              ) : (
                <>
                  <Save className="mr-2 h-5 w-5" />
                  Save Profile
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function TagInput({
  name,
  value,
  onChange,
  placeholder,
  suggestions = [],
}: {
  name: string;
  value: string[];
  onChange: (name: string, value: string[]) => void;
  placeholder: string;
  suggestions: string[];
}) {
  const [inputValue, setInputValue] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);

  const handleAdd = () => {
    if (inputValue.trim() && !value.includes(inputValue.trim())) {
      onChange(name, [...value, inputValue.trim()]);
      setInputValue('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAdd();
    } else if (e.key === 'Escape') {
      setShowSuggestions(false);
    }
  };

  return (
    <div className="relative">
      <div className="flex flex-wrap gap-2 min-h-[44px] p-2 border border-neutral-300 rounded-lg bg-white focus-within:ring-2 focus-within:ring-primary-500 focus-within:border-transparent">
        {value.map((tag, index) => (
          <span key={index} className="inline-flex items-center gap-1 px-3 py-1 bg-primary-50 text-primary-700 rounded-full text-sm">
            {tag}
            <button
              type="button"
              onClick={() => onChange(name, value.filter((_, i) => i !== index))}
              className="hover:bg-primary-100 rounded-full p-0.5"
              aria-label={`Remove ${tag}`}
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </span>
        ))}
        <input
          type="text"
          value={inputValue}
          onChange={e => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setShowSuggestions(true)}
          onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
          placeholder={value.length === 0 ? placeholder : ''}
          className="flex-1 min-w-[120px] border-none focus:outline-none text-sm"
        />
      </div>
      {showSuggestions && inputValue && (
        <div className="absolute z-10 mt-1 w-full max-h-40 overflow-y-auto bg-white border border-neutral-300 rounded-lg shadow-lg">
          {suggestions
            .filter(s => s.toLowerCase().includes(inputValue.toLowerCase()) && !value.includes(s))
            .slice(0, 10)
            .map(suggestion => (
              <button
                key={suggestion}
                type="button"
                onClick={() => {
                  if (!value.includes(suggestion)) {
                    onChange(name, [...value, suggestion]);
                    setInputValue('');
                  }
                }}
                className="w-full px-3 py-2 text-left text-sm hover:bg-neutral-50"
              >
                {suggestion}
              </button>
            ))}
        </div>
      )}
    </div>
  );
}

export default ProfilePage;