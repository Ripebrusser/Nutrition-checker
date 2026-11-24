import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { toast } from 'react-hot-toast';
import { Save, Loader2, Moon, Sun, Monitor, Bell, Shield, Database, Palette, CheckCircle2 } from 'lucide-react';

export function PreferencesPage() {
  const { user } = useAuth();
  const [preferences, setPreferences] = useState({
    theme: 'system',
    sidebarCollapsed: false,
    compactMode: false,
    notifications: {
      email: true,
      mealReminders: true,
      weeklyReport: true,
      recommendations: false,
    },
    privacy: {
      analytics: true,
      crashReporting: true,
      dataSharing: false,
    },
    units: {
      weight: 'kg',
      height: 'cm',
      energy: 'kcal',
    },
    language: 'en',
  });
  const [isSaving, setIsSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleChange = (key: string, value: any) => {
    setPreferences(prev => {
      const current = (prev as Record<string, any>)[key];
      return {
        ...prev,
        [key]: typeof current === 'object' ? { ...current, ...value } : value,
      };
    });
    setSaved(false);
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      // Save to localStorage for now
      localStorage.setItem('user_preferences', JSON.stringify(preferences));
      toast.success('Preferences saved');
      setSaved(true);
    } catch {
      toast.error('Failed to save preferences');
    } finally {
      setIsSaving(false);
    }
  };

  const handleReset = () => {
    if (confirm('Reset all preferences to defaults?')) {
      const defaults = {
        theme: 'system',
        sidebarCollapsed: false,
        compactMode: false,
        notifications: {
          email: true,
          mealReminders: true,
          weeklyReport: true,
          recommendations: false,
        },
        privacy: {
          analytics: true,
          crashReporting: true,
          dataSharing: false,
        },
        units: {
          weight: 'kg',
          height: 'cm',
          energy: 'kcal',
        },
        language: 'en',
      };
      setPreferences(defaults);
      localStorage.removeItem('user_preferences');
      toast.success('Preferences reset to defaults');
    }
  };

  const loadPreferences = () => {
    try {
      const stored = localStorage.getItem('user_preferences');
      if (stored) {
        setPreferences(JSON.parse(stored));
      }
    } catch {
      // Ignore
    }
  };

  React.useEffect(() => {
    loadPreferences();
  }, []);

  return (
    <div className="page-container">
      <div className="max-w-3xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-neutral-900">Preferences</h1>
          <p className="text-neutral-600 mt-1">Customize your experience and manage settings</p>
        </div>

        {/* Appearance */}
        <section className="card p-6 mb-6">
          <h2 className="text-lg font-semibold text-neutral-900 mb-6 flex items-center gap-2">
            <Palette className="w-5 h-5 text-primary-600" />
            Appearance
          </h2>
          <div className="space-y-6">
            <div>
              <label className="label">Theme</label>
              <div className="grid grid-cols-3 gap-3">
                {[
                  { value: 'light', label: 'Light', icon: Sun },
                  { value: 'dark', label: 'Dark', icon: Moon },
                  { value: 'system', label: 'System', icon: Monitor },
                ].map(opt => (
                  <button
                    key={opt.value}
                    type="button"
                    onClick={() => handleChange('theme', opt.value)}
                    className={`p-4 rounded-lg border-2 text-center transition-all ${
                      preferences.theme === opt.value
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-neutral-200 hover:border-neutral-300'
                    }`}
                  >
                    <opt.icon className="w-6 h-6 mx-auto mb-2" />
                    <span className="font-medium">{opt.label}</span>
                  </button>
                ))}
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <label className="flex items-center gap-3 p-3 bg-neutral-50 rounded-lg cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.sidebarCollapsed}
                  onChange={e => handleChange('sidebarCollapsed', e.target.checked)}
                  className="w-4 h-4 rounded border-neutral-300 text-primary-600 focus:ring-2 focus:ring-primary-500"
                />
                <span className="text-neutral-900">Collapse sidebar by default</span>
              </label>
              <label className="flex items-center gap-3 p-3 bg-neutral-50 rounded-lg cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.compactMode}
                  onChange={e => handleChange('compactMode', e.target.checked)}
                  className="w-4 h-4 rounded border-neutral-300 text-primary-600 focus:ring-2 focus:ring-primary-500"
                />
                <span className="text-neutral-900">Compact mode (denser layout)</span>
              </label>
            </div>
          </div>
        </section>

        {/* Notifications */}
        <section className="card p-6 mb-6">
          <h2 className="text-lg font-semibold text-neutral-900 mb-6 flex items-center gap-2">
            <Bell className="w-5 h-5 text-primary-600" />
            Notifications
          </h2>
          <div className="space-y-4">
            {[
              { key: 'email', label: 'Email notifications', desc: 'Receive important updates via email' },
              { key: 'mealReminders', label: 'Meal reminders', desc: 'Get notified before planned meal times' },
              { key: 'weeklyReport', label: 'Weekly nutrition report', desc: 'Weekly summary of your nutrition intake' },
              { key: 'recommendations', label: 'New recommendations', desc: 'Alert when new personalized recipes are available' },
            ].map(item => (
              <label key={item.key} className="flex items-start gap-3 p-3 bg-neutral-50 rounded-lg cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.notifications[item.key as keyof typeof preferences.notifications]}
                  onChange={e => handleChange('notifications', { [item.key]: e.target.checked })}
                  className="w-4 h-4 mt-0.5 rounded border-neutral-300 text-primary-600 focus:ring-2 focus:ring-primary-500"
                />
                <div>
                  <p className="font-medium text-neutral-900">{item.label}</p>
                  <p className="text-sm text-neutral-500">{item.desc}</p>
                </div>
              </label>
            ))}
          </div>
        </section>

        {/* Privacy */}
        <section className="card p-6 mb-6">
          <h2 className="text-lg font-semibold text-neutral-900 mb-6 flex items-center gap-2">
            <Shield className="w-5 h-5 text-primary-600" />
            Privacy & Data
          </h2>
          <div className="space-y-4">
            {[
              { key: 'analytics', label: 'Usage analytics', desc: 'Help improve the app with anonymous usage data' },
              { key: 'crashReporting', label: 'Crash reporting', desc: 'Automatically send error reports for debugging' },
              { key: 'dataSharing', label: 'Data sharing', desc: 'Allow anonymized data to be used for research' },
            ].map(item => (
              <label key={item.key} className="flex items-start gap-3 p-3 bg-neutral-50 rounded-lg cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.privacy[item.key as keyof typeof preferences.privacy]}
                  onChange={e => handleChange('privacy', { [item.key]: e.target.checked })}
                  className="w-4 h-4 mt-0.5 rounded border-neutral-300 text-primary-600 focus:ring-2 focus:ring-primary-500"
                />
                <div>
                  <p className="font-medium text-neutral-900">{item.label}</p>
                  <p className="text-sm text-neutral-500">{item.desc}</p>
                </div>
              </label>
            ))}
          </div>
        </section>

        {/* Units */}
        <section className="card p-6 mb-6">
          <h2 className="text-lg font-semibold text-neutral-900 mb-6 flex items-center gap-2">
            <Database className="w-5 h-5 text-primary-600" />
            Units & Language
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label htmlFor="weightUnit" className="label">Weight Unit</label>
              <select
                id="weightUnit"
                value={preferences.units.weight}
                onChange={e => handleChange('units', { weight: e.target.value })}
                className="input-field"
              >
                <option value="kg">Kilograms (kg)</option>
                <option value="lb">Pounds (lb)</option>
              </select>
            </div>
            <div>
              <label htmlFor="heightUnit" className="label">Height Unit</label>
              <select
                id="heightUnit"
                value={preferences.units.height}
                onChange={e => handleChange('units', { height: e.target.value })}
                className="input-field"
              >
                <option value="cm">Centimeters (cm)</option>
                <option value="ft">Feet/Inches (ft/in)</option>
              </select>
            </div>
            <div>
              <label htmlFor="energyUnit" className="label">Energy Unit</label>
              <select
                id="energyUnit"
                value={preferences.units.energy}
                onChange={e => handleChange('units', { energy: e.target.value })}
                className="input-field"
              >
                <option value="kcal">Kilocalories (kcal)</option>
                <option value="kJ">Kilojoules (kJ)</option>
              </select>
            </div>
          </div>
          <div className="mt-4">
            <label htmlFor="language" className="label">Language</label>
            <select
              id="language"
              value={preferences.language}
              onChange={e => handleChange('language', e.target.value)}
              className="input-field w-auto"
            >
              <option value="en">English</option>
              <option value="hi">Hindi (हिंदी)</option>
              <option value="ta">Tamil (தமிழ்)</option>
              <option value="te">Telugu (తెలుగు)</option>
              <option value="kn">Kannada (ಕನ್ನಡ)</option>
              <option value="ml">Malayalam (മലയാളം)</option>
              <option value="bn">Bengali (বাংলা)</option>
              <option value="gu">Gujarati (ગુજરાતી)</option>
              <option value="mr">Marathi (मराठी)</option>
              <option value="pa">Punjabi (ਪੰਜਾਬੀ)</option>
            </select>
          </div>
        </section>

        {/* Data Management */}
        <section className="card p-6 mb-6 border-red-200 bg-red-50">
          <h2 className="text-lg font-semibold text-red-800 mb-4 flex items-center gap-2">
            <Database className="w-5 h-5" />
            Data Management
          </h2>
          <div className="space-y-3 text-sm text-red-700">
            <p>All your data is stored locally on your device:</p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>User profiles and preferences: SQLite database</li>
              <li>Meal plans and history: SQLite database</li>
              <li>Saved recipes: SQLite database</li>
              <li>UI preferences: localStorage</li>
              <li>Recipe cache: none - no offline cache is implemented</li>
            </ul>
            <div className="flex gap-2 pt-2">
              <button className="btn-secondary text-sm">
                Export Data (JSON)
              </button>
              <button className="btn-secondary text-sm">
                Import Data
              </button>
              <button className="btn-ghost text-red-600 hover:text-red-700 text-sm">
                Delete All Data
              </button>
            </div>
          </div>
        </section>

        {/* Actions */}
        <div className="flex justify-end gap-4">
          <button onClick={handleReset} className="btn-secondary">
            Reset to Defaults
          </button>
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="btn-primary"
          >
            {isSaving ? (
              <>
                <Loader2 className="animate-spin mr-2 w-5 h-5" />
                Saving...
              </>
            ) : saved ? (
              <>
                <CheckCircle2 className="mr-2 w-5 h-5" />
                Saved
              </>
            ) : (
              <>
                <Save className="mr-2 w-5 h-5" />
                Save Preferences
              </>
            )}
          </button>
        </div>

        {/* Account Info */}
        <div className="mt-12 card p-6">
          <h2 className="text-lg font-semibold text-neutral-900 mb-4">Account Information</h2>
          <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <dt className="text-sm text-neutral-500">Email</dt>
              <dd className="font-medium text-neutral-900">{user?.email}</dd>
            </div>
            <div>
              <dt className="text-sm text-neutral-500">Name</dt>
              <dd className="font-medium text-neutral-900">{user?.full_name}</dd>
            </div>
            <div>
              <dt className="text-sm text-neutral-500">Role</dt>
              <dd className="font-medium text-neutral-900 capitalize">{user?.role?.toLowerCase()}</dd>
            </div>
            <div>
              <dt className="text-sm text-neutral-500">Member since</dt>
              <dd className="font-medium text-neutral-900">Account created locally</dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  );
}

export default PreferencesPage;