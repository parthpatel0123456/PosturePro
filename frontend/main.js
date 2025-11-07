const { app, BrowserWindow, nativeTheme, globalShortcut } = require("electron");

const liquidGlass = require("electron-liquid-glass");

function createWindow() {
  const win = new BrowserWindow({
    width: 500,
    height: 350,
    resizable: false,
    frame: false,
    transparent: true,
    backgroundColor: "rgba(0, 0, 0, 0.1)",
    vibrancy: {
      theme: nativeTheme.shouldUseDarkColors ? "dark" : "light",
      material: "hud",
      effect: "under-window", // or "behind-window"
    },
    visualEffectState: "active",
    // vibrancy: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
    alwaysOnTop: true,
    hasShadow: true,
  });

  win.loadFile("index.html");

  win.once("ready-to-show", () => {
    win.show();
  });

  globalShortcut.register("CommandOrControl+Alt+R", () => {
    app.quit();
  });

  globalShortcut.register("CommandOrControl+\\", () => {
    win.setPosition(1750, 1250);
  });

  globalShortcut.register("CommandOrControl+Down", () => {
    win.setPosition(500, 375);
  });
}

app.whenReady().then(() => {
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
