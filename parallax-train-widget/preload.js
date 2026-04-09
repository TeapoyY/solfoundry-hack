const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  minimize: () => ipcRenderer.invoke('window-minimize'),
  maximize: () => ipcRenderer.invoke('window-maximize'),
  close: () => ipcRenderer.invoke('window-close'),
  isMaximized: () => ipcRenderer.invoke('window-is-maximized'),
  setAlwaysOnTop: (value) => ipcRenderer.invoke('set-always-on-top', value),
  openFileDialog: (options) => ipcRenderer.invoke('open-file-dialog', options),
  showNotification: (title, body) => ipcRenderer.invoke('show-notification', title, body),
  minimizeToTray: () => ipcRenderer.invoke('minimize-to-tray'),
  readFile: (filePath) => ipcRenderer.invoke('read-file', filePath),
  writeFile: (filePath, data) => ipcRenderer.invoke('write-file', filePath, data),
  onTrayStartPomodoro: (callback) => {
    ipcRenderer.on('tray-start-pomodoro', callback);
    return () => ipcRenderer.removeListener('tray-start-pomodoro', callback);
  },
  onMaximizeChange: (callback) => {
    const handler = (event, isMaximized) => callback(isMaximized);
    ipcRenderer.on('window-maximized-change', handler);
    return () => ipcRenderer.removeListener('window-maximized-change', handler);
  },
  onWidgetModeChange: (callback) => {
    ipcRenderer.on('widget-mode-changed', (event, mode) => callback(mode));
    return () => ipcRenderer.removeListener('widget-mode-changed', callback);
  },
  // Widget mode controls
  setWidgetMode: (mode) => ipcRenderer.invoke('set-widget-mode', mode),
  setClickThrough: (enabled) => ipcRenderer.invoke('set-click-through', enabled),
  getWidgetMode: () => ipcRenderer.invoke('get-widget-mode'),
  // Config persistence (file-based via Electron IPC)
  saveConfig: (config) => ipcRenderer.invoke('save-config', config),
  loadConfig: () => ipcRenderer.invoke('load-config'),
  // Alias for readFile that returns data URL
  readFileAsDataUrl: (filePath) => ipcRenderer.invoke('read-file-as-dataurl', filePath),
});
