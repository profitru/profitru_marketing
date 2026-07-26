(function () {
  'use strict';

  var root = document.querySelector('[data-amazon-profit-calc]');
  if (!root) return;

  var PRESETS = {
    fashion: { price: 1299, cogs: 480, referral: 17, fulfil: 75, ad: 12, ret: 18 },
    electronics: { price: 2499, cogs: 1650, referral: 8, fulfil: 95, ad: 6, ret: 5 },
    home: { price: 899, cogs: 420, referral: 15, fulfil: 65, ad: 8, ret: 12 },
    beauty: { price: 699, cogs: 210, referral: 12, fulfil: 55, ad: 15, ret: 10 }
  };

  function num(el, fallback) {
    if (!el) return fallback;
    var raw = String(el.value != null ? el.value : '').replace(/,/g, '').trim();
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

  function setVal(name, value) {
    var el = root.querySelector('[name="' + name + '"]');
    if (el) el.value = String(value);
  }

  function applyPreset(key) {
    var p = PRESETS[key];
    if (!p) return;
    setVal('calc_price', p.price);
    setVal('calc_cogs', p.cogs);
    setVal('calc_referral_pct', p.referral);
    setVal('calc_fulfilment', p.fulfil);
    setVal('calc_ad_pct', p.ad);
    setVal('calc_return_pct', p.ret);
    root.querySelectorAll('[data-calc-preset]').forEach(function (btn) {
      btn.classList.toggle('is-active', btn.getAttribute('data-calc-preset') === key);
    });
    recalc();
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
    var payoutEl = root.querySelector('[data-calc-payout]');
    var gapEl = root.querySelector('[data-calc-gap]');
    var toneCard = root.querySelector('[data-calc-real-card]');

    if (price <= 0) {
      if (netEl) netEl.textContent = '\u2014';
      if (marginEl) marginEl.textContent = '\u2014';
      if (payoutEl) payoutEl.textContent = '\u2014';
      if (gapEl) gapEl.textContent = '\u2014';
      return;
    }

    var referralAmt = price * (referralPct / 100);
    var adAmt = price * (adPct / 100);
    // What a settlement-style "net after Amazon fees" often looks like (ignores COGS, ads, returns)
    var payoutLike = price - referralAmt - fulfil;
    var preReturn = price - referralAmt - fulfil - adAmt - cogs;
    var afterReturns = preReturn * (1 - Math.min(100, Math.max(0, retPct)) / 100);
    var marginOnPrice = (afterReturns / price) * 100;
    var gap = payoutLike - afterReturns;

    if (rowReferral) rowReferral.textContent = fmtInr(referralAmt);
    if (rowAd) rowAd.textContent = fmtInr(adAmt);
    if (rowPre) rowPre.textContent = fmtInr(preReturn);
    if (netEl) netEl.textContent = fmtInr(afterReturns);
    if (marginEl) marginEl.textContent = pct(marginOnPrice);
    if (payoutEl) payoutEl.textContent = fmtInr(payoutLike);
    if (gapEl) gapEl.textContent = fmtInr(gap);

    if (toneCard) {
      toneCard.classList.toggle('profit-calc__compare-card--win', afterReturns > 0);
      toneCard.classList.toggle('profit-calc__compare-card--warn', afterReturns <= 0);
    }
  }

  root.querySelectorAll('input').forEach(function (inp) {
    inp.addEventListener('input', function () {
      root.querySelectorAll('[data-calc-preset]').forEach(function (btn) {
        btn.classList.remove('is-active');
      });
      recalc();
    });
    inp.addEventListener('change', recalc);
  });

  root.querySelectorAll('[data-calc-preset]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      applyPreset(btn.getAttribute('data-calc-preset'));
    });
  });

  // Default: Home & kitchen-style example
  applyPreset('home');
})();
