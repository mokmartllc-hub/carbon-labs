/* Carbon Labs — load product catalog from Supabase */
(function () {
  function normalizeSizes(sizes) {
    return (sizes || []).map((s) => ({
      l: s.l,
      p: Number(s.p),
      img: s.img,
      batch: s.batch || '',
      stock: s.stock != null ? Number(s.stock) : 100,
    }));
  }

  function rowToProduct(row) {
    return {
      id: row.id,
      name: row.name,
      cat: row.cat,
      tag: row.tag || '',
      badge: row.badge || null,
      exp: row.exp || '',
      desc: row.desc || '',
      bullets: row.bullets || [],
      storage: row.storage || '',
      sizes: normalizeSizes(row.sizes),
    };
  }

  function sortProds(list) {
    const glp3 = list.find((p) => p.id === 'glp3rt');
    const rest = list.filter((p) => p.id !== 'glp3rt').sort((a, b) => a.name.localeCompare(b.name));
    return glp3 ? [glp3, ...rest] : rest;
  }

  window.applyProductCatalog = function (list) {
    if (!list?.length) return false;
    window.PRODS = sortProds(list);
    if (typeof filterProds === 'function') filterProds();
    const fg = document.getElementById('featgrid');
    if (fg && typeof pcard === 'function') {
      fg.innerHTML = window.PRODS.slice(0, 8).map(pcard).join('');
    }
    if (typeof updCardBtns === 'function') updCardBtns();
    return true;
  };

  window.getProductStock = function (productId, sizeLabel) {
    const p = (window.PRODS || []).find((x) => x.id === productId);
    const sz = p?.sizes?.find((s) => s.l === sizeLabel);
    return sz?.stock != null ? sz.stock : null;
  };

  window.loadCatalogFromDb = async function () {
    try {
      if (!window.SUPABASE_URL || !window.supabase) return false;
      const client = supabase.createClient(window.SUPABASE_URL, window.SUPABASE_ANON_KEY);
      const { data, error } = await client
        .from('products')
        .select('*')
        .eq('active', true)
        .order('sort_order', { ascending: true });
      if (error) throw error;
      if (!data?.length) return false;
      return applyProductCatalog(data.map(rowToProduct));
    } catch (e) {
      console.warn('Catalog load failed, using embedded products', e);
      return false;
    }
  };

  window.dbProductPayload = function (p, sortOrder) {
    return {
      id: p.id,
      name: p.name,
      cat: p.cat,
      tag: p.tag || '',
      badge: p.badge || null,
      exp: p.exp || '',
      desc: p.desc || '',
      bullets: p.bullets || [],
      storage: p.storage || '',
      sizes: normalizeSizes(p.sizes),
      active: true,
      sort_order: sortOrder != null ? sortOrder : 0,
      updated_at: new Date().toISOString(),
    };
  };
})();
