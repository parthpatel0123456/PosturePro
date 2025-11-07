const { app, BrowserWindow, nativeTheme, globalShortcut } = require("electron");

const liquidGlass = require("electron-liquid-glass");

function createWindow() {
  const win = new BrowserWindow({
    width: 640,
    height: 340,
    resizable: false,
    frame: false,
    transparent: true,
    // backgroundColor: "#00000000",
    // vibrancy: {
    //   theme: nativeTheme.shouldUseDarkColors ? "dark" : "light",
    //   effect: "under-window", // or "behind-window"
    //   useCustomWindowRefreshMethod: true,
    // },
    // visualEffectState: "active",
    vibrancy: false,
    // webPreferences: {
    //   nodeIntegration: true,
    //   contextIsolation: false,
    // },
    alwaysOnTop: true,
  });

  win.loadFile("index.html");

  win.once("ready-to-show", () => {
    win.show();
  });

  win.webContents.once("did-finish-load", () => {
    const glassId = liquidGlass.addView(win.getNativeWindowHandle(), {
      tintColor: "rgba(0, 0, 0, 0.28)",
      blurRadius: 20,
    });
  });

  globalShortcut.register("CommandOrControl+Alt+R", () => {
    app.quit();
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
