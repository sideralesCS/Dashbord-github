# Dashbord - Siderales Creative Studio

Dashboard de gestion de ingresos para Siderales Creative Studio, 2Matute Studio y Freelance.

## Uso

### 1. Sincronizar datos desde Notion

```bash
python sync_notion.py
```

O simplemente hacé doble click en `sync.bat` (Windows).

Esto descarga los datos de Notion, normaliza servicios, clientes y fuentes, y genera `data.json`.

### 2. Abrir el dashboard

```bash
# Opcion A: doble click en dashboard.html

# Opcion B: desde terminal
start dashboard.html   # Windows
open dashboard.html    # Mac
xdg-open dashboard.html  # Linux
```

### 3. Subir cambios a GitHub (acceso celular)

```bash
git add .
git commit -m "Update data"
git push origin main
```

Despues de eso, tu dashboard esta disponible en:
`https://sideralesCS.github.io/Dashbord-github/`

**Nota:** Si ves una pantalla vacia, espera 2-3 minutos y recargá. GitHub Pages tarda en activator.

---

## Estructura

```
sync_notion.py     → Script que sincroniza desde Notion → data.json
build_dashboard.py  → Genera dashboard.html (opcional, ya esta incluido)
dashboard.html      → Dashboard completo (abre en navegador)
data.json           → Datos sincronizados (generado por sync_notion.py)
sync.bat            → Atajo para ejecutar sync_notion.py
db_list.json        → Lista de databases de Notion (no editar)
README.md           → Este archivo
```

---

## Secciones del Dashboard

| Pestana | Que muestra |
|---------|-------------|
| **Resumen** | Total, Neto, IVA, ingresos por fuente, evolucion mensual |
| **IVA** | IVA recolectado vs declarado vs pendiente de declarar al SII |
| **Servicios** | Agrupacion por tipo de servicio (Video, Foto, Drone, Boda, etc.) |
| **Clientes** | Los 54 clientes con telefono, fuente, frecuencia y servicios |
| **Evolucion** | Grafico 2025 vs 2026, Top 10 clientes, insights |

---

## Fuentes de ingreso

- **2Matute Studio** → Personas (sesiones, bodas, eventos)
- **Agencias** → Propalta, Crinimo, Makrim, SERCAR, Punto Zero
- **Siderales Creative** → Proyectos corporativos, freelance

---

## Tecnologias

- Python 3 para sync
- HTML + CSS + JS (Chart.js) para el dashboard
- GitHub Pages para acceso desde celular
- Notion API para datos

---

## Configuracion

El token de Notion esta guardado en `sync_notion.py`. Si necesitas actualizarlo, edit la linea:

```python
NOTION_TOKEN = 'ntn_TU_TOKEN_AQUI'
```

---

## Problemas comunes

**"No se pudo cargar data.json"**
→ Ejecuta primero `python sync_notion.py`

**Git push pide usuario/contrasena**
→ Usa un Personal Access Token en lugar de contrasena. GitHub ya no acepta contrasenas para git push.

**No aparecen datos de un mes**
→ Revisa que el archivo JSON de ese mes exista en la carpeta y no este corrupto.