(function () {
  'use strict';

  var root = document.querySelector('[data-amazon-profit-calc]');
  if (!root) return;

  function num(el, fallback) {
    if (!el) return fallback;
    var raw = String(el.value != null ? el.value : el.textContent).replace(/,/g, '').trim();
    var n = parseFloat(raw);
    return isFinite(n) ? n : fallback;
  }

  function fmtInr(n) {
    if (!isFinite(n)) return '\u2014';
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: n % 1 === 0 ? 0 : 2
    }).format(n);
  }

  function pct(n) {
    if (!isFinite(n)) return '\u2014';
    return n.toFixed(1) + '%';
  }

  function recalc() {
    var price = num(root.querySelector('[name="calc_price"]'), 0);
    var cogs = num(root.querySelector('[name="calc_cogs"]'), 0);
    var referralPct = num(root.querySelector('[name="calc_referral_pct"]'), 0);
    var fulfil = num(root.querySelector('[name="calc_fulfilment"]'), 0);
    var adPct = num(root.querySelector('[name="calc_ad_pct"]'), 0);
    var retPct = num(root.querySelector('[name="calc_return_pct"]'), 0);

    var netEl = root.querySelector('[data-calc-net]');
    var marginEl = root.querySelector('[data-calc-margin]');
    var rowReferral = root.querySelector('[data-calc-row-referral]');
    var rowAd = root.querySelector('[data-calc-row-ad]');
    var rowPre = root.querySelector('[data-calc-row-pre]');

    if (price <= 0) {
      if (netEl) netEl.textContent = '\u2014';
      if (marginEl) marginEl.textContent = '\u2014';
      return;
    }

    var referralAmt = price * (referralPct / 100);
    var adAmt = price * (adPct / 100);
    var preReturn = price - referralAmt - fulfil - adAmt - cogs;
    var afterReturns = preReturn * (1 - Math.min(100, Math.max(0, retPct)) / 100);
    var marginOnPrice = (afterReturns / price) * 100;

    if (rowReferral) rowReferral.textContent = fmtInr(referralAmt);
    if (rowAd) rowAd.textContent = fmtInr(adAmt);
    if (rowPre) rowPre.textContent = fmtInr(preReturn);
    if (netEl) netEl.textContent = fmtInr(afterReturns);
    if (marginEl) marginEl.textContent = pct(marginOnPrice);
  }

  root.querySelectorAll('input').forEach(function (inp) {
    inp.addEventListener('input', recalc);
    inp.addEventListener('change', recalc);
  });

  recalc();
})();
