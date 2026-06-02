// Siderales Creative Studio - Google Sheets Sync API
// Instructions:
/*
1. Go to: https://sheets.google.com
2. Create a new spreadsheet named "Siderales Clientes"
3. In the spreadsheet, go to Extensions > Apps Script
4. Delete any existing code and paste this entire script
5. Save (Ctrl+S) and name it "SideralesSync"
6. Click Deploy > New deployment
7. Select "Web app" type
8. Set "Who has access" to "Anyone" (so the dashboard can read)
9. Click Deploy and copy the Web App URL
10. Paste that URL in the dashboard settings

The web app URL format will be:
https://script.google.com/macros/s/XXXXX/exec
*/

// Configuration
const SPREADSHEET_NAME = 'Siderales Clientes';
const SHEET_NAME = 'Clientes';

// Get or create the spreadsheet
function getSpreadsheet() {
  const files = DriveApp.getFilesByName(SPREADSHEET_NAME);
  if (files.hasNext()) {
    const ss = SpreadsheetApp.open(files.next());
    let sheet = ss.getSheetByName(SHEET_NAME);
    if (!sheet) {
      sheet = ss.insertSheet(SHEET_NAME);
      setupHeaders(sheet);
    }
    return sheet;
  } else {
    const ss = SpreadsheetApp.create(SPREADSHEET_NAME);
    const sheet = ss.getSheetByName(SHEET_NAME);
    setupHeaders(sheet);
    return sheet;
  }
}

function setupHeaders(sheet) {
  const headers = ['Nombre', 'Telefono', 'Categoria', 'Total', 'Servicios', 'Frecuencia', 'Anos'];
  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  sheet.getRange(1, 1, 1, headers.length).setFontWeight('bold');
  sheet.setHeaderRowEnabled(true);
}

// GET - Return all clients as JSON
function doGet(e) {
  const sheet = getSpreadsheet();
  const lastRow = sheet.getLastRow();
  
  if (lastRow < 2) {
    return ContentService
      .createTextOutput(JSON.stringify({clients: [], success: true}))
      .setMimeType(ContentService.MimeType.JSON);
  }
  
  const data = sheet.getRange(2, 1, lastRow - 1, 7).getValues();
  const clients = data.map(row => ({
    name: row[0] || '',
    phone: row[1] || '',
    source: row[2] || 'Siderales',
    total: parseInt(row[3]) || 0,
    services: (row[4] || '').split(';').map(s => s.trim()).filter(s => s),
    count: parseInt(row[5]) || 1,
    years: (row[6] || '2026').split(';').map(s => s.trim()).filter(s => s)
  })).filter(c => c.name);
  
  const output = JSON.stringify({clients: clients, success: true});
  return ContentService
    .createTextOutput(output)
    .setMimeType(ContentService.MimeType.JSON);
}

// POST - Save/update clients
function doPost(e) {
  try {
    const sheet = getSpreadsheet();
    const payload = JSON.parse(e.postData.contents);
    const clients = payload.clients || [];
    
    // Clear existing data (keep headers)
    const lastRow = sheet.getLastRow();
    if (lastRow > 1) {
      sheet.deleteRows(2, lastRow - 1);
    }
    
    // Write new data
    const rows = clients.map(c => [
      c.name || '',
      c.phone || '',
      c.source || 'Siderales',
      c.total || 0,
      (c.services || []).join('; '),
      c.count || 1,
      (c.years || ['2026']).join('; ')
    ]);
    
    if (rows.length > 0) {
      sheet.getRange(2, 1, rows.length, 7).setValues(rows);
    }
    
    return ContentService
      .createTextOutput(JSON.stringify({success: true, count: clients.length}))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch(err) {
    return ContentService
      .createTextOutput(JSON.stringify({success: false, error: err.message}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// POST - Add single client
function addClient(data) {
  const sheet = getSpreadsheet();
  const name = data.name || '';
  const phone = data.phone || '';
  const source = data.source || 'Siderales';
  const total = data.total || 0;
  const services = (data.services || ['Otro']).join('; ');
  const count = data.count || 1;
  const years = (data.years || ['2026']).join('; ');
  
  // Check if client exists
  const existing = findClientRow(name);
  if (existing) {
    sheet.getRange(existing, 1, 1, 7).setValues([[name, phone, source, total, services, count, years]]);
  } else {
    sheet.appendRow([name, phone, source, total, services, count, years]);
  }
  
  return {success: true};
}

// Find client by name
function findClientRow(name) {
  const sheet = getSpreadsheet();
  const data = sheet.getRange(2, 1, sheet.getLastRow() - 1, 1).getValues();
  
  for (let i = 0; i < data.length; i++) {
    if (data[i][0].toLowerCase() === name.toLowerCase()) {
      return i + 2; // +2 because row 1 is header, and array is 0-indexed
    }
  }
  return null;
}

// DELETE - Remove client
function deleteClient(name) {
  const sheet = getSpreadsheet();
  const row = findClientRow(name);
  
  if (row) {
    sheet.deleteRow(row);
    return {success: true};
  }
  return {success: false, error: 'Client not found'};
}