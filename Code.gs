/**
 * 1. 기초 설정 및 메뉴 생성
 */
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('🚀 관리자 시스템')
    .addItem('현장 입력창 열기', 'showInputForm')
    .addItem('회사 전산용 엑셀 생성', 'generateExportFile')
    .addToUi();
}

// 웹 앱 접속 시 실행 (라우팅 및 단순 비밀번호 인증)
function doGet(e) {
  const page = e.parameter.page || 'Login'; // 기본페이지는 로그인
  
  if (page === 'Login') {
    return HtmlService.createTemplateFromFile('Login')
        .evaluate()
        .setTitle('시스템 로그인')
        .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
  }

  // 인증된 세션(또는 파라미터) 확인 로직 (간소화)
  const auth = e.parameter.auth;
  if (!auth) {
    return HtmlService.createHtmlOutput("<script>window.top.location.href='?page=Login';</script>");
  }

  const template = HtmlService.createTemplateFromFile(page);
  template.scriptUrl = ScriptApp.getService().getUrl();
  
  return template.evaluate()
      .setTitle(page === 'Admin' ? '관리자 대시보드' : '현장 판매 등록')
      .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/**
 * 4. 실시간 관리자 인증 (시트 연동)
 */
function checkLogin(password) {
  try {
    const sheet = getAdminSheet();
    const data = sheet.getDataRange().getValues();
    data.shift(); // 헤더 제거
    
    for (let row of data) {
      if (row[2].toString() === password.toString()) {
        return { 
          success: true, 
          role: row[3], 
          branch: row[4], 
          userName: row[1],
          redirect: row[3] === 'Admin' ? 'Admin' : 'Index' 
        };
      }
    }
    return { success: false, message: '비밀번호가 올바르지 않습니다.' };
  } catch (e) {
    return { success: false, message: '인증 시스템 오류: ' + e.message };
  }
}

// 현장 직원용 입력 폼 호출 (기존 수동 호출용)
function showInputForm() {
  const html = HtmlService.createHtmlOutputFromFile('Index')
      .setTitle('현장 판매 등록')
      .setWidth(800)
      .setHeight(600);
  SpreadsheetApp.getUi().showModalDialog(html, '카드키 판매 등록');
}

/**
 * GitHub OAuth2 서비스 설정
 * [중요] CLIENT_ID와 CLIENT_SECRET을 여기에 입력해야 합니다.
 */
function getGitHubService() {
  // 헬퍼 함수: OAuth2 라이브러리가 없을 경우를 대비한 가상 구현 또는 라이브러리 참조
  // 실제 구현 시에는 "OAuth2" 라이브러리 추가 권장 (MDS673_Y_83DsbqZ68z6ke6-0_9v026")
  return {
    hasAccess: function() { return true; }, // 임시 허용 (실제 구현 시 토큰 체크)
    getAuthorizationUrl: function() { return "#"; },
    logout: function() { /* 토큰 삭제 */ }
  };
}

function authCallback(request) {
  const service = getGitHubService();
  const authorized = service.handleCallback(request);
  if (authorized) {
    return HtmlService.createHtmlOutput('인증 완료! 창을 닫고 다시 접속해주세요.');
  } else {
    return HtmlService.createHtmlOutput('인증 실패.');
  }
}

/**
 * 2. 데이터 저장 로직 (현장 앱 -> 시트)
 * 서비스번호를 기준으로 저장
 */
function processForm(data) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const rawSheet = ss.getSheetByName('판매내역') || ss.insertSheet('판매내역');
  
  if (rawSheet.getLastRow() === 0) {
    rawSheet.appendRow(['일자', '지사', '사원명', '서비스번호', '종류1', '종류2', '수량', '단가', '합계액', '비고', '판매구분']);
  }
  
  const saleType = data.saleType || "paid";
  const unitPrice = (saleType === 'free') ? 0 : 3000;
  const qty = parseInt(data.qty) || 0;
  const totalPrice = qty * unitPrice;
  
  rawSheet.appendRow([
    new Date(), 
    data.branch, 
    data.worker, 
    data.serviceNo, 
    data.type1, 
    data.type2, 
    qty, 
    unitPrice,
    totalPrice, 
    data.memo,
    saleType === 'free' ? "무상" : "유상"
  ]);
  
  return "판매 등록 완료되었습니다. (합계: " + totalPrice.toLocaleString() + "원)";
}

/**
 * 지사별/사원별 불출대장 처리 (본사 -> 지사/사원)
 */
function processIssuance(data) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const issSheet = ss.getSheetByName('불출내역') || ss.insertSheet('불출내역');
  
  if (issSheet.getLastRow() === 0) {
    issSheet.appendRow(['일자', '지사', '사원명', '종류1', '종류2', '수량', '비고']);
  }
  
  issSheet.appendRow([
    new Date(),
    data.branch,
    data.worker,
    data.type1,
    data.type2,
    data.qty,
    data.memo || ""
  ]);
  
  return "불출 등록 완료되었습니다.";
}

/**
 * 지사별 사원 목록 가져오기
 */
function getWorkersByBranch(branch) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const workerSheet = ss.getSheetByName('사원정보');
  if (!workerSheet) return [];
  
  const data = workerSheet.getDataRange().getValues();
  data.shift();
  
  return data
    .filter(row => row[0] === branch)
    .map(row => row[1]);
}

/**
 * 3. 데이터 매칭 및 엑셀 다운로드용 데이터 생성
 * 서비스번호를 키값으로 '마스터시트'의 계약/고객/청구번호를 매칭
 */
function generateExportFile() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const salesSheet = ss.getSheetByName('판매내역');
  const masterSheet = ss.getSheetByName('마스터데이터'); // 계약/고객/청구번호가 들어있는 시트
  
  const salesData = salesSheet.getDataRange().getValues();
  const masterData = masterSheet.getDataRange().getValues();
  
  // 결과물 담을 배열 (업로드용 고도화된 컬럼 구성)
  // A: 계약번호, B: 고객번호, C: 청구번호, D: 서비스번호, E: 수량, F: KTT금액, G: 비고(사원명), H: 실패사유
  let exportData = [["계약번호", "고객번호", "청구번호", "서비스번호", "수량", "KTT금액", "비고", "실패사유"]];
  
  for (let i = 1; i < salesData.length; i++) {
    let sNo = salesData[i][3]; // 판매내역의 서비스번호
    let qty = salesData[i][6]; // 수량
    let price = salesData[i][7]; // 금액
    let worker = salesData[i][2]; // 사원명
    let memo = salesData[i][8];  // 비고
    
    let match = masterData.find(row => row[3] == sNo); // 마스터의 서비스번호(D열) 매칭
    
    if (match) {
      exportData.push([
        match[0], // 계약번호
        match[1], // 고객번호
        match[2], // 청구번호
        sNo,      // 서비스번호
        qty,      // 수량 (추가 적용)
        price,    // KTT금액
        worker,   // 비고 (이미지상 사원명이 위치함)
        memo      // 실패사유 (이미지상 메모/사유가 위치함)
      ]);
    } else {
      // 매칭 실패 시에도 내역은 표기 (실패사유 기재)
      exportData.push([
        "", "", "", sNo, qty, price, worker, "마스터 데이터 매칭 실패"
      ]);
    }
  }
  
  // 결과 시트 업데이트 및 포맷팅
  const resultSheet = ss.getSheetByName('업로드용_결과') || ss.insertSheet('업로드용_결과');
  resultSheet.clear();
  
  if (exportData.length > 0) {
    const range = resultSheet.getRange(1, 1, exportData.length, exportData[0].length);
    range.setValues(exportData);
    
    // 기본적인 프리미엄 포맷팅 적용
    resultSheet.getRange(1, 1, 1, exportData[0].length)
      .setBackground("#10b981")
      .setFontColor("white")
      .setFontWeight("bold")
      .setHorizontalAlignment("center");
    
    resultSheet.setFrozenRows(1);
    resultSheet.autoResizeColumns(1, exportData[0].length);
  }
  // SpreadsheetApp.getUi()는 웹 앱 환경에서 사용 불가하므로 데이터만 확보하고 클라이언트에서 처리 유도 가능
  return "업로드용 시트가 생성되었습니다.";
}

/**
 * 4. 재고 등록 로직
 */
function processInventory(data) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const invSheet = ss.getSheetByName('재고내역') || ss.insertSheet('재고내역');
  
  // 헤더 생성
  if (invSheet.getLastRow() === 0) {
    invSheet.appendRow(['일자', '지사', '사원명', '종류', '입고수량', '비고']);
  }
  
  invSheet.appendRow([
    new Date(), 
    data.branch, 
    data.worker || "관리자", 
    data.type, 
    data.qty, 
    data.memo || ""
  ]);
  
  return "재고 등록이 완료되었습니다.";
}

/**
 * 5. 대시보드 시각화용 데이터 집계 (재고 포함)
 */
function getDashboardData(role, branchFilter, year, month, day) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const salesSheet = ss.getSheetByName('판매내역');
  const invSheet = ss.getSheetByName('재고내역');
  const issSheet = ss.getSheetByName('불출내역');
  
  const filterByDate = (dateVal) => {
    if (!dateVal) return true;
    const d = new Date(dateVal);
    const rYear = d.getFullYear().toString();
    const rMonth = (d.getMonth() + 1).toString().padStart(2, '0');
    const rDay = d.getDate().toString().padStart(2, '0');

    if (year && year !== 'ALL' && rYear !== year) return false;
    if (month && month !== 'ALL' && rMonth !== month) return false;
    if (day && day !== 'ALL' && rDay !== day) return false;
    return true;
  };

  let stats = {
    totalSales: 0,
    totalRevenue: 0,
    branchPerformance: {},
    keyTypeDistribution: {},
    dailyTrends: {},
    dailyQtyTrends: {}, // 일별 판매수량 추이
    inventory: {}, // 지사별 현재 재고 (상세)
    workerStock: {}, // 사원별 현재 보유재고 (상세)
    branchStockMetrics: {} // 지사별 통계 (재고 vs 판매 vs 잔여)
  };

  // 1. 판매 데이터 처리
  if (salesSheet) {
    const data = salesSheet.getDataRange().getValues();
    data.shift();
    data.forEach(row => {
      const date = new Date(row[0]);
      if (!filterByDate(date)) return;

      const branch = row[1];
      if (role === 'Branch' && branch !== branchFilter) return;
      const dateStr = Utilities.formatDate(date, "GMT+9", "MM/dd");
      const worker = row[2];
      const type1 = row[4];
      const type2 = row[5];
      const typeKey = type1 + "(" + type2 + ")";
      const qty = parseInt(row[6]) || 0;
      const total = parseInt(row[8]) || 0;

      stats.totalSales += qty;
      stats.totalRevenue += total;
      stats.branchPerformance[branch] = (stats.branchPerformance[branch] || 0) + qty;
      stats.keyTypeDistribution[typeKey] = (stats.keyTypeDistribution[typeKey] || 0) + qty;
      stats.dailyTrends[dateStr] = (stats.dailyTrends[dateStr] || 0) + total;
      stats.dailyQtyTrends[dateStr] = (stats.dailyQtyTrends[dateStr] || 0) + qty;

      // 지사 재고 차감
      if (!stats.inventory[branch]) stats.inventory[branch] = {};
      stats.inventory[branch][typeKey] = (stats.inventory[branch][typeKey] || 0) - qty;

      // 사원 재고 차감
      const wKey = branch + "_" + worker;
      if (!stats.workerStock[wKey]) stats.workerStock[wKey] = {};
      stats.workerStock[wKey][typeKey] = (stats.workerStock[wKey][typeKey] || 0) - qty;
    });
  }

  // 2. 불출 데이터 처리 (본사/지사 -> 사원)
  if (issSheet) {
    const data = issSheet.getDataRange().getValues();
    data.shift();
    data.forEach(row => {
      if (!filterByDate(row[0])) return;
      const branch = row[1];
      if (role === 'Branch' && branch !== branchFilter) return;

      const worker = row[2];
      const type1 = row[3];
      const type2 = row[4];
      const typeKey = type1 + "(" + type2 + ")";
      const qty = parseInt(row[5]) || 0;

      const wKey = branch + "_" + worker;
      if (!stats.workerStock[wKey]) stats.workerStock[wKey] = {};
      stats.workerStock[wKey][typeKey] = (stats.workerStock[wKey][typeKey] || 0) + qty;
    });
  }

  // 3. 재고 데이터 처리 (입고)
  if (invSheet) {
    const data = invSheet.getDataRange().getValues();
    data.shift();
    data.forEach(row => {
      if (!filterByDate(row[0])) return;
      const branch = row[1];
      if (role === 'Branch' && branch !== branchFilter) return;

      const type = row[3];
      const qty = parseInt(row[4]) || 0;

      if (!stats.inventory[branch]) stats.inventory[branch] = {};
      stats.inventory[branch][type] = (stats.inventory[branch][type] || 0) + qty;
      
      // 통계용 합산
      if (!stats.branchStockMetrics[branch]) {
        stats.branchStockMetrics[branch] = { stock: 0, sales: 0, residual: 0 };
      }
      stats.branchStockMetrics[branch].stock += qty;
    });
  }

  // 4. 잔여 수량 계산 및 판매실적 합산 (Metrics 보정)
  Object.keys(stats.branchPerformance).forEach(branch => {
    if (!stats.branchStockMetrics[branch]) {
      stats.branchStockMetrics[branch] = { stock: 0, sales: 0, residual: 0 };
    }
    stats.branchStockMetrics[branch].sales = stats.branchPerformance[branch];
  });

  Object.keys(stats.branchStockMetrics).forEach(branch => {
    stats.branchStockMetrics[branch].residual = stats.branchStockMetrics[branch].stock - stats.branchStockMetrics[branch].sales;
  });

  return stats;
}

/**
 * 6. 슈퍼 관리자 도구 (Admin Management)
 */
function getAdminSheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName('관리자정보');
  if (!sheet) {
    sheet = ss.insertSheet('관리자정보');
    sheet.appendRow(['사용자ID', '성명', '비밀번호', '권한', '지사']);
    // 초기 관리자 계정 생성
    sheet.appendRow(['admin', '최고관리자', 'admin1234', 'Admin', 'HQ']);
    sheet.appendRow(['branch_test', '중앙지사장', '1234', 'Branch', '중앙']);
    
    // 포맷팅
    sheet.getRange(1, 1, 1, 5).setBackground('#10b981').setFontColor('white').setFontWeight('bold');
  }
  return sheet;
}

function getAdminUsers() {
  try {
    const sheet = getAdminSheet();
    const data = sheet.getDataRange().getValues();
    data.shift(); // 헤더 제거
    
    return data.map(row => ({
      id: row[0],
      name: row[1],
      role: row[3],
      branch: row[4]
    }));
  } catch (e) {
    Logger.log("Error in getAdminUsers: " + e.message);
    return [];
  }
}

function resetAdminPassword(userId, newPassword) {
  try {
    const sheet = getAdminSheet();
    const data = sheet.getDataRange().getValues();
    
    for (let i = 1; i < data.length; i++) {
      if (data[i][0] === userId) {
        sheet.getRange(i + 1, 3).setValue(newPassword);
        return { success: true, message: `${data[i][1]}(${userId})님의 비밀번호가 초기화되었습니다.` };
      }
    }
    return { success: false, message: "사용자를 찾을 수 없습니다." };
  } catch (e) {
    return { success: false, message: "비밀번호 초기화 중 오류 발생: " + e.message };
  }
}

function registerAdmin(data) {
  try {
    const sheet = getAdminSheet();
    sheet.appendRow([
      data.userId || "user_" + Math.floor(Date.now() / 1000), // ID 자동생성 또는 입력
      data.name,
      data.password,
      data.role || 'Admin',
      data.branch || 'HQ'
    ]);
    return { success: true, message: `${data.name} 관리자가 등록되었습니다.` };
  } catch (e) {
    return { success: false, message: "관리자 등록 중 오류 발생: " + e.message };
  }
}

function updateAdminInfo(data) {
  try {
    const sheet = getAdminSheet();
    const values = sheet.getDataRange().getValues();
    
    for (let i = 1; i < values.length; i++) {
      if (values[i][0] === data.userId) {
        sheet.getRange(i + 1, 2).setValue(data.name);
        sheet.getRange(i + 1, 4).setValue(data.role);
        sheet.getRange(i + 1, 5).setValue(data.branch);
        return { success: true, message: "정보가 성공적으로 수정되었습니다." };
      }
    }
    return { success: false, message: "사용자를 찾을 수 없습니다." };
  } catch (e) {
    return { success: false, message: "수정 중 오류 발생: " + e.message };
  }
}

/**
 * 시스템 초기화 (모든 데이터 삭제 - 주의!!)
 * 판매내역, 재고내역, 불출내역을 모두 비우고 헤더만 남깁니다.
 * 사원정보와 관리자정보는 기본값으로 복구합니다.
 */
function initializeSystem() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheetsToClear = ['판매내역', '재고내역', '불출내역', '업로드용_결과'];
  
  sheetsToClear.forEach(name => {
    const sheet = ss.getSheetByName(name);
    if (sheet) {
      if (sheet.getLastRow() > 1) {
        sheet.deleteRows(2, sheet.getLastRow() - 1);
      }
    }
  });

  // 사원정보 초기화 (예시 데이터만 남기거나 비우기)
  const workerSheet = ss.getSheetByName('사원정보');
  if (workerSheet && workerSheet.getLastRow() > 1) {
    workerSheet.deleteRows(2, workerSheet.getLastRow() - 1);
    workerSheet.appendRow(['중앙', '홍길동']); // 기본 예시
  }

  // 관리자정보 초기화 (기본 admin 계정만 남기기)
  const adminSheet = ss.getSheetByName('관리자정보');
  if (adminSheet) {
    adminSheet.clear();
    adminSheet.appendRow(['사용자ID', '성명', '비밀번호', '권한', '지사']);
    adminSheet.appendRow(['admin', '최고관리자', 'admin1234', 'Admin', 'HQ']);
  }

  return "시스템의 모든 데이터가 초기화되었습니다.";
}
