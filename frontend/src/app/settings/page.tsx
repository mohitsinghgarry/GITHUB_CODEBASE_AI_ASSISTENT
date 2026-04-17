'use client';

import { useState, useEffect } from 'react';
import { AppShell } from '@/components/layout/AppShell';
import { useSettingsStore } from '@/store/settingsStore';
import { api, type AvailableModels, type Settings as BackendSettings } from '@/lib/api';

export default function SettingsPage() {
  // Backend settings state
  const [availableModels, setAvailableModels] = useState<AvailableModels | null>(null);
  const [backendSettings, setBackendSettings] = useState<BackendSettings | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  
  // Local state for form
  const [activeModel, setActiveModel] = useState('openai/gpt-oss-120b');
  const [embeddingModel, setEmbeddingModel] = useState('sentence-transformers/all-MiniLM-L6-v2');
  const [temperature, setTemperature] = useState(0.7);
  const [editorFont, setEditorFont] = useState('JetBrains Mono');
  
  // Use the actual settings store for theme and font size
  const theme = useSettingsStore((state) => state.theme);
  const fontSize = useSettingsStore((state) => state.fontSize);
  const setTheme = useSettingsStore((state) => state.setTheme);
  const setFontSize = useSettingsStore((state) => state.setFontSize);
  
  // Map fontSize to UI labels
  const fontSizeMap: Record<string, 'xs' | 'sm' | 'base' | 'lg' | 'xl'> = {
    small: 'sm',
    medium: 'base',
    large: 'lg',
  };
  
  const fontSizeReverseMap: Record<string, string> = {
    xs: 'small',
    sm: 'small',
    base: 'medium',
    lg: 'large',
    xl: 'large',
  };
  
  const uiFontSize = fontSizeReverseMap[fontSize] || 'medium';

  // Load available models and current settings on mount
  useEffect(() => {
    const loadSettings = async () => {
      try {
        setIsLoading(true);
        const [models, settings] = await Promise.all([
          api.getAvailableModels(),
          api.getSettings(),
        ]);
        
        setAvailableModels(models);
        setBackendSettings(settings);
        
        // Update local form state
        setActiveModel(settings.llm_model);
        setEmbeddingModel(settings.embedding_model);
        setTemperature(settings.temperature);
        
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load settings');
      } finally {
        setIsLoading(false);
      }
    };
    
    loadSettings();
  }, []);

  const handleSaveSettings = async () => {
    try {
      setIsSaving(true);
      setError(null);
      setSuccessMessage(null);
      
      const updatedSettings = await api.updateSettings({
        llm_model: activeModel,
        embedding_model: embeddingModel,
        temperature: temperature,
      });
      
      setBackendSettings(updatedSettings);
      setSuccessMessage('Settings saved successfully!');
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <AppShell>
      <div className="flex h-full overflow-hidden">
        {/* Settings Sub-Navigation */}
        <nav className="w-64 bg-surface flex flex-col p-6 space-y-2 border-r border-outline-variant/10">
          <h3 className="text-[10px] font-bold text-outline uppercase tracking-widest px-3 mb-2">
            Configuration
          </h3>
          <a
            href="#"
            className="flex items-center gap-3 px-3 py-2 text-on-surface-variant hover:bg-surface-container-low rounded transition-colors"
          >
            <span className="material-symbols-outlined text-lg">tune</span>
            <span className="text-sm">General</span>
          </a>
          <a
            href="#"
            className="flex items-center gap-3 px-3 py-2 bg-surface-container text-primary rounded transition-colors border border-outline-variant/5"
          >
            <span className="material-symbols-outlined text-lg">smart_toy</span>
            <span className="text-sm font-medium">Model Configuration</span>
          </a>
          <a
            href="#"
            className="flex items-center gap-3 px-3 py-2 text-on-surface-variant hover:bg-surface-container-low rounded transition-colors"
          >
            <span className="material-symbols-outlined text-lg">source</span>
            <span className="text-sm">Repository</span>
          </a>
          <a
            href="#"
            className="flex items-center gap-3 px-3 py-2 text-on-surface-variant hover:bg-surface-container-low rounded transition-colors"
          >
            <span className="material-symbols-outlined text-lg">palette</span>
            <span className="text-sm">Appearance</span>
          </a>
          <div className="pt-6">
            <h3 className="text-[10px] font-bold text-outline uppercase tracking-widest px-3 mb-2">
              Technical
            </h3>
            <a
              href="#"
              className="flex items-center gap-3 px-3 py-2 text-on-surface-variant hover:bg-surface-container-low rounded transition-colors"
            >
              <span className="material-symbols-outlined text-lg">key</span>
              <span className="text-sm">API Keys</span>
            </a>
            <a
              href="#"
              className="flex items-center gap-3 px-3 py-2 text-on-surface-variant hover:bg-surface-container-low rounded transition-colors"
            >
              <span className="material-symbols-outlined text-lg">shield</span>
              <span className="text-sm">Security</span>
            </a>
          </div>
        </nav>

        {/* Main Scrollable Content */}
        <div className="flex-1 overflow-y-auto bg-surface-container-low/30 scroll-smooth">
          {isLoading ? (
            <div className="flex items-center justify-center h-full">
              <div className="animate-spin rounded-full h-12 w-12 border-2 border-primary border-t-transparent"></div>
            </div>
          ) : (
            <div className="max-w-4xl mx-auto p-12 space-y-16">
              {/* Header Section */}
              <section>
                <h2 className="text-3xl font-bold tracking-tight text-on-surface mb-2">
                  Settings
                </h2>
                <p className="text-on-surface-variant">
                  Manage your AI intelligence parameters and workspace preferences.
                </p>
                
                {/* Error/Success Messages */}
                {error && (
                  <div className="mt-4 p-4 bg-error/10 border border-error/20 rounded-xl flex items-start gap-3">
                    <span className="material-symbols-outlined text-error">error</span>
                    <p className="text-sm text-error">{error}</p>
                  </div>
                )}
                
                {successMessage && (
                  <div className="mt-4 p-4 bg-tertiary/10 border border-tertiary/20 rounded-xl flex items-start gap-3">
                    <span className="material-symbols-outlined text-tertiary">check_circle</span>
                    <p className="text-sm text-tertiary">{successMessage}</p>
                  </div>
                )}
              </section>

              {/* Model Config Section */}
              <section className="space-y-6">
                <div className="flex items-center gap-3 border-b border-outline-variant/10 pb-4">
                  <span className="material-symbols-outlined text-primary text-xl">
                    smart_toy
                  </span>
                  <h3 className="text-xl font-semibold">Model Configuration</h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-on-surface">
                      Active LLM
                    </label>
                    <div className="relative">
                      <select
                        value={activeModel}
                        onChange={(e) => setActiveModel(e.target.value)}
                        className="w-full bg-surface-container-high border-none rounded-lg text-sm px-4 py-3 appearance-none focus:ring-1 focus:ring-primary/30 text-on-surface"
                      >
                        {availableModels?.llm_models.map((model) => (
                          <option key={model.id} value={model.id}>
                            {model.name}
                          </option>
                        ))}
                      </select>
                      <div className="absolute inset-y-0 right-3 flex items-center pointer-events-none">
                        <div className="w-2 h-2 rounded-full bg-tertiary shadow-[0_0_8px_rgba(105,246,184,0.4)] mr-2"></div>
                        <span className="material-symbols-outlined text-outline">
                          expand_more
                        </span>
                      </div>
                    </div>
                    <p className="text-[11px] text-on-surface-variant">
                      {availableModels?.llm_models.find(m => m.id === activeModel)?.description || 'High-reasoning model for complex tasks.'}
                    </p>
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-on-surface">
                      Embedding Model
                    </label>
                    <select
                      value={embeddingModel}
                      onChange={(e) => setEmbeddingModel(e.target.value)}
                      className="w-full bg-surface-container-high border-none rounded-lg text-sm px-4 py-3 focus:ring-1 focus:ring-primary/30 text-on-surface"
                    >
                      {availableModels?.embedding_models.map((model) => (
                        <option key={model.id} value={model.id}>
                          {model.name}
                        </option>
                      ))}
                    </select>
                    <p className="text-[11px] text-on-surface-variant">
                      {availableModels?.embedding_models.find(m => m.id === embeddingModel)?.description || 'Determines vector search accuracy for codebase context.'}
                    </p>
                  </div>
                </div>

                <div className="bg-surface-container p-6 rounded-xl space-y-4">
                  <div className="flex justify-between items-center">
                    <label className="text-sm font-medium text-on-surface">
                      Creativity (Temperature)
                    </label>
                    <span className="text-sm font-mono text-primary bg-primary/10 px-2 py-0.5 rounded">
                      {temperature.toFixed(1)}
                    </span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={temperature}
                    onChange={(e) => setTemperature(parseFloat(e.target.value))}
                    className="w-full h-1"
                  />
                  <div className="flex justify-between text-[10px] text-outline uppercase tracking-wider font-bold">
                    <span>Precise</span>
                    <span>Balanced</span>
                    <span>Creative</span>
                  </div>
                </div>
              </section>

              {/* Appearance Section */}
              <section className="space-y-6">
                <div className="flex items-center gap-3 border-b border-outline-variant/10 pb-4">
                  <span className="material-symbols-outlined text-secondary text-xl">
                    palette
                  </span>
                  <h3 className="text-xl font-semibold">Appearance</h3>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  {/* Light Mode Card */}
                  <div
                    className="group cursor-pointer"
                    onClick={() => setTheme('light')}
                  >
                    <div
                      className={`h-24 bg-on-background border-2 ${
                        theme === 'light'
                          ? 'border-primary shadow-[0_0_15px_rgba(163,166,255,0.1)]'
                          : 'border-transparent group-hover:border-outline-variant/20'
                      } rounded-lg mb-2 relative overflow-hidden transition-all`}
                    >
                      <div className="absolute top-2 left-2 w-8 h-2 bg-surface-container-highest/20 rounded"></div>
                      <div className="absolute top-6 left-2 w-12 h-1 bg-surface-container-highest/10 rounded"></div>
                      <div className="absolute bottom-2 right-2 w-4 h-4 bg-primary/20 rounded-full"></div>
                    </div>
                    <span
                      className={`text-xs block text-center ${
                        theme === 'light'
                          ? 'text-primary font-medium'
                          : 'text-on-surface-variant'
                      }`}
                    >
                      {theme === 'light' ? 'Light (Active)' : 'Light'}
                    </span>
                  </div>

                  {/* Dark Mode Card */}
                  <div
                    className="group cursor-pointer"
                    onClick={() => setTheme('dark')}
                  >
                    <div
                      className={`h-24 bg-surface-container border-2 ${
                        theme === 'dark'
                          ? 'border-primary shadow-[0_0_15px_rgba(163,166,255,0.1)]'
                          : 'border-transparent group-hover:border-outline-variant/20'
                      } rounded-lg mb-2 relative overflow-hidden transition-all`}
                    >
                      <div className="absolute top-2 left-2 w-8 h-2 bg-on-surface-variant/20 rounded"></div>
                      <div className="absolute top-6 left-2 w-12 h-1 bg-on-surface-variant/10 rounded"></div>
                      <div className="absolute bottom-2 right-2 w-4 h-4 bg-primary rounded-full"></div>
                    </div>
                    <span
                      className={`text-xs block text-center ${
                        theme === 'dark'
                          ? 'text-primary font-medium'
                          : 'text-on-surface-variant'
                      }`}
                    >
                      {theme === 'dark' ? 'Dark (Active)' : 'Dark'}
                    </span>
                  </div>

                  {/* System Card */}
                  <div
                    className="group cursor-pointer"
                    onClick={() => setTheme('system')}
                  >
                    <div
                      className={`h-24 bg-surface-container border-2 ${
                        theme === 'system'
                          ? 'border-primary shadow-[0_0_15px_rgba(163,166,255,0.1)]'
                          : 'border-transparent group-hover:border-outline-variant/20'
                      } rounded-lg mb-2 relative overflow-hidden transition-all`}
                    >
                      <div className="absolute inset-0 bg-gradient-to-br from-on-background/10 to-surface-container-highest/50"></div>
                      <div className="absolute bottom-2 right-2 w-4 h-4 bg-outline/20 rounded-full"></div>
                    </div>
                    <span
                      className={`text-xs block text-center ${
                        theme === 'system'
                          ? 'text-primary font-medium'
                          : 'text-on-surface-variant'
                      }`}
                    >
                      {theme === 'system' ? 'System (Active)' : 'System'}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-8">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-on-surface">
                      Editor Font
                    </label>
                    <select
                      value={editorFont}
                      onChange={(e) => setEditorFont(e.target.value)}
                      className="w-full bg-surface-container-high border-none rounded-lg text-sm px-4 py-3 focus:ring-1 focus:ring-primary/30 font-mono text-on-surface"
                    >
                      <option>JetBrains Mono</option>
                      <option>Fira Code</option>
                      <option>Cascadia Code</option>
                    </select>
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-on-surface">
                      UI Font Size
                    </label>
                    <div className="flex items-center bg-surface-container-high rounded-lg p-1">
                      <button
                        onClick={() => setFontSize(fontSizeMap['small'])}
                        className={`flex-1 py-2 text-xs rounded transition-colors ${
                          uiFontSize === 'small'
                            ? 'bg-surface-bright shadow-sm text-on-surface'
                            : 'hover:bg-surface-container text-on-surface-variant'
                        }`}
                      >
                        Small
                      </button>
                      <button
                        onClick={() => setFontSize(fontSizeMap['medium'])}
                        className={`flex-1 py-2 text-xs rounded transition-colors ${
                          uiFontSize === 'medium'
                            ? 'bg-surface-bright shadow-sm text-on-surface'
                            : 'hover:bg-surface-container text-on-surface-variant'
                        }`}
                      >
                        Medium
                      </button>
                      <button
                        onClick={() => setFontSize(fontSizeMap['large'])}
                        className={`flex-1 py-2 text-xs rounded transition-colors ${
                          uiFontSize === 'large'
                            ? 'bg-surface-bright shadow-sm text-on-surface'
                            : 'hover:bg-surface-container text-on-surface-variant'
                        }`}
                      >
                        Large
                      </button>
                    </div>
                  </div>
                </div>
              </section>

              {/* Footer actions */}
              <div className="pt-8 flex justify-end gap-4 border-t border-outline-variant/10">
                <button 
                  onClick={() => window.location.reload()}
                  className="px-6 py-2.5 text-sm font-medium text-on-surface-variant hover:text-on-surface transition-colors"
                  disabled={isSaving}
                >
                  Discard Changes
                </button>
                <button 
                  onClick={handleSaveSettings}
                  disabled={isSaving}
                  className="px-8 py-2.5 text-sm font-bold bg-primary text-on-primary rounded shadow-lg shadow-primary/20 active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {isSaving ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-2 border-on-primary border-t-transparent"></div>
                      Saving...
                    </>
                  ) : (
                    'Save Changes'
                  )}
                </button>
              </div>

              {/* Extra spacing */}
              <div className="h-24"></div>
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
