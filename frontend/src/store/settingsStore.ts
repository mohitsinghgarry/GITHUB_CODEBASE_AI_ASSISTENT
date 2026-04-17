/**
 * Settings Store
 * 
 * Manages application settings and preferences including:
 * - Theme (light/dark mode)
 * - UI preferences
 * - User preferences
 * - Feature flags
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

type Theme = 'light' | 'dark' | 'system';
type CodeTheme = 'github-dark' | 'github-light' | 'monokai' | 'dracula' | 'nord';
type FontSize = 'xs' | 'sm' | 'base' | 'lg' | 'xl';

interface SettingsState {
  // Theme settings
  theme: Theme;
  codeTheme: CodeTheme;
  
  // Backend settings (synced with API)
  llmModel: string;
  temperature: number;
  maxContextTokens: number;
  maxResponseTokens: number;
  embeddingModel: string;
  chunkSize: number;
  chunkOverlap: number;
  defaultTopK: number;
  hybridSearchAlpha: number;
  
  // UI preferences
  sidebarCollapsed: boolean;
  fontSize: FontSize;
  lineNumbers: boolean;
  wordWrap: boolean;
  compactMode: boolean;
  
  // Chat preferences
  streamingEnabled: boolean;
  showCitations: boolean;
  autoScrollChat: boolean;
  
  // Search preferences
  defaultSearchMode: 'semantic' | 'keyword' | 'hybrid';
  defaultTopK: number;
  highlightMatches: boolean;
  
  // Code review preferences
  showLineNumbers: boolean;
  showSeverityIcons: boolean;
  autoExpandIssues: boolean;
  
  // Notification preferences
  showNotifications: boolean;
  notificationSound: boolean;
  
  // Feature flags
  experimentalFeatures: boolean;
  betaFeatures: boolean;
  
  // Actions
  setTheme: (theme: Theme) => void;
  setCodeTheme: (codeTheme: CodeTheme) => void;
  toggleTheme: () => void;
  
  // Backend settings actions
  setLlmModel: (model: string) => void;
  setTemperature: (temperature: number) => void;
  setMaxContextTokens: (tokens: number) => void;
  setMaxResponseTokens: (tokens: number) => void;
  setEmbeddingModel: (model: string) => void;
  setChunkSize: (size: number) => void;
  setChunkOverlap: (overlap: number) => void;
  setDefaultTopK: (topK: number) => void;
  setHybridSearchAlpha: (alpha: number) => void;
  
  setSidebarCollapsed: (collapsed: boolean) => void;
  toggleSidebar: () => void;
  
  setFontSize: (fontSize: FontSize) => void;
  setLineNumbers: (enabled: boolean) => void;
  setWordWrap: (enabled: boolean) => void;
  setCompactMode: (enabled: boolean) => void;
  
  setStreamingEnabled: (enabled: boolean) => void;
  setShowCitations: (enabled: boolean) => void;
  setAutoScrollChat: (enabled: boolean) => void;
  
  setDefaultSearchMode: (mode: 'semantic' | 'keyword' | 'hybrid') => void;
  setDefaultTopK: (topK: number) => void;
  setHighlightMatches: (enabled: boolean) => void;
  
  setShowLineNumbers: (enabled: boolean) => void;
  setShowSeverityIcons: (enabled: boolean) => void;
  setAutoExpandIssues: (enabled: boolean) => void;
  
  setShowNotifications: (enabled: boolean) => void;
  setNotificationSound: (enabled: boolean) => void;
  
  setExperimentalFeatures: (enabled: boolean) => void;
  setBetaFeatures: (enabled: boolean) => void;
  
  reset: () => void;
  resetToDefaults: () => void;
}

const defaultSettings = {
  // Theme settings
  theme: 'system' as Theme,
  codeTheme: 'github-dark' as CodeTheme,
  
  // Backend settings (defaults)
  llmModel: 'openai/gpt-oss-120b',
  temperature: 0.7,
  maxContextTokens: 4096,
  maxResponseTokens: 2048,
  embeddingModel: 'sentence-transformers/all-MiniLM-L6-v2',
  chunkSize: 512,
  chunkOverlap: 50,
  defaultTopK: 10,
  hybridSearchAlpha: 0.5,
  
  // UI preferences
  sidebarCollapsed: false,
  fontSize: 'base' as FontSize,
  lineNumbers: true,
  wordWrap: true,
  compactMode: false,
  
  // Chat preferences
  streamingEnabled: true,
  showCitations: true,
  autoScrollChat: true,
  
  // Search preferences
  defaultSearchMode: 'hybrid' as const,
  defaultTopK: 10,
  highlightMatches: true,
  
  // Code review preferences
  showLineNumbers: true,
  showSeverityIcons: true,
  autoExpandIssues: false,
  
  // Notification preferences
  showNotifications: true,
  notificationSound: false,
  
  // Feature flags
  experimentalFeatures: false,
  betaFeatures: false,
};

export const useSettingsStore = create<SettingsState>()(
  devtools(
    persist(
      (set, get) => ({
        ...defaultSettings,

        // Theme actions
        setTheme: (theme) => set({ theme }, false, 'setTheme'),

        setCodeTheme: (codeTheme) => set({ codeTheme }, false, 'setCodeTheme'),

        toggleTheme: () =>
          set(
            (state) => {
              const themeMap: Record<Theme, Theme> = {
                light: 'dark',
                dark: 'system',
                system: 'light',
              };
              return { theme: themeMap[state.theme] };
            },
            false,
            'toggleTheme'
          ),

        // Backend settings actions
        setLlmModel: (llmModel) => set({ llmModel }, false, 'setLlmModel'),
        
        setTemperature: (temperature) => set({ temperature }, false, 'setTemperature'),
        
        setMaxContextTokens: (maxContextTokens) => 
          set({ maxContextTokens }, false, 'setMaxContextTokens'),
        
        setMaxResponseTokens: (maxResponseTokens) => 
          set({ maxResponseTokens }, false, 'setMaxResponseTokens'),
        
        setEmbeddingModel: (embeddingModel) => 
          set({ embeddingModel }, false, 'setEmbeddingModel'),
        
        setChunkSize: (chunkSize) => set({ chunkSize }, false, 'setChunkSize'),
        
        setChunkOverlap: (chunkOverlap) => 
          set({ chunkOverlap }, false, 'setChunkOverlap'),
        
        setDefaultTopK: (defaultTopK) => 
          set({ defaultTopK }, false, 'setDefaultTopK'),
        
        setHybridSearchAlpha: (hybridSearchAlpha) => 
          set({ hybridSearchAlpha }, false, 'setHybridSearchAlpha'),

        // Sidebar actions
        setSidebarCollapsed: (collapsed) =>
          set({ sidebarCollapsed: collapsed }, false, 'setSidebarCollapsed'),

        toggleSidebar: () =>
          set(
            (state) => ({ sidebarCollapsed: !state.sidebarCollapsed }),
            false,
            'toggleSidebar'
          ),

        // UI preference actions
        setFontSize: (fontSize) => set({ fontSize }, false, 'setFontSize'),

        setLineNumbers: (enabled) =>
          set({ lineNumbers: enabled }, false, 'setLineNumbers'),

        setWordWrap: (enabled) => set({ wordWrap: enabled }, false, 'setWordWrap'),

        setCompactMode: (enabled) =>
          set({ compactMode: enabled }, false, 'setCompactMode'),

        // Chat preference actions
        setStreamingEnabled: (enabled) =>
          set({ streamingEnabled: enabled }, false, 'setStreamingEnabled'),

        setShowCitations: (enabled) =>
          set({ showCitations: enabled }, false, 'setShowCitations'),

        setAutoScrollChat: (enabled) =>
          set({ autoScrollChat: enabled }, false, 'setAutoScrollChat'),

        // Search preference actions
        setDefaultSearchMode: (mode) =>
          set({ defaultSearchMode: mode }, false, 'setDefaultSearchMode'),

        setDefaultTopK: (topK) =>
          set({ defaultTopK: topK }, false, 'setDefaultTopK'),

        setHighlightMatches: (enabled) =>
          set({ highlightMatches: enabled }, false, 'setHighlightMatches'),

        // Code review preference actions
        setShowLineNumbers: (enabled) =>
          set({ showLineNumbers: enabled }, false, 'setShowLineNumbers'),

        setShowSeverityIcons: (enabled) =>
          set({ showSeverityIcons: enabled }, false, 'setShowSeverityIcons'),

        setAutoExpandIssues: (enabled) =>
          set({ autoExpandIssues: enabled }, false, 'setAutoExpandIssues'),

        // Notification preference actions
        setShowNotifications: (enabled) =>
          set({ showNotifications: enabled }, false, 'setShowNotifications'),

        setNotificationSound: (enabled) =>
          set({ notificationSound: enabled }, false, 'setNotificationSound'),

        // Feature flag actions
        setExperimentalFeatures: (enabled) =>
          set({ experimentalFeatures: enabled }, false, 'setExperimentalFeatures'),

        setBetaFeatures: (enabled) =>
          set({ betaFeatures: enabled }, false, 'setBetaFeatures'),

        // Utility actions
        reset: () => set(defaultSettings, false, 'reset'),

        resetToDefaults: () => set(defaultSettings, false, 'resetToDefaults'),
      }),
      {
        name: 'settings-store',
        // Persist all settings
      }
    ),
    { name: 'SettingsStore' }
  )
);
