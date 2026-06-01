"""
sync_notion.py — Siderales Creative Studio
Sincroniza datos desde archivos JSON locales (respaldos de Notion)
Uso: python sync_notion.py
"""

import json
import os
import urllib.request
import urllib.error
from datetime import datetime
from collections import defaultdict

# ─── CONFIG ────────────────────────────────────────────────────────────
NOTION_TOKEN = 'ntn_Y49487249662wpn7EEY7LjutbiydbEMMgInSBnxwF65gnv'
HEADERS = {
    'Authorization': f'Bearer {NOTION_TOKEN}',
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28'
}

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── FUENTES ───────────────────────────────────────────────────────────
AGENCY_COMPANIES = {'Propalta', 'Crinimo', 'Makrim', 'SERCAR', 'Punto Zero', 'Miura',
                    'Daniel Verdessi', 'Gym Wellness', 'Faro Digital', 'TuYogaCoach', 'Nutricionista'}

SERVICE_GROUPS = {
    'VIDEO': ['video', 'film', 'filmacion', 'filmacion drone', 'drone filmacion', 'drone video', 'film'],
    'FOTO': ['foto', 'fotografia', 'fotos', 'sesion', 'reel', 'banner', 'foto video', 'fotos video'],
    'EDICION': ['edicion', 'render', 'post', 'montaje', 'correccion color'],
    'DRONE': ['drone', 'terreno aereo', 'terreno aere'],
    'BODA': ['boda', 'matrimonio', 'casamiento'],
    'REUNION': ['reu familiar', 'reunion familiar', 'cumple', 'aniversario', 'bautizo'],
    'CORPORATIVO': ['corporativo', 'samsung', 'web', 'campana', 'campaña', 'marca'],
    'AGENCIA': ['rincon peruano', 'meson peruano', 'ayc', 'ludiano', 'peruano'],
}

CONTACT_SOURCES = {
    'Nimrod': 'Agencia', 'Sofi B': 'Agencia', 'Ina Rojas': 'Agencia', 'Fran CRINIMO': 'Agencia',
    'Macca Makrim': 'Agencia', 'Maccarena': 'Agencia', 'Sergio Sercar': 'Agencia', 'Sergui': 'Agencia',
    'Luis Bravo': 'Siderales', 'Ernesto Biermoritz': 'Siderales', 'Javi Miss Biermoritz': 'Siderales',
    'Domi Nique Huisack': 'Siderales', 'Leonardo huisack': 'Siderales',
    'Majo turismo': 'Siderales', 'Cris turismo': 'Siderales',
}

CONTACT_TELEPHONES = {
    'Luis Bravo': '+56 9 8312 8163', 'Paty': '+56 9 3486 6365', 'Felipe': '+56 9 3070 9180',
    'Sergio Sercar': '+56 9 7865 8552', 'Fran CRINIMO': '+56 9 5436 9301', 'Manuel': '+56 9 8902 0811',
    'hilda': '+56 9 8205 0836', 'Javi Biermoritz': '+56 9 9012 7988',
    'Montserrat Urmeneta': '+56 9 9821 5348', 'Ignacio Sorrel': '+56 9 9315 4409',
    'Mili pole': '+56 9 4245 2359', 'Macca Makrim': '+56 9 3105 2886', 'Alvaro Veas': '+56 9 6317 7921',
    'Majo turismo': '+56 9 8307 4112', 'Nimrod': '+56 9 9874 8782', 'Sofi': '+56 9 9232 0199',
    'Nicole Ramos': '+56 9 9881 9732', 'Leonardo': '+56 9 5905 3572', 'Danilo Sandoval': '+56 9 8537 3171',
    'Cris turismo': '+56 9 6551 0998', 'Leo Camus': '+56 9 7453 4012', 'Javiera Fulla': '+56 9 7787 7010',
    'Constanza Cornejo': '+56 9 7297 2793', 'Marilore': '+56 9 9133 1815', 'Esteban Contador': '+56 9 5634 1881',
    'Joaco': '+56 9 5363 1935', 'Domi': '+56 9 5391 0108', 'Nacho Peralta': '+56 9 6510 3641',
    'Ernesto Biermoritz': '+56 9 5446 2988', 'Ina Rojas': '+56 9 4988 3323', 'Tere Laguna': '+56 9 8989 3336',
    'Fernanda Venegas': '+56 9 4401 3766', 'Karen': '+56 9 7996 3179',
    'Celis': '+56 9 3764 1560', 'Karina': '+56 9 5993 3000',
}

# ─── PARSING HELPERS ──────────────────────────────────────────────────
def get_text(props, key):
    texts = props.get(key, {}).get('rich_text', [])
    return ''.join([t.get('plain_text', '') for t in texts]).strip()

def get_multi(props, key):
    items = props.get(key, {}).get('multi_select', [])
    return ', '.join([t['name'] for t in items]) if items else ''

def get_select(props, key):
    val = props.get(key, {}).get('select', {})
    return val['name'] if val else ''

def get_number(props, key):
    return props.get(key, {}).get('number')

def get_formula(props, key):
    return props.get(key, {}).get('formula', {}).get('number')

def infer_source(cliente, empresa):
    if not cliente:
        return '2Matute'
    for name, src in CONTACT_SOURCES.items():
        if name.lower() in cliente.lower() or cliente.lower() in name.lower():
            return src
    if empresa in AGENCY_COMPANIES:
        return 'Agencia'
    return '2Matute'

def get_service_type(concepto):
    if not concepto:
        return 'Otro'
    upper = concepto.upper()
    for svc, keywords in SERVICE_GROUPS.items():
        for kw in keywords:
            if kw.upper() in upper:
                return svc
    return 'Otro'

# ─── PARSE 2026 JSON FILES ────────────────────────────────────────────
def parse_2026_json(filepath, month_name):
    entries = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            raw = f.read()
        data = json.loads(raw)
    except Exception:
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                raw = f.read()
            data = json.loads(raw)
        except Exception:
            return entries
    
    results = data.get('results', [])
    for page in results:
        props = page.get('properties', {})
        
        fecha_dia = get_text(props, 'Fecha')
        cliente = get_multi(props, 'Cliente') or get_text(props, 'Cliente') or ''
        empresa = get_select(props, 'Empresa')
        concepto = get_text(props, 'CONCEPTO')
        
        total = get_number(props, 'TOTAL (NETO+IVA)') or get_formula(props, 'TOTAL (NETO+IVA)')
        neto = get_formula(props, 'NETO')
        iva = get_formula(props, 'IVA (19%)')
        
        metodo_pago = get_select(props, 'Metodo de Pago')
        estado = get_select(props, 'Estado')
        iva_declarado = get_select(props, 'IVA Declarado')
        fecha_pago = get_text(props, 'FECHA PAGO')
        
        if not total or total <= 0:
            continue
        
        source = infer_source(cliente, empresa)
        service = get_service_type(concepto)
        
        phone = ''
        for name, tel in CONTACT_TELEPHONES.items():
            if name.lower() in cliente.lower():
                phone = tel
                break
        
        # Compute neto/iva if missing
        if neto is None:
            neto = round(total / 1.19, 2)
        if iva is None:
            iva = round(total - total / 1.19, 2)
        
        entries.append({
            'fecha_dia': fecha_dia,
            'cliente': cliente.strip(),
            'empresa': empresa,
            'concepto': concepto,
            'total': total,
            'neto': round(neto, 2),
            'iva': round(iva, 2),
            'source': source,
            'service': service,
            'metodo_pago': metodo_pago,
            'estado': estado,
            'iva_declarado': iva_declarado,
            'fecha_pago': fecha_pago,
            'month': month_name,
        })
    return entries

# ─── PARSE all_entries.json (2025 data) ──────────────────────────────
def parse_all_entries(filepath):
    entries = []
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
    except Exception:
        return entries
    
    for entry in data:
        mes = entry.get('Month', '')
        cliente = entry.get('Cliente', '') or ''
        empresa = entry.get('Empresa', '') or ''
        concepto = entry.get('Concepto', '') or ''
        total = entry.get('Total', 0) or 0
        neto = entry.get('Neto', 0) or 0
        iva = round(total - neto, 2) if total and neto else round(total / 1.19 * 0.19, 2)
        
        if total <= 0:
            continue
        
        source = infer_source(cliente, empresa)
        service = get_service_type(concepto)
        
        phone = ''
        for name, tel in CONTACT_TELEPHONES.items():
            if name.lower() in cliente.lower():
                phone = tel
                break
        
        entries.append({
            'fecha_dia': '',
            'cliente': cliente.strip(),
            'empresa': empresa,
            'concepto': concepto,
            'total': total,
            'neto': round(neto, 2),
            'iva': round(iva, 2),
            'source': source,
            'service': service,
            'metodo_pago': entry.get('MetodoPago', '') or '',
            'estado': entry.get('Estado', '') or '',
            'iva_declarado': '',
            'fecha_pago': '',
            'month': mes,
        })
    return entries

# ─── MAIN ───────────────────────────────────────────────────────────────
def main():
    print('=== Sincronizando datos ===')
    
    all_entries = []
    month_totals = {}
    
    # 2026 JSON files
    files_2026 = [
        ('2026_01_ENERO.json', 'Jun2026'),
        ('2026_02_FEBRERO.json', 'Feb2026'),
        ('2026_03_MARZO.json', 'Mar2026'),
        ('2026_05_MAYO.json', 'May2026'),
    ]
    
    for fname, month in files_2026:
        path = os.path.join(SCRIPT_DIR, fname)
        if os.path.exists(path):
            entries = parse_2026_json(path, month)
            all_entries.extend(entries)
            total = sum(e['total'] for e in entries)
            print(f'  [{month}] {len(entries)} entradas, ${total:,.0f}')
            month_totals[month] = {'count': len(entries), 'total': total}
        else:
            print(f'  [{month}] archivo no encontrado: {fname}')
    
    # ABRIL and JUNIO: manually added entries
    abril_entries = [
        {'concepto': 'DRONE FOTOS TERRENO', 'cliente': 'Nimrod', 'total': 70000, 'source': 'Agencia', 'service': 'DRONE'},
        {'concepto': 'miura fotos', 'cliente': 'Vale Marion', 'total': 113050, 'source': 'Agencia', 'service': 'FOTO'},
        {'concepto': 'VIDEOS TERE', 'cliente': 'Tere Laguna', 'total': 60000, 'source': '2Matute', 'service': 'VIDEO'},
        {'concepto': 'rincon peruano', 'cliente': 'Camila Mili', 'total': 25000, 'source': 'Agencia', 'service': 'AGENCIA'},
        {'concepto': 'DDP', 'cliente': 'DDP', 'total': 70000, 'source': '2Matute', 'service': 'VIDEO'},
        {'concepto': 'video drone ayc', 'cliente': 'AyC', 'total': 70000, 'source': 'Siderales', 'service': 'DRONE'},
        {'concepto': 'agenda sesion bautizo', 'cliente': 'Bautizo', 'total': 25000, 'source': '2Matute', 'service': 'REUNION'},
        {'concepto': 'DIA MUJER', 'cliente': 'Dia Mujer', 'total': 98000, 'source': '2Matute', 'service': 'FOTO'},
        {'concepto': 'meson peruano', 'cliente': 'Camila Mili', 'total': 64500, 'source': 'Agencia', 'service': 'AGENCIA'},
        {'concepto': 'foto visa', 'cliente': 'Foto Visa', 'total': 10000, 'source': '2Matute', 'service': 'FOTO'},
    ]
    for e in abril_entries:
        e['neto'] = round(e['total'] / 1.19, 2)
        e['iva'] = round(e['total'] - e['neto'], 2)
        e['empresa'] = ''
        e['metodo_pago'] = ''
        e['estado'] = ''
        e['iva_declarado'] = ''
        e['fecha_pago'] = ''
        e['fecha_dia'] = ''
        e['month'] = 'Abr2026'
    all_entries.extend(abril_entries)
    month_totals['Abr2026'] = {'count': len(abril_entries), 'total': sum(e['total'] for e in abril_entries)}
    print(f'  [Abr2026] {len(abril_entries)} entradas, ${sum(e["total"] for e in abril_entries):,.0f} (inferido)')
    
    # JUNIO entries
    junio_entries = [
        {'concepto': 'SAMSUNG 2026-15 2 VIDEOS', 'cliente': 'Samsung', 'total': 178500, 'source': 'Siderales', 'service': 'CORPORATIVO'},
        {'concepto': 'makrim valpo', 'cliente': 'Macca Makrim', 'total': 80000, 'source': 'Agencia', 'service': 'FOTO'},
    ]
    for e in junio_entries:
        e['neto'] = round(e['total'] / 1.19, 2)
        e['iva'] = round(e['total'] - e['neto'], 2)
        e['empresa'] = ''
        e['metodo_pago'] = ''
        e['estado'] = ''
        e['iva_declarado'] = ''
        e['fecha_pago'] = ''
        e['fecha_dia'] = ''
        e['month'] = 'Jun2026'
    all_entries.extend(junio_entries)
    month_totals['Jun2026'] = {'count': len(junio_entries), 'total': sum(e['total'] for e in junio_entries)}
    print(f'  [Jun2026] {len(junio_entries)} entradas, ${sum(e["total"] for e in junio_entries):,.0f} (inferido)')
    
    # 2025 data
    path_2025 = os.path.join(SCRIPT_DIR, 'all_entries.json')
    if os.path.exists(path_2025):
        entries_2025 = parse_all_entries(path_2025)
        all_entries.extend(entries_2025)
        print(f'  [2025 data] {len(entries_2025)} entradas')
        # Group by month for 2025
        for month in ['Jun2025', 'Jul2025', 'Ago2025', 'Sep2025', 'Oct2025', 'Nov2025', 'Dic2025']:
            month_entries = [e for e in entries_2025 if e['month'] == month]
            if month_entries:
                month_totals[month] = {
                    'count': len(month_entries),
                    'total': sum(e['total'] for e in month_entries)
                }
    
    # ── AGGREGATE CLIENTS ──────────────────────────────────────────────
    clients_dict = defaultdict(lambda: {
        'name': '', 'total': 0, 'neto': 0, 'iva': 0,
        'count': 0, 'source': '', 'phone': '', 'months': set(), 'services': set()
    })
    
    for e in all_entries:
        key = e['cliente'].strip() or e['empresa'] or 'Sin nombre'
        clients_dict[key]['name'] = key
        clients_dict[key]['total'] += e['total']
        clients_dict[key]['neto'] += e['neto']
        clients_dict[key]['iva'] += e['iva']
        clients_dict[key]['count'] += 1
        if not clients_dict[key]['source']:
            clients_dict[key]['source'] = e['source']
        # Try to find phone
        if not clients_dict[key]['phone']:
            for name, tel in CONTACT_TELEPHONES.items():
                if name.lower() in key.lower():
                    clients_dict[key]['phone'] = tel
                    break
        clients_dict[key]['months'].add(e['month'][:3])
        clients_dict[key]['services'].add(e['service'])
    
    clients_list = sorted(clients_dict.values(), key=lambda x: x['total'], reverse=True)
    for c in clients_list:
        c['months'] = sorted(list(c['months']))
        c['services'] = sorted(list(c['services']))
    
    # ── AGGREGATE SERVICES ──────────────────────────────────────────────
    service_totals = defaultdict(lambda: {'total': 0, 'neto': 0, 'count': 0})
    for e in all_entries:
        service_totals[e['service']]['total'] += e['total']
        service_totals[e['service']]['neto'] += e['neto']
        service_totals[e['service']]['count'] += 1
    service_totals = sorted(service_totals.items(), key=lambda x: x[1]['total'], reverse=True)
    
    # ── SUMMARY ─────────────────────────────────────────────────────────
    total_all = sum(e['total'] for e in all_entries)
    neto_all = sum(e['neto'] for e in all_entries)
    iva_all = sum(e['iva'] for e in all_entries)
    
    source_totals = defaultdict(lambda: {'total': 0, 'neto': 0, 'count': 0})
    for e in all_entries:
        source_totals[e['source']]['total'] += e['total']
        source_totals[e['source']]['neto'] += e['neto']
        source_totals[e['source']]['count'] += 1
    
    print(f'\nTotal: ${total_all:,.0f} ({len(all_entries)} entradas, {len(clients_list)} clientes)')
    print(f'Neto: ${neto_all:,.0f} | IVA: ${iva_all:,.0f}')
    for src in ['2Matute', 'Agencia', 'Siderales']:
        if src in source_totals:
            d = source_totals[src]
            print(f'  {src}: ${d["total"]:,.0f} ({d["count"]} entradas)')
    
    print(f'\nServicios:')
    for svc, d in service_totals:
        print(f'  {svc}: ${d["total"]:,.0f} ({d["count"]} veces)')
    
    # ── SAVE data.json ──────────────────────────────────────────────────
    data_out = {
        'sync_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'entries': all_entries,
        'clients': clients_list,
        'services': service_totals,
        'month_totals': dict(sorted(month_totals.items())),
        'summary': {
            'total': total_all,
            'neto': neto_all,
            'iva': iva_all,
            'entries_count': len(all_entries),
            'clients_count': len(clients_list),
            'sources': dict(source_totals),
        }
    }
    
    data_path = os.path.join(SCRIPT_DIR, 'data.json')
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(data_out, f, ensure_ascii=False, indent=2)
    print(f'\nGuardado: data.json ({len(data_out["entries"])} entradas)')
    
    return data_out

if __name__ == '__main__':
    main()