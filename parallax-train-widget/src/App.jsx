import React, { useState, useEffect, useCallback } from 'react';
import WidgetFrame from './components/WidgetFrame';
import ParallaxCanvas from './components/ParallaxCanvas';
import LayerEditor from './components/LayerEditor';
import TodoList from './components/TodoList';
import PomodoroTimer from './components/PomodoroTimer';
import defaultConfig from './config/config.json';

const STORAGE_KEY = 'parallax-train-config';
const MODE_KEY = 'parallax-train-widget-mode';

const App = () => {
  const [showEditor, setShowEditor] = useState(false);
  const [config, setConfig] = useState(() => {
    // Try to load saved config from localStorage
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        return JSON.parse(saved);
      }
    } catch (e) {
      console.warn('Failed to load saved config:', e);
    }
    return defaultConfig;
  });
  const [alwaysOnTop, setAlwaysOnTop] = useState(false);
  const [showTodo, setShowTodo] = useState(false);
  const [showPomodoro, setShowPomodoro] = useState(true);
  const [widgetMode, setWidgetMode] = useState(() => {
    // Try to load saved mode
    try {
      return localStorage.getItem(MODE_KEY) || 'normal';
    } catch (e) {
      return 'normal';
    }
  });

  // Save config to localStorage whenever it changes
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
    } catch (e) {
      console.warn('Failed to save config:', e);
    }
  }, [config]);

  // Save widget mode to localStorage
  useEffect(() => {
    try {
      localStorage.setItem(MODE_KEY, widgetMode);
    } catch (e) {
      console.warn('Failed to save widget mode:', e);
    }
  }, [widgetMode]);

  const handleAlwaysOnTopChange = useCallback((value) => {
    setAlwaysOnTop(value);
    if (window.electron) {
      window.electron.setAlwaysOnTop(value);
    }
  }, []);

  const handleConfigChange = useCallback((newConfig) => {
    if (newConfig === null) {
      // Reset to defaults
      setConfig(defaultConfig);
    } else {
      setConfig(newConfig);
    }
  }, []);

  const handleMinimizeToTray = useCallback(() => {
    if (window.electron) {
      window.electron.minimizeToTray();
    }
  }, []);

  const handleWidgetModeChange = useCallback((mode) => {
    setWidgetMode(mode);
  }, []);

  useEffect(() => {
    if (window.electron) {
      window.electron.onTrayStartPomodoro(() => {
        setShowPomodoro(true);
      });
      // Get initial mode
      window.electron.getWidgetMode().then((mode) => {
        if (mode) setWidgetMode(mode);
      });
    }
  }, []);

  // Build app class names based on mode
  const appClassName = `app ${widgetMode === 'transparent' ? 'transparent-mode' : ''} ${widgetMode === 'desktop' ? 'desktop-mode' : ''}`;

  return (
    <div className={appClassName}>
      <WidgetFrame
        alwaysOnTop={alwaysOnTop}
        onAlwaysOnTopChange={handleAlwaysOnTopChange}
        onMinimizeToTray={handleMinimizeToTray}
        onToggleEditor={() => setShowEditor(!showEditor)}
        showEditor={showEditor}
        widgetMode={widgetMode}
        onWidgetModeChange={handleWidgetModeChange}
      />

      <div className="main-content">
        <div className="canvas-container">
          <ParallaxCanvas
            config={config}
            onConfigChange={handleConfigChange}
          />
        </div>

        <div className={`widget-panel ${showPomodoro ? 'visible' : ''}`}>
          <div className="panel-header">
            <span>Pomodoro</span>
            <button className="panel-close" onClick={() => setShowPomodoro(false)}>×</button>
          </div>
          <PomodoroTimer />
        </div>

        <div className={`widget-panel todo-panel ${showTodo ? 'visible' : ''}`}>
          <div className="panel-header">
            <span>Tasks</span>
            <button className="panel-close" onClick={() => setShowTodo(false)}>×</button>
          </div>
          <TodoList />
        </div>
      </div>

      <div className="panel-toggles">
        <button
          className={`panel-toggle ${showPomodoro ? 'active' : ''}`}
          onClick={() => setShowPomodoro(!showPomodoro)}
          title="Pomodoro Timer"
        >
          🍅
        </button>
        <button
          className={`panel-toggle ${showTodo ? 'active' : ''}`}
          onClick={() => setShowTodo(!showTodo)}
          title="Todo List"
        >
          📋
        </button>
      </div>

      {showEditor && (
        <LayerEditor
          config={config}
          onConfigChange={handleConfigChange}
          onClose={() => setShowEditor(false)}
        />
      )}
    </div>
  );
};

export default App;
