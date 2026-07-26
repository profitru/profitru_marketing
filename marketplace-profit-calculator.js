/**
 * Shared marketplace unit-economics calculator.
 * Mount: [data-marketplace-profit-calc][data-marketplace="flipkart|meesho|ebay"]
 */
(function () {
  'use strict';

  var root = document.querySelector('[data-marketplace-profit-calc]');
  if (!root) return;

  var market = (root.getAttribute('data-marketplace') || '').toLowerCase();

  var MARKETS = {
    flipkart: {
      currency: 'INR',
      locale: 'en-IN',
      defaultPreset: 'fashion',
      feeField: 'Commission + fixed fees (%, blended)',
      fulfilField: 'Fulfilment / shipping per unit (\u20b9)',
      payoutNote: 'Price \u2212 commission \u2212 fulfilment (ignores COGS, ads, returns)',
      realNote: 'Also subtracts COGS + ads, then applies return / RTO rate',
      payoutLabel: 'Looks like after Flipkart fees',
      realLabel: 'Real contribution after returns',
      feeRow: 'Commission (est.)',
      presets: {
        fashion: { price: 999, cogs: 380, referral: 18, fulfil: 70, ad: 10, ret: 16 },
        electronics: { price: 2999, cogs: 2100, referral: 8, fulfil: 90, ad: 5, ret: 4 },
        home: { price: 799, cogs: 360, referral: 14, fulfil: 65, ad: 7, ret: 12 },
        beauty: { price: 549, cogs: 180, referral: 16, fulfil: 50, ad: 12, ret: 14 }
      }
    },
    meesho: {
      currency: 'INR',
      locale: 'en-IN',
      defaultPreset: 'ethnic',
      feeField: 'Commission / platform fee (%, blended)',
      fulfilField: 'Shipping + packaging per unit (\u20b9)',
      payoutNote: 'Price \u2212 platform fee \u2212 shipping (ignores COGS, ads, RTO)',
      realNote: 'Also subtracts COGS + ads, then applies return / RTO rate',
      payoutLabel: 'Looks like after Meesho fees',
      realLabel: 'Real contribution after RTO / returns',
      feeRow: 'Platform fee (est.)',
      presets: {
        ethnic: { price: 499, cogs: 220, referral: 5, fulfil: 55, ad: 4, ret: 28 },
        beauty: { price: 299, cogs: 95, referral: 6, fulfil: 40, ad: 8, ret: 22 },
        home: { price: 399, cogs: 170, referral: 5, fulfil: 50, ad: 3, ret: 20 },
        kids: { price: 449, cogs: 190, referral: 5, fulfil: 48, ad: 5, ret: 25 }
      }
    },
    ebay: {
      currency: 'INR',
      locale: 'en-IN',
      defaultPreset: 'electronics',
      feeField: 'Final value + fees (%, blended)',
      fulfilField: 'Shipping / postage per unit (\u20b9)',
      payoutNote: 'Price \u2212 eBay fees \u2212 shipping (ignores COGS, ads, returns)',
      realNote: 'Also subtracts COGS + promoted listings, then applies return rate',
      payoutLabel: 'Looks like after eBay fees',
      realLabel: 'Real contribution after returns',
      feeRow: 'eBay fees (est.)',
      presets: {
        electronics: { price: 4500, cogs: 3200, referral: 11, fulfil: 180, ad: 6, ret: 6 },
        fashion: { price: 1800, cogs: 700, referral: 13, fulfil: 120, ad: 8, ret: 12 },
        collectibles: { price: 2500, cogs: 900, referral: 12, fulfil: 200, ad: 5, ret: 4 },
        home: { price: 3200, cogs: 1800, referral: 12, fulfil: 250, ad: 4, ret: 8 }
      }
    }
  };

  var cfg = MARKETS[market];
  if (!cfg) return;

  function num(el, fallback) {
    if (!el) return fallback;
    var raw = String(el.value != null ? el.value : '').replace(/,/g, '').trim();
    var n = parseFloat(raw);
    return isFinite(n) ? n : fallback;
  }

  function fmtMoney(n) {
    if (!isFinite(n)) return '\u2014';
    return new Intl.NumberFormat(cfg.locale, {
      style: 'currency',
      currency: cfg.currency,
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
    var p = cfg.presets[key];
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
    var payoutLike = price - referralAmt - fulfil;
    var preReturn = price - referralAmt - fulfil - adAmt - cogs;
    var afterReturns = preReturn * (1 - Math.min(100, Math.max(0, retPct)) / 100);
    var marginOnPrice = (afterReturns / price) * 100;
    var gap = payoutLike - afterReturns;

    if (rowReferral) rowReferral.textContent = fmtMoney(referralAmt);
    if (rowAd) rowAd.textContent = fmtMoney(adAmt);
    if (rowPre) rowPre.textContent = fmtMoney(preReturn);
    if (netEl) netEl.textContent = fmtMoney(afterReturns);
    if (marginEl) marginEl.textContent = pct(marginOnPrice);
    if (payoutEl) payoutEl.textContent = fmtMoney(payoutLike);
    if (gapEl) gapEl.textContent = fmtMoney(gap);

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

  applyPreset(cfg.defaultPreset);
})();
