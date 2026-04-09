import React, { useState, useEffect } from 'react';

const WidgetFrame = ({ alwaysOnTop, onAlwaysOnTopChange, onMinimizeToTray, onToggleEditor, showEditor, widgetMode, onWidgetModeChange }) => {
  const [isMaximized, setIsMaximized] = useState(false);

  useEffect(() => {
    if (window.electron) {
      window.electron.isMaximized().then(setIsMaximized);
      // Listen for mode changes from main process
      window.electron.onWidgetModeChange((mode) => {
        if (onWidgetModeChange) onWidgetModeChange(mode);
      });
    }
  }, []);

  const handleMinimize = () => {
    if (window.electron) {
      window.electron.minimize();
    }
  };

  const handleMaximize = async () => {
    if (window.electron) {
      await window.electron.maximize();
      const maximized = await window.electron.isMaximized();
      setIsMaximized(maximized);
    }
  };

  const handleClose = () => {
    if (window.electron) {
      window.electron.close();
    }
  };

  const handleMinimizeTray = () => {
    if (window.electron) {
      window.electron.minimizeToTray();
    }
  };

  const handleModeChange = (mode) => {
    if (window.electron) {
      window.electron.setWidgetMode(mode);
    }
    if (onWidgetModeChange) {
      onWidgetModeChange(mode);
    }
  };

  return (
    <div className="widget-frame">
      <div className="widget-title">
        <span>🚂</span>
        <span>Parallax Train</span>
      </div>
      
      <div className="widget-controls">
        {/* Widget Mode Toggle */}
        <div className="mode-toggle">
          <button
            className={`mode-btn ${widgetMode === 'normal' ? 'active' : ''}`}
            onClick={() => handleModeChange('normal')}
            title="Normal Mode"
          >
            📦
          </button>
          <button
            className={`mode-btn ${widgetMode === 'transparent' ? 'active' : ''}`}
            onClick={() => handleModeChange('transparent')}
            title="Transparent Mode"
          >
            🔲
          </button>
          <button
            className={`mode-btn ${widgetMode === 'desktop' ? 'active' : ''}`}
            onClick={() => handleModeChange('desktop')}
            title="Desktop Mode (Click-through)"
          >
            🖥️
          </button>
        </div>
        
        <button
          className={`widget-btn edit ${showEditor ? 'active' : ''}`}
          onClick={onToggleEditor}
          title="Layer Editor"
        >
          {showEditor ? '✓ Edit' : 'Edit'}
        </button>
        
        <button
          className={`widget-btn pin ${alwaysOnTop ? 'active' : ''}`}
          onClick={() => onAlwaysOnTopChange(!alwaysOnTop)}
          title="Always on Top"
        >
          📌
        </button>
        
        <button
          className="widget-btn"
          onClick={handleMinimizeTray}
          title="Minimize to Tray"
        >
          ⬇
        </button>
        
        <button
          className="widget-btn"
          onClick={handleMinimize}
          title="Minimize"
        >
          ─
        </button>
        
        <button
          className="widget-btn"
          onClick={handleMaximize}
          title={isMaximized ? 'Restore' : 'Maximize'}
        >
          {isMaximized ? '❐' : '□'}
        </button>
        
        <button
          className="widget-btn close"
          onClick={handleClose}
          title="Close"
        >
          ✕
        </button>
      </div>
    </div>
  );
};

export default WidgetFrame;
