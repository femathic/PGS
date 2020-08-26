function checkSubmit(e) {
  if (e && e.keyCode == 13) document.forms[0].submit();
};

function changeSelected() {
  const keyword = document.getElementById('keyword').value
  if (keyword.length >= 3) document.forms[0].submit();
}