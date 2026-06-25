const { app, BrowserWindow } = require('electron');
const path = require('path');

function createWindow () {
  // Create the native browser window.
  const mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    autoHideMenuBar: true, // Hides the default File/Edit/View menu
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  // -----------------------------------------------------------
  // DEVELOPMENT MODE: Point directly to your running Vite server
  // -----------------------------------------------------------
  mainWindow.loadURL('http://localhost:5173');

  // -----------------------------------------------------------
  // PRODUCTION MODE: Uncomment this later when you build the .exe
  // -----------------------------------------------------------
  // mainWindow.loadFile(path.join(__dirname, '../FrontEnd/dist/index.html'));
}

// Boot up the window when Electron is ready
app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

// Quit when all windows are closed (except on macOS)
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});