# Dashboard React — Plan Optimizado

## Meta: Listo en ~2 horas

El dashboard actual funciona. El problema: 2200 líneas en un archivo. La solución: **dividir en partes lógicas, no reescribir**.

---

## TIEMPO REAL

| Tarea | Tiempo |
|-------|--------|
| Setup Vite | 5 min |
| Copiar CSS | 10 min |
| Copiar datos | 15 min |
| App.jsx (todo junto) | 60 min |
| Deploy | 10 min |
| **Total** | **~100 min** |

---

## ESTRUCTURA MÍNIMA

```
src/
├── App.jsx       # Todo el código (copiar del HTML)
├── data.js       # DEFAULT_CLIENTS + monthlyEntries
├── index.css     # CSS copiado
└── main.jsx
```

**Sí, un solo App.jsx.** No hay necesidad de separar en 10 componentes para algo que ya funciona.

---

## PASO 1: Setup

```bash
npm create vite@latest dashboard -- --template react
cd dashboard
npm install chart.js react-chartjs-2
rm src/App.css src/index.css
```

---

## PASO 2: Copiar datos (15 min)

Crear `src/data.js` con:
- DEFAULT_CLIENTS (53 clientes)
- monthlyEntries (2025-2026)

---

## PASO 3: Copiar CSS (10 min)

Copiar el `<style>` del `dashboard.html` a `src/index.css`.

---

## PASO 4: Copiar App.jsx (60 min)

1. Importar datos y Chart.js
2. Copiar todas las funciones del JS del HTML
3. Copiar el HTML del `<body>` como JSX
4. Conectar con Chart.js

**Regla: Copiar tal cual primero. Optimizar después.**

---

## PASO 5: Deploy (10 min)

```bash
npm install -D gh-pages

# package.json:
"homepage": "https://sideralescs.github.io/dashboard"
"scripts": { "deploy": "npm run build && gh-pages -d dist" }

npm run deploy
```

---

## CHECKLIST FINAL

```
□ npm create vite
□ npm install chart.js react-chartjs-2
□ Copiar CSS
□ Crear data.js
□ Copiar todo a App.jsx
□ npm run build
□ npm run deploy
□ Probar
```

---

## ALTERNATIVA: No migrar a React

Solo dividir el HTML en módulos:

```
dashboard/
├── index.html     # Estructura
├── data.js         # Datos
├── state.js        # localStorage logic
├── charts.js       # Chart configs
└── app.js          # Lógica
```

~1 hora, mismo resultado en producción.

---

¿Quieres que partamos ahora o hay algo que ajustar en el plan?