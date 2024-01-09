// フォームバリデーション用の関数
function validateForm() {
    // 例: トレーニング記録フォームのバリデーション
    var date = document.getElementById('date').value;
    var weight = document.getElementById('weight').value;
    var rep = document.getElementById('rep').value;
    var set = document.getElementById('set').value;

    if (!date || weight <= 0 || rep <= 0 || set <= 0) {
        alert('正しい値を入力してください。');
        return false;
    }
    return true;
}

// トレーニング記録フォームが存在する場合、バリデーションを適用
var recordForm = document.querySelector('.record-form');
if (recordForm) {
    recordForm.onsubmit = validateForm;
}

// その他の必要なJavaScriptコード...
