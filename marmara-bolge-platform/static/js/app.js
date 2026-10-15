/* Marmara Bölge Yönetim Platformu — istemci tarafı yardımcılar (satır içi script yok; CSP uyumlu) */
(function () {
  "use strict";
  const $ = (s, k) => (k || document).querySelector(s);
  const $$ = (s, k) => Array.from((k || document).querySelectorAll(s));

  // mobil menü
  const ac = $("#menu-ac");
  if (ac) ac.addEventListener("click", () => $(".kenar").classList.toggle("acik"));

  // onay isteyen formlar
  $$("form[data-onay]").forEach(f => f.addEventListener("submit", e => {
    if (!confirm(f.dataset.onay)) e.preventDefault();
  }));

  // projeler: toplu seçim (arşivle / sil)
  const tf = $("#toplu-form");
  if (tf) {
    const kutular = () => $$('input[name="sec"]', tf);
    const cubuk = $("#toplu-cubuk"), sayi = $("#secili-sayi"), hepsi = $("#tumunu-sec");
    const guncelle = () => {
      const s = kutular().filter(k => k.checked);
      kutular().forEach(k => k.closest("tr").classList.toggle("secili", k.checked));
      if (cubuk) cubuk.hidden = s.length === 0;
      if (sayi) sayi.textContent = s.length;
      if (hepsi) { hepsi.checked = s.length > 0 && s.length === kutular().length; hepsi.indeterminate = s.length > 0 && s.length < kutular().length; }
    };
    tf.addEventListener("change", e => { if (e.target.name === "sec") guncelle(); });
    if (hepsi) hepsi.addEventListener("change", () => { kutular().forEach(k => { k.checked = hepsi.checked; }); guncelle(); });
    const kaldir = $("#secimi-kaldir");
    if (kaldir) kaldir.addEventListener("click", () => { kutular().forEach(k => { k.checked = false; }); guncelle(); });
    tf.addEventListener("submit", e => {
      const n = kutular().filter(k => k.checked).length;
      const islem = e.submitter && e.submitter.value;
      const metin = { sil: n + " proje KALICI olarak silinecek (alt adımları ve gelişme kayıtlarıyla birlikte). Bu işlem geri alınamaz. Emin misiniz?",
                      arsivle: n + " proje arşive kaldırılsın mı? Arşivdeki projeler panoda ve listelerde görünmez; istediğiniz zaman geri alabilirsiniz.",
                      arsivden_cikar: n + " proje arşivden çıkarılsın mı?" }[islem];
      if (!n || (metin && !confirm(metin))) e.preventDefault();
    });
    guncelle();
  }

  // test modu: kullanıcı değiştirme
  const tk = document.getElementById("test-k");
  if (tk) tk.addEventListener("change", () => {
    location.href = tk.dataset.git.replace(/0$/, tk.value);
  });

  // otomatik gönderilen filtreler
  $$("form.filtre select").forEach(s => s.addEventListener("change", () => s.form.submit()));

  const getJSON = url => fetch(url, { credentials: "same-origin" }).then(r => r.json());
  const secenek = (sel, liste, deger, bos) => {
    sel.innerHTML = "";
    if (bos !== undefined) { const o = document.createElement("option"); o.value = ""; o.textContent = bos; sel.appendChild(o); }
    liste.forEach(([v, t]) => {
      const o = document.createElement("option"); o.value = v; o.textContent = t;
      if (String(v) === String(deger)) o.selected = true; sel.appendChild(o);
    });
  };

  // ── proje formu: saha müdürü → il → bayi kademeli, ID önerisi ──
  const pf = $("#proje-form");
  if (pf) {
    const sm = $("#sm_adi"), il = $("#il"), bayi = $("#bayi"), id = $("#id"), ust = $("#ust_id");
    const yeni = pf.dataset.yeni === "1";
    const bayiYukle = () => {
      if (!sm.value) { secenek(bayi, [], "", "← Önce saha müdürü seçin"); secenek(il, [], "", "← Önce saha müdürü seçin"); return; }
      const mevBayi = bayi.dataset.deger || bayi.value, mevIl = il.dataset.deger || il.value;
      getJSON("/api/kanopiler?sm=" + encodeURIComponent(sm.value)).then(l => {
        const liste = l.map(x => [x.etiket, x.etiket + "  ·  " + x.ilce]);
        if (mevBayi && !l.some(x => x.etiket === mevBayi)) liste.unshift([mevBayi, mevBayi + " (mevcut)"]);
        secenek(bayi, liste, mevBayi, "— bayi seçin —");
      });
      getJSON("/api/iller?sm=" + encodeURIComponent(sm.value)).then(l => {
        const liste = l.map(x => [x, x]);
        if (mevIl && !l.includes(mevIl)) liste.unshift([mevIl, mevIl]);
        secenek(il, liste, mevIl, "— il seçin —");
      });
    };
    const idOner = () => {
      if (!yeni || !id) return;
      const q = ust && ust.value ? "ust=" + encodeURIComponent(ust.value) : "sm=" + encodeURIComponent(sm.value);
      if (!sm.value && !(ust && ust.value)) return;
      getJSON("/api/sonraki-id?" + q).then(r => { id.value = r.id; });
    };
    if (sm) sm.addEventListener("change", () => { bayi.dataset.deger = ""; il.dataset.deger = ""; bayiYukle(); idOner(); });
    if (ust) ust.addEventListener("change", () => {
      const o = ust.selectedOptions[0];
      if (o && o.dataset.sm && sm.tagName === "SELECT") { sm.value = o.dataset.sm; bayiYukle(); }
      idOner();
    });
    bayiYukle();
  }

  // ── ziyaret formu: saha müdürü → bayi (+ bayi bilgi kartı) ──
  const zf = $("#ziyaret-form");
  if (zf) {
    const sm = $("#z_sm"), b = $("#bayi_id"), kutu = $("#bayi-bilgi"), prj = $("#proje_id");
    let veri = [];
    const bilgi = () => {
      const x = veri.find(v => String(v.id) === b.value);
      if (!x) { kutu.hidden = true; return; }
      const fmt = n => n == null ? "–" : Number(n).toLocaleString("tr-TR", { maximumFractionDigits: 0 });
      kutu.hidden = false;
      kutu.innerHTML = "";
      const parca = [["İl / İlçe", x.il + " / " + x.ilce], ["Kod", x.ist_kodu], ["Segment", x.segment],
                     ["Ağustos hacmi", fmt(x.ay_hacim) + " m³"], ["Risk", x.risk]];
      parca.forEach(([k, v]) => { const s = document.createElement("span"); s.innerHTML = "<small></small> <b></b>";
        s.querySelector("small").textContent = k + ":"; s.querySelector("b").textContent = v; kutu.appendChild(s);
        kutu.appendChild(document.createTextNode("   ")); });
    };
    const yukle = () => {
      if (!sm.value) { secenek(b, [], "", "← Önce saha müdürü seçin"); kutu.hidden = true; return; }
      const mev = b.dataset.deger || b.value;
      getJSON("/api/bayiler?sm=" + encodeURIComponent(sm.value)).then(l => {
        veri = l;
        secenek(b, l.map(x => [x.id, `${x.ilce} · ${x.unvan.slice(0, 60)}  [${x.segment}]${x.risk !== "Temiz" ? "  ⚠ " + x.risk : ""}`]), mev, "— bayi seçin —");
        bilgi();
      });
      if (prj) $$("option[data-sm]", prj).forEach(o => { o.hidden = o.dataset.sm !== sm.value; });
    };
    sm.addEventListener("change", () => { b.dataset.deger = ""; yukle(); });
    b.addEventListener("change", bilgi);
    yukle();
  }

  // gelişme formu: aşamaya göre seçenekleri göster
  const gf = $("#gelisme-form");
  if (gf) {
    const a = $("#asama", gf), t = $("#tamamla-kutu"), e = $("#engel-kutu");
    const g = () => { if (t) t.hidden = a.value !== "Tamamlandı"; if (e) e.hidden = a.value !== "Engel"; };
    a.addEventListener("change", g); g();
  }

  // ── grafikler ──
  if (window.Chart) {
    Chart.defaults.font.family = '-apple-system,"Segoe UI",Roboto,Arial,sans-serif';
    Chart.defaults.font.size = 11.5;
    Chart.defaults.color = "#667085";
    Chart.defaults.plugins.legend.labels.boxWidth = 12;
  }
  const RENK = { lac: "#2E5395", lac2: "#9DB3DC", kir: "#D14343", yes: "#2E9E4F", tur: "#E08A2E", gri: "#C4CCD8" };
  $$("canvas[data-grafik]").forEach(cv => {
    if (!window.Chart) return;
    const d = JSON.parse($("#" + cv.dataset.veri).textContent);
    const tip = cv.dataset.grafik;
    let cfg;
    if (tip === "sm-tamam") cfg = { type: "bar", data: { labels: d.sm, datasets: [
      { label: "Tamamlanma %", data: d.tamam, backgroundColor: RENK.lac, borderRadius: 4 }] },
      options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, max: 100, ticks: { callback: v => v + "%" } } } } };
    else if (tip === "sm-acik") cfg = { type: "bar", data: { labels: d.sm, datasets: [
      { label: "Açık", data: d.acik, backgroundColor: RENK.lac2, borderRadius: 4 },
      { label: "Geciken", data: d.geciken, backgroundColor: RENK.kir, borderRadius: 4 }] },
      options: { scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } } };
    else if (tip === "sm-pp") cfg = { type: "bar", data: { labels: d.sm, datasets: [
      { label: "2025 Oca–Tem", data: d.pp25, backgroundColor: RENK.gri, borderRadius: 4 },
      { label: "2026 Oca–Tem", data: d.pp26, backgroundColor: RENK.lac, borderRadius: 4 }] },
      options: { scales: { y: { beginAtZero: true, ticks: { callback: v => "%" + v } } } } };
    else if (tip === "il-bp") cfg = { type: "bar", data: { labels: d.iller, datasets: [
      { label: "Pay değişimi (bp)", data: d.bp, backgroundColor: d.bp.map(v => v >= 0 ? RENK.yes : RENK.kir), borderRadius: 4 }] },
      options: { plugins: { legend: { display: false } }, scales: { y: { ticks: { callback: v => v + " bp" } } } } };
    else if (tip === "yas") cfg = { type: "bar", data: { labels: d.sm, datasets: d.yas.map((y, i) => (
      { label: y.ad, data: y.veri, backgroundColor: [RENK.lac2, "#7E9BD0", RENK.lac, RENK.tur, RENK.kir][i], borderRadius: 3 })) },
      options: { scales: { x: { stacked: true }, y: { stacked: true, beginAtZero: true, ticks: { callback: v => v.toLocaleString("tr-TR") } } },
                 plugins: { tooltip: { callbacks: { label: c => c.dataset.label + ": " + c.parsed.y.toLocaleString("tr-TR") + " bin TL" } } } } };
    else if (tip === "onay-sm") cfg = { type: "bar", data: { labels: d.sm, datasets: [
      { label: "Onay talebi", data: d.onay, backgroundColor: RENK.lac, borderRadius: 4 }] },
      options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } } };
    else if (tip === "aylik") cfg = { type: "line", data: { labels: d.aylar, datasets: [
      { label: "2025", data: d.a25, borderColor: RENK.gri, backgroundColor: RENK.gri, tension: .3, pointRadius: 3 },
      { label: "2026", data: d.a26, borderColor: RENK.lac, backgroundColor: RENK.lac, tension: .3, pointRadius: 3, borderWidth: 2.5 }] },
      options: { scales: { y: { ticks: { callback: v => "%" + v } } } } };
    if (cfg) { cfg.options = Object.assign({ responsive: true, maintainAspectRatio: false }, cfg.options); new Chart(cv, cfg); }
  });
})();
