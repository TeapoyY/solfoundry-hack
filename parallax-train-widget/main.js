const { app, BrowserWindow, ipcMain, dialog, Notification, Tray, Menu, nativeImage } = require('electron');
const path = require('path');
const fs = require('fs');

let mainWindow = null;
let tray = null;

// Parse command line args for widget mode
const args = process.argv.slice(1);
const isDev = args.includes('--dev') || !app.isPackaged;
const initialMode = args.includes('--desktop') ? 'desktop' : args.includes('--transparent') ? 'transparent' : 'normal';

function createWindow() {
  const windowConfig = {
    width: 900,
    height: 600,
    minWidth: 400,
    minHeight: 300,
    frame: false,
    transparent: false,
    resizable: true,
    alwaysOnTop: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      webSecurity: true,
    },
    backgroundColor: '#1a1a2e',
  };

  // Apply transparent mode settings
  if (initialMode === 'transparent' || initialMode === 'desktop') {
    windowConfig.transparent = true;
    windowConfig.backgroundColor = '#00000000';
    windowConfig.frame = false;
    windowConfig.alwaysOnTop = true;
  }

  mainWindow = new BrowserWindow(windowConfig);

  // Apply click-through for desktop mode
  if (initialMode === 'desktop') {
    mainWindow.setIgnoreMouseEvents(true, { forward: true });
  }

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools({ mode: 'detach' });
  } else {
    mainWindow.loadFile(path.join(__dirname, 'dist-renderer', 'index.html'));
  }

  // Send initial mode to renderer
  mainWindow.webContents.on('did-finish-load', () => {
    mainWindow.webContents.send('widget-mode-changed', initialMode);
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function createTray() {
  const iconSize = 16;
  const icon = nativeImage.createEmpty();
  
  // Create a simple train icon programmatically
  const canvas = Buffer.alloc(iconSize * iconSize * 4);
  for (let y = 0; y < iconSize; y++) {
    for (let x = 0; x < iconSize; x++) {
      const idx = (y * iconSize + x) * 4;
      // Simple train shape
      const isTrain = (
        (y >= 4 && y <= 10 && x >= 2 && x <= 13) || // body
        (y >= 6 && y <= 8 && x >= 3 && x <= 5) || // window
        (y >= 6 && y <= 8 && x >= 7 && x <= 9) || // window
        (y >= 6 && y <= 8 && x >= 11 && x <= 13) || // window
        (y >= 11 && y <= 12 && (x === 4 || x === 9)) // wheels
      );
      if (isTrain) {
        canvas[idx] = 79;     // R
        canvas[idx + 1] = 195; // G
        canvas[idx + 2] = 247; // B
        canvas[idx + 3] = 255; // A
      } else {
        canvas[idx + 3] = 0; // Transparent
      }
    }
  }
  
  const trainIcon = nativeImage.createFromBuffer(canvas, { width: iconSize, height: iconSize });
  
  tray = new Tray(trainIcon);
  tray.setToolTip('Parallax Train Widget');
  
  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Show Window',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.focus();
        }
      }
    },
    {
      label: 'Start Pomodoro',
      click: () => {
        if (mainWindow) {
          mainWindow.webContents.send('tray-start-pomodoro');
        }
      }
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => {
        app.quit();
      }
    },
  ]);
  
  tray.setContextMenu(contextMenu);
  
  tray.on('double-click', () => {
    if (mainWindow) {
      mainWindow.show();
      mainWindow.focus();
    }
  });
}

app.whenReady().then(() => {
  createWindow();
  createTray();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// IPC Handlers
ipcMain.handle('window-minimize', () => {
  if (mainWindow) mainWindow.minimize();
});

ipcMain.handle('window-maximize', () => {
  if (mainWindow) {
    if (mainWindow.isMaximized()) {
      mainWindow.unmaximize();
    } else {
      mainWindow.maximize();
    }
  }
});

ipcMain.handle('window-close', () => {
  if (mainWindow) mainWindow.close();
});

ipcMain.handle('window-is-maximized', () => {
  return mainWindow ? mainWindow.isMaximized() : false;
});

ipcMain.handle('set-always-on-top', (event, value) => {
  if (mainWindow) {
    mainWindow.setAlwaysOnTop(value);
  }
});

// Set widget mode: 'normal' | 'transparent' | 'desktop'
ipcMain.handle('set-widget-mode', (event, mode) => {
  if (!mainWindow) return;
  
  if (mode === 'transparent') {
    mainWindow.setTransparent(true);
    mainWindow.setAlwaysOnTop(true);
    mainWindow.setIgnoreMouseEvents(false);
    mainWindow.setBackgroundColor('#00000000');
  } else if (mode === 'desktop') {
    mainWindow.setTransparent(true);
    mainWindow.setAlwaysOnTop(true);
    mainWindow.setIgnoreMouseEvents(true, { forward: true });
    mainWindow.setBackgroundColor('#00000000');
  } else {
    // normal mode
    mainWindow.setTransparent(false);
    mainWindow.setAlwaysOnTop(false);
    mainWindow.setIgnoreMouseEvents(false);
    mainWindow.setBackgroundColor('#1a1a2e');
  }
  
  mainWindow.webContents.send('widget-mode-changed', mode);
});

// Enable/disable click-through
ipcMain.handle('set-click-through', (event, enabled) => {
  if (mainWindow) {
    mainWindow.setIgnoreMouseEvents(enabled, { forward: true });
  }
});

// Get current widget mode
ipcMain.handle('get-widget-mode', () => {
  if (!mainWindow) return 'normal';
  return mainWindow.isTransparent() ? 'desktop' : 'normal';
});

ipcMain.handle('open-file-dialog', async (event, options) => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [
      { name: 'Images', extensions: ['png', 'jpg', 'jpeg', 'gif', 'webp'] }
    ],
    ...options
  });
  return result;
});

ipcMain.handle('show-notification', (event, title, body) => {
  if (Notification.isSupported()) {
    new Notification({ title, body }).show();
  }
});

ipcMain.handle('minimize-to-tray', () => {
  if (mainWindow) {
    mainWindow.hide();
  }
});

ipcMain.handle('read-file', async (event, filePath) => {
  try {
    const data = fs.readFileSync(filePath);
    return data.toString('base64');
  } catch (e) {
    return null;
  }
});

ipcMain.handle('write-file', async (event, filePath, data) => {
  try {
    fs.writeFileSync(filePath, data, 'utf-8');
    return true;
  } catch (e) {
    return false;
  }
});

ipcMain.handle('save-config', async (event, config) => {
  try {
    const configDir = path.join(app.getPath('userData'), 'config');
    if (!fs.existsSync(configDir)) fs.mkdirSync(configDir, { recursive: true });
    const filePath = path.join(configDir, 'widget-config.json');
    fs.writeFileSync(filePath, JSON.stringify(config, null, 2), 'utf-8');
    return true;
  } catch (e) {
    console.error('save-config failed:', e);
    return false;
  }
});

ipcMain.handle('load-config', async () => {
  try {
    const filePath = path.join(app.getPath('userData'), 'config', 'widget-config.json');
    if (!fs.existsSync(filePath)) return null;
    return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  } catch (e) {
    console.error('load-config failed:', e);
    return null;
  }
});

ipcMain.handle('read-file-as-dataurl', async (event, filePath) => {
  try {
    const data = fs.readFileSync(filePath);
    const ext = (filePath.split('.').pop() || 'png').toLowerCase();
    const mimeMap = {
      png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg',
      gif: 'image/gif', webp: 'image/webp', svg: 'image/svg+xml',
    };
    const mime = mimeMap[ext] || 'image/png';
    return `data:${mime};base64,${data.toString('base64')}`;
  } catch (e) {
    console.error('read-file-as-dataurl failed:', e);
    return null;
  }
});
