// Kayıt formu: Bölge Müdürü seçilince kurulum kodu alanını göster, ad alanını gizle
(function () {
  var f = document.getElementById("kayit-form");
  if (!f) return;
  var kk = document.getElementById("kurulum-alan"), ad = document.getElementById("ad-alan");
  var adIn = document.getElementById("ad"), kkIn = document.getElementById("kk");
  function guncelle() {
    var s = f.querySelector('input[name="mintika"]:checked');
    var bm = s && s.value === "NW1";
    kk.hidden = !bm; ad.hidden = bm;
    kkIn.required = bm; adIn.required = !bm;
  }
  f.addEventListener("change", guncelle);
  guncelle();
})();
