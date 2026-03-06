/**
 * Excel 업로드 데이터 처리
 * JSON 형태로 전달받은 데이터를 '판매내역' 시트에 일괄 추가
 */
function uploadSalesData(dataList) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('판매내역') || ss.insertSheet('판매내역');
  
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(['일자', '지사', '사원명', '서비스번호', '종류1', '종류2', '수량', '단가', '합계액', '비고']);
  }

  const rows = dataList.map(item => {
    return [
      item.date || new Date(),
      item.branch || '',
      item.worker || '',
      item.serviceNo || '',
      item.type1 || '',
      item.type2 || '',
      item.qty || 0,
      item.unitPrice || 3000,
      item.total || (parseInt(item.qty) * (item.unitPrice || 3000)),
      item.note || '엑셀일괄업로드'
    ];
  });

  if (rows.length > 0) {
    sheet.getRange(sheet.getLastRow() + 1, 1, rows.length, rows[0].length).setValues(rows);
  }
  
  return { success: true, count: rows.length };
}
