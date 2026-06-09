const { app, BrowserWindow } = require('electron');
const path = require('path');

async function run() {
  const mainWindow = new BrowserWindow({ width: 1280, height: 800, webPreferences: { nodeIntegration: false } });
  await mainWindow.loadURL('http://localhost:5173');
  await mainWindow.webContents.waitForDidStopLoading();

  await new Promise(r => setTimeout(r, 2000));

  const results = await mainWindow.webContents.evaluate(() => {
    const activePage = document.querySelector('.page.active');
    const exportBtn = document.querySelector('.big');
    return {
      hasApp: !!document.querySelector('.app'),
      hasActivePage: !!activePage,
      descText: activePage ? activePage.querySelector('.desc')?.textContent?.trim().slice(0, 80) : '',
      hasExportBtn: !!exportBtn,
      hasMetaRow: !!document.querySelector('.meta-row'),
      hasScaleSelect: !!document.querySelector('select'),
      tabCount: document.querySelectorAll('.tab').length,
      tabs: Array.from(document.querySelectorAll('.tab')).map(t => t.textContent.trim())
    };
  });

  console.log('--- Tab1 Verification ---');
  console.log('App mounted:', results.hasApp);
  console.log('Active page found:', results.hasActivePage);
  console.log('Description:', results.descText);
  console.log('Export button:', results.hasExportBtn);
  console.log('Meta row (files info):', results.hasMetaRow);
  console.log('Scale select:', results.hasScaleSelect);
  console.log('Tab count:', results.tabCount);
  console.log('Tabs:', results.tabs.join(' | '));

  const img = await mainWindow.webContents.capturePage();
  require('fs').writeFileSync(path.join(__dirname, 'shots/verify_tab1.png'), img.toPNG());
  console.log('Screenshot: shots/verify_tab1.png');

  app.quit();
}

app.whenReady().then(run).catch(e => { console.error(e.message); app.quit(); });