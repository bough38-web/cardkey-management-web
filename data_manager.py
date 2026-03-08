import json
import os
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# ─── JSON File Helpers ───────────────────────────────────────────

def _load_json(filename):
    filepath = DATA_DIR / filename
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def _save_json(filename, data):
    filepath = DATA_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ─── 판매 등록 ──────────────────────────────────────────────────

def save_sale(sale_data):
    """판매 데이터 저장"""
    sales = _load_json('sales.json')
    sale_data['date'] = sale_data.get('date', datetime.now().strftime('%Y-%m-%d'))
    sales.append(sale_data)
    _save_json('sales.json', sales)
    return "✅ 저장 완료되었습니다."

def get_all_sales():
    return _load_json('sales.json')

# ─── 재고 등록 ──────────────────────────────────────────────────

def save_inventory(inv_data):
    inventory = _load_json('inventory.json')
    inv_data['date'] = inv_data.get('date', datetime.now().strftime('%Y-%m-%d'))
    inventory.append(inv_data)
    _save_json('inventory.json', inventory)
    return "✅ 재고 등록 완료되었습니다."

def get_all_inventory():
    return _load_json('inventory.json')

# ─── 불출 등록 ──────────────────────────────────────────────────

def save_issuance(iss_data):
    issuance = _load_json('issuance.json')
    iss_data['date'] = iss_data.get('date', datetime.now().strftime('%Y-%m-%d'))
    issuance.append(iss_data)
    _save_json('issuance.json', issuance)
    return "✅ 불출 등록 완료되었습니다."

def get_all_issuance():
    return _load_json('issuance.json')

# ─── 사원 정보 ──────────────────────────────────────────────────

def get_workers_by_branch(branch):
    workers = _load_json('workers.json')
    return [w['name'] for w in workers if w.get('branch') == branch]

def get_all_workers():
    return _load_json('workers.json')

# ─── 관리자 로그인 ──────────────────────────────────────────────

def check_login(user_id, password):
    admins = _load_json('admins.json')
    for admin in admins:
        if admin['userId'] == user_id and admin['password'] == password:
            return {
                'success': True,
                'name': admin['name'],
                'role': admin['role'],
                'branch': admin.get('branch', 'HQ')
            }
    return {'success': False}

# ─── 대시보드 데이터 ────────────────────────────────────────────

def get_dashboard_data(role='Admin', branch_filter='', year='', month='', day=''):
    sales = _load_json('sales.json')
    inventory = _load_json('inventory.json')
    issuance = _load_json('issuance.json')

    def date_match(date_str):
        if not date_str:
            return True
        try:
            d = datetime.strptime(date_str, '%Y-%m-%d')
        except (ValueError, TypeError):
            return True
        if year and year != 'ALL' and str(d.year) != str(year):
            return False
        if month and month != 'ALL' and str(d.month).zfill(2) != str(month).zfill(2):
            return False
        if day and day != 'ALL' and str(d.day).zfill(2) != str(day).zfill(2):
            return False
        return True

    stats = {
        'totalSales': 0,
        'totalRevenue': 0,
        'branchPerformance': {},
        'keyTypeDistribution': {},
        'dailyTrends': {},
        'dailyQtyTrends': {},
        'inventory': {},
        'workerStock': {},
        'branchStockMetrics': {}
    }

    # 판매 데이터 처리
    for s in sales:
        if not date_match(s.get('date')):
            continue
        branch = s.get('branch', '')
        if role == 'Branch' and branch != branch_filter:
            continue

        qty = int(s.get('qty', 0))
        total = int(s.get('totalPrice', 0))
        worker = s.get('worker', '')
        type_key = f"{s.get('keyType', '')}({s.get('keySubType', '')})"
        try:
            d = datetime.strptime(s.get('date', ''), '%Y-%m-%d')
            date_str = d.strftime('%m/%d')
        except (ValueError, TypeError):
            date_str = 'N/A'

        stats['totalSales'] += qty
        stats['totalRevenue'] += total
        stats['branchPerformance'][branch] = stats['branchPerformance'].get(branch, 0) + qty
        stats['keyTypeDistribution'][type_key] = stats['keyTypeDistribution'].get(type_key, 0) + qty
        stats['dailyTrends'][date_str] = stats['dailyTrends'].get(date_str, 0) + total
        stats['dailyQtyTrends'][date_str] = stats['dailyQtyTrends'].get(date_str, 0) + qty

        if branch not in stats['inventory']:
            stats['inventory'][branch] = {}
        stats['inventory'][branch][type_key] = stats['inventory'][branch].get(type_key, 0) - qty

        w_key = f"{branch}_{worker}"
        if w_key not in stats['workerStock']:
            stats['workerStock'][w_key] = {}
        stats['workerStock'][w_key][type_key] = stats['workerStock'][w_key].get(type_key, 0) - qty

    # 재고 데이터 처리
    for inv in inventory:
        if not date_match(inv.get('date')):
            continue
        branch = inv.get('branch', '')
        if role == 'Branch' and branch != branch_filter:
            continue

        inv_type = inv.get('type', '')
        qty = int(inv.get('qty', 0))

        if branch not in stats['inventory']:
            stats['inventory'][branch] = {}
        stats['inventory'][branch][inv_type] = stats['inventory'][branch].get(inv_type, 0) + qty

        if branch not in stats['branchStockMetrics']:
            stats['branchStockMetrics'][branch] = {'stock': 0, 'sales': 0, 'residual': 0}
        stats['branchStockMetrics'][branch]['stock'] += qty

    # 불출 데이터 처리
    for iss in issuance:
        if not date_match(iss.get('date')):
            continue
        branch = iss.get('branch', '')
        if role == 'Branch' and branch != branch_filter:
            continue

        worker = iss.get('worker', '')
        type_key = f"{iss.get('type1', '')}({iss.get('type2', '')})"
        qty = int(iss.get('qty', 0))

        w_key = f"{branch}_{worker}"
        if w_key not in stats['workerStock']:
            stats['workerStock'][w_key] = {}
        stats['workerStock'][w_key][type_key] = stats['workerStock'][w_key].get(type_key, 0) + qty

    # 잔여 수량 계산
    for branch, perf_qty in stats['branchPerformance'].items():
        if branch not in stats['branchStockMetrics']:
            stats['branchStockMetrics'][branch] = {'stock': 0, 'sales': 0, 'residual': 0}
        stats['branchStockMetrics'][branch]['sales'] = perf_qty

    for branch in stats['branchStockMetrics']:
        m = stats['branchStockMetrics'][branch]
        m['residual'] = m['stock'] - m['sales']

    return stats

# ─── 데이터 초기화 ──────────────────────────────────────────────

def reset_data(branch_filter='ALL', data_type='ALL'):
    """
    데이터 초기화
    branch_filter: 'ALL' 또는 특정 지사명
    data_type: 'ALL', 'SALES', 'INVENTORY', 'ISSUANCE'
    """
    is_global_branch = not branch_filter or branch_filter == 'ALL'
    is_global_type = not data_type or data_type == 'ALL'

    file_map = {
        'SALES': 'sales.json',
        'INVENTORY': 'inventory.json',
        'ISSUANCE': 'issuance.json'
    }

    files_to_process = []
    if is_global_type:
        files_to_process = list(file_map.values())
    elif data_type in file_map:
        files_to_process = [file_map[data_type]]

    deleted_count = 0

    for filename in files_to_process:
        data = _load_json(filename)
        if is_global_branch:
            deleted_count += len(data)
            _save_json(filename, [])
        else:
            original_len = len(data)
            filtered = [row for row in data if row.get('branch', '') != branch_filter]
            deleted_count += original_len - len(filtered)
            _save_json(filename, filtered)

    # 전체 초기화 시 관리자/사원 정보도 리셋
    if is_global_branch and is_global_type:
        _save_json('workers.json', [
            {"branch": "중앙", "name": "홍길동"}
        ])
        _save_json('admins.json', [
            {"userId": "admin", "name": "최고관리자", "password": "admin1234", "role": "Admin", "branch": "HQ"}
        ])

    type_labels = {'ALL': '전체', 'SALES': '판매실적', 'INVENTORY': '재고', 'ISSUANCE': '불출'}
    type_label = type_labels.get(data_type, data_type) if not is_global_type else '전체'
    branch_label = '전체 지사' if is_global_branch else f'{branch_filter} 지사'

    return f"✅ {branch_label}의 {type_label} 데이터가 초기화되었습니다. ({deleted_count}건 삭제)"

# ─── 초기 데이터 생성 (최초 실행 시) ────────────────────────────

def ensure_initial_data():
    """앱 최초 실행 시 기본 데이터 파일이 없으면 생성"""
    if not (DATA_DIR / 'admins.json').exists():
        _save_json('admins.json', [
            {"userId": "admin", "name": "최고관리자", "password": "admin1234", "role": "Admin", "branch": "HQ"},
            {"userId": "branch_test", "name": "중앙지사장", "password": "1234", "role": "Branch", "branch": "중앙"}
        ])
    if not (DATA_DIR / 'workers.json').exists():
        _save_json('workers.json', [
            {"branch": "중앙", "name": "김현장"},
            {"branch": "중앙", "name": "이사원"},
            {"branch": "강북", "name": "박팀장"},
            {"branch": "강북", "name": "최대리"},
            {"branch": "서대문", "name": "정과장"},
            {"branch": "고양", "name": "한주임"},
            {"branch": "의정부", "name": "송부장"},
            {"branch": "남양주", "name": "윤대리"},
            {"branch": "강릉", "name": "임사원"},
            {"branch": "원주", "name": "오팀장"}
        ])
    if not (DATA_DIR / 'sales.json').exists():
        _save_json('sales.json', [])
    if not (DATA_DIR / 'inventory.json').exists():
        _save_json('inventory.json', [])
    if not (DATA_DIR / 'issuance.json').exists():
        _save_json('issuance.json', [])
