/* Carbon Labs — Admin panel */
(function () {
  let isAdmin = false;
  let adminTab = 'dashboard';
  let editingProductId = null;

  function esc(s) {
    return String(s ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function fmtDate(iso) {
    return new Date(iso).toLocaleString();
  }

  function fmtMoney(n) {
    return '$' + Number(n).toFixed(2);
  }

  function getClient() {
    return typeof getSupabase === 'function' ? getSupabase() : null;
  }

  function getAdminPass() {
    return sessionStorage.getItem('cl_admin_pass') || '';
  }

  function adminSessionActive() {
    return sessionStorage.getItem('cl_admin') === '1' && !!getAdminPass();
  }

  function renderAdminLogin() {
    const root = document.getElementById('admin-root');
    if (!root) return;
    root.innerHTML = `
      <div class="admin-card" style="max-width:420px;margin:40px auto">
        <h2>Admin login</h2>
        <p class="acct-sub">Enter the admin password to manage products, orders, and stock.</p>
        <div class="auth-err" id="admin-login-err"></div>
        <div class="auth-field">
          <label>Password</label>
          <input class="auth-input" id="admin-pass" type="password" placeholder="Admin password"
            onkeydown="if(event.key==='Enter')submitAdminPassword()">
        </div>
        <button class="auth-btn" style="width:100%;margin-top:8px" onclick="submitAdminPassword()">Unlock admin →</button>
      </div>`;
    document.getElementById('admin-pass')?.focus();
  }

  window.submitAdminPassword = async function () {
    const err = document.getElementById('admin-login-err');
    const pwd = document.getElementById('admin-pass')?.value || '';
    err?.classList.remove('show');
    if (!pwd) {
      if (err) {
        err.textContent = 'Enter the admin password.';
        err.classList.add('show');
      }
      return;
    }
    if (window.ADMIN_PASSWORD && pwd !== window.ADMIN_PASSWORD) {
      if (err) {
        err.textContent = 'Incorrect password.';
        err.classList.add('show');
      }
      return;
    }
    const client = getClient();
    if (!client) {
      if (err) {
        err.textContent = 'Supabase is not configured.';
        err.classList.add('show');
      }
      return;
    }
    const { data, error } = await client.rpc('admin_verify', { pass: pwd });
    if (error || !data) {
      if (err) {
        err.textContent = error ? errMsg(error) : 'Incorrect password.';
        err.classList.add('show');
      }
      return;
    }
    sessionStorage.setItem('cl_admin', '1');
    sessionStorage.setItem('cl_admin_pass', pwd);
    isAdmin = true;
    renderAdminPage();
  };

  window.adminLock = function () {
    sessionStorage.removeItem('cl_admin');
    sessionStorage.removeItem('cl_admin_pass');
    isAdmin = false;
    renderAdminLogin();
  };

  window.refreshAdminAccess = async function () {
    isAdmin = adminSessionActive();
    return isAdmin;
  };

  function adminNav() {
    const tabs = [
      ['dashboard', 'Dashboard'],
      ['orders', 'Orders'],
      ['products', 'Products'],
      ['messages', 'Messages'],
      ['newsletter', 'Newsletter'],
    ];
    return `<nav class="admin-tabs">${tabs
      .map(
        ([id, label]) =>
          `<button type="button" class="admin-tab ${adminTab === id ? 'active' : ''}" onclick="setAdminTab('${id}')">${label}</button>`
      )
      .join('')}<button type="button" class="admin-tab" style="margin-left:auto" onclick="adminLock()">Lock</button></nav>`;
  }

  window.setAdminTab = function (tab) {
    adminTab = tab;
    renderAdminPage();
  };

  async function loadDashboard() {
    const pass = getAdminPass();
    const { data, error } = await getClient().rpc('admin_get_stats', { pass });
    if (error) throw error;
    const stats = data || {};
    const lowStock = stats.low_stock || [];
    return `
      <div class="admin-stats">
        <div class="admin-stat"><div class="n">${stats.orders_count ?? 0}</div><div class="l">Orders</div></div>
        <div class="admin-stat"><div class="n">${fmtMoney(stats.revenue ?? 0)}</div><div class="l">Revenue</div></div>
        <div class="admin-stat"><div class="n">${stats.products_count ?? 0}</div><div class="l">Products</div></div>
        <div class="admin-stat"><div class="n">${stats.messages_count ?? 0}</div><div class="l">Messages</div></div>
        <div class="admin-stat"><div class="n">${stats.subscribers_count ?? 0}</div><div class="l">Subscribers</div></div>
      </div>
      ${
        lowStock.length
          ? `<div class="admin-alert">Low stock: ${lowStock.map(esc).join(', ')}</div>`
          : '<div class="admin-note">All products have stock above 5 units.</div>'
      }`;
  }

  async function loadOrdersPanel() {
    const { data, error } = await getClient().rpc('admin_list_orders', { pass: getAdminPass() });
    if (error) throw error;
    if (!data?.length) return '<div class="admin-empty">No orders yet.</div>';
    return `<div class="admin-table-wrap"><table class="admin-table">
      <thead><tr><th>Order</th><th>Customer</th><th>Total</th><th>Status</th><th>Date</th></tr></thead>
      <tbody>${data
        .map(
          (o) => `<tr>
          <td><strong>${esc(o.order_number)}</strong><div class="admin-sub">${(o.items || []).length} line(s)</div></td>
          <td>${esc(o.shipping_name)}<div class="admin-sub">${esc(o.shipping_email)}</div></td>
          <td>${fmtMoney(o.total)}</td>
          <td><select class="admin-select" onchange="adminUpdateOrderStatus(${o.id}, this.value)">
            ${['confirmed', 'processing', 'shipped', 'delivered']
              .map((s) => `<option value="${s}" ${o.status === s ? 'selected' : ''}>${s}</option>`)
              .join('')}
          </select></td>
          <td>${fmtDate(o.created_at)}</td>
        </tr>`
        )
        .join('')}</tbody></table></div>`;
  }

  window.adminUpdateOrderStatus = async function (id, status) {
    try {
      const { error } = await getClient().rpc('admin_update_order', {
        pass: getAdminPass(),
        order_id: id,
        new_status: status,
      });
      if (error) throw error;
    } catch (e) {
      alert(errMsg(e));
    }
  };

  async function loadProductsPanel() {
    const { data, error } = await getClient().rpc('admin_list_products', { pass: getAdminPass() });
    if (error) throw error;
    const list = data || [];
  return `
      <div class="admin-toolbar">
        <button class="auth-btn admin-btn-sm" onclick="adminSyncCatalog()">Sync from site catalog</button>
        <button class="auth-btn admin-btn-sm admin-btn-ghost" onclick="adminEditProduct(null)">+ New product</button>
      </div>
      ${
        !list.length
          ? '<div class="admin-empty">No products in database. Click “Sync from site catalog” to import.</div>'
          : `<div class="admin-table-wrap"><table class="admin-table">
        <thead><tr><th>Product</th><th>Category</th><th>Price</th><th>Stock</th><th>Active</th><th></th></tr></thead>
        <tbody>${list
          .map((p) => {
            const minP = Math.min(...(p.sizes || []).map((s) => Number(s.p) || 0));
            const totalStock = (p.sizes || []).reduce((s, x) => s + (Number(x.stock) || 0), 0);
            return `<tr>
              <td><strong>${esc(p.name)}</strong><div class="admin-sub">${esc(p.id)}</div></td>
              <td>${esc(p.cat)}</td>
              <td>from ${fmtMoney(minP)}</td>
              <td>${totalStock}</td>
              <td>${p.active ? '✓' : '—'}</td>
              <td><button class="admin-link-btn" onclick="adminEditProduct('${esc(p.id)}')">Edit</button></td>
            </tr>`;
          })
          .join('')}</tbody></table></div>`
      }
      <div id="admin-product-editor"></div>`;
  }

  window.adminSyncCatalog = async function () {
    const source = window.PRODS_RAW || window.PRODS;
    if (!source?.length) {
      alert('No embedded catalog found.');
      return;
    }
    const rows = source.map((p, i) => dbProductPayload(p, i));
    try {
      const client = getClient();
      const pass = getAdminPass();
      for (const row of rows) {
        const { error } = await client.rpc('admin_upsert_product', { pass, payload: row });
        if (error) throw error;
      }
      await loadCatalogFromDb();
      alert('Catalog synced (' + rows.length + ' products).');
      renderAdminPage();
    } catch (e) {
      alert(errMsg(e));
    }
  };

  window.adminEditProduct = async function (id) {
    editingProductId = id;
    const el = document.getElementById('admin-product-editor');
    if (!el) return;
    let p = null;
    if (id) {
      const { data } = await getClient().rpc('admin_list_products', { pass: getAdminPass() });
      p = (data || []).find((x) => x.id === id) || null;
    }
    if (!p) {
      p = {
        id: '',
        name: '',
        cat: 'Metabolic Research',
        tag: '',
        badge: '',
        exp: '06/27',
        desc: '',
        bullets: [],
        storage: '',
        sizes: [{ l: '10mg', p: 0, img: '', batch: '', stock: 100 }],
        active: true,
      };
    }
    const sizes = p.sizes || [];
    el.innerHTML = `
      <div class="admin-card" style="margin-top:20px">
        <h2>${id ? 'Edit product' : 'New product'}</h2>
        <div class="auth-err" id="admin-prod-err"></div>
        <div class="acct-row">
          <div class="auth-field"><label>ID (slug)</label><input class="auth-input" id="ap-id" value="${esc(p.id)}" ${id ? 'disabled' : ''}></div>
          <div class="auth-field"><label>Name</label><input class="auth-input" id="ap-name" value="${esc(p.name)}"></div>
        </div>
        <div class="acct-row">
          <div class="auth-field"><label>Category</label><input class="auth-input" id="ap-cat" value="${esc(p.cat)}"></div>
          <div class="auth-field"><label>Tag line</label><input class="auth-input" id="ap-tag" value="${esc(p.tag)}"></div>
        </div>
        <div class="acct-row">
          <div class="auth-field"><label>Badge</label><input class="auth-input" id="ap-badge" value="${esc(p.badge || '')}" placeholder="Trending"></div>
          <div class="auth-field"><label>Expiry</label><input class="auth-input" id="ap-exp" value="${esc(p.exp || '')}"></div>
        </div>
        <div class="auth-field"><label>Description</label><textarea class="auth-input admin-textarea" id="ap-desc">${esc(p.desc || '')}</textarea></div>
        <div class="auth-field"><label>Storage</label><input class="auth-input" id="ap-storage" value="${esc(p.storage || '')}"></div>
        <div class="auth-field"><label>Bullets (one per line)</label><textarea class="auth-input admin-textarea" id="ap-bullets">${esc((p.bullets || []).join('\n'))}</textarea></div>
        <h3 style="color:white;font-size:14px;margin:16px 0 8px">Sizes / pricing / stock</h3>
        <div id="ap-sizes">${sizes
          .map(
            (s, i) => `<div class="admin-size-row" data-i="${i}">
            <input class="auth-input" placeholder="Size" value="${esc(s.l)}" data-f="l">
            <input class="auth-input" type="number" step="0.01" placeholder="Price" value="${s.p}" data-f="p">
            <input class="auth-input" type="number" placeholder="Stock" value="${s.stock != null ? s.stock : 100}" data-f="stock">
            <input class="auth-input" placeholder="Batch" value="${esc(s.batch || '')}" data-f="batch">
            <input class="auth-input" placeholder="Image URL" value="${esc(typeof s.img === 'string' && s.img.length < 200 ? s.img : '')}" data-f="img">
          </div>`
          )
          .join('')}</div>
        <button type="button" class="admin-link-btn" onclick="adminAddSizeRow()">+ Add size</button>
        <label style="display:flex;align-items:center;gap:8px;margin:16px 0;color:rgba(255,255,255,.6);font-size:13px">
          <input type="checkbox" id="ap-active" ${p.active !== false ? 'checked' : ''}> Active (visible on site)
        </label>
        <div style="display:flex;gap:10px;margin-top:12px">
          <button class="auth-btn admin-btn-sm" onclick="adminSaveProduct()">Save product</button>
          ${id ? `<button class="auth-btn admin-btn-sm admin-btn-danger" onclick="adminDeleteProduct('${esc(id)}')">Delete</button>` : ''}
          <button class="auth-btn admin-btn-sm admin-btn-ghost" onclick="adminCloseEditor()">Cancel</button>
        </div>
      </div>`;
    el.scrollIntoView({ behavior: 'smooth' });
  };

  window.adminAddSizeRow = function () {
    const wrap = document.getElementById('ap-sizes');
    if (!wrap) return;
    const div = document.createElement('div');
    div.className = 'admin-size-row';
    div.innerHTML = `
      <input class="auth-input" placeholder="Size" data-f="l">
      <input class="auth-input" type="number" step="0.01" placeholder="Price" data-f="p">
      <input class="auth-input" type="number" placeholder="Stock" value="100" data-f="stock">
      <input class="auth-input" placeholder="Batch" data-f="batch">
      <input class="auth-input" placeholder="Image URL" data-f="img">`;
    wrap.appendChild(div);
  };

  window.adminCloseEditor = function () {
    editingProductId = null;
    const el = document.getElementById('admin-product-editor');
    if (el) el.innerHTML = '';
  };

  function readSizeRows() {
    return Array.from(document.querySelectorAll('#ap-sizes .admin-size-row'))
      .map((row) => {
        const get = (f) => row.querySelector(`[data-f="${f}"]`)?.value?.trim() || '';
        const imgVal = get('img');
        let img = imgVal;
        if (!img && editingProductId) {
          const existing = (window.PRODS || []).find((p) => p.id === editingProductId);
          const match = existing?.sizes?.find((s) => s.l === get('l'));
          if (match) img = match.img;
        }
        return {
          l: get('l'),
          p: Number(get('p')) || 0,
          stock: Number(get('stock')) || 0,
          batch: get('batch'),
          img: img || '',
        };
      })
      .filter((s) => s.l);
  }

  window.adminSaveProduct = async function () {
    const err = document.getElementById('admin-prod-err');
    const id = (document.getElementById('ap-id')?.value || editingProductId || '').trim();
    const payload = {
      id,
      name: document.getElementById('ap-name')?.value.trim(),
      cat: document.getElementById('ap-cat')?.value.trim(),
      tag: document.getElementById('ap-tag')?.value.trim(),
      badge: document.getElementById('ap-badge')?.value.trim() || null,
      exp: document.getElementById('ap-exp')?.value.trim(),
      desc: document.getElementById('ap-desc')?.value.trim(),
      storage: document.getElementById('ap-storage')?.value.trim(),
      bullets: (document.getElementById('ap-bullets')?.value || '')
        .split('\n')
        .map((b) => b.trim())
        .filter(Boolean),
      sizes: readSizeRows(),
      active: document.getElementById('ap-active')?.checked !== false,
      updated_at: new Date().toISOString(),
    };
    if (!payload.id || !payload.name || !payload.sizes.length) {
      err.textContent = 'ID, name, and at least one size are required.';
      err.classList.add('show');
      return;
    }
    err.classList.remove('show');
    try {
      const { error } = await getClient().rpc('admin_upsert_product', {
        pass: getAdminPass(),
        payload,
      });
      if (error) throw error;
      await loadCatalogFromDb();
      adminCloseEditor();
      renderAdminPage();
    } catch (e) {
      err.textContent = errMsg(e);
      err.classList.add('show');
    }
  };

  window.adminDeleteProduct = async function (id) {
    if (!confirm('Delete product ' + id + '?')) return;
    try {
      const { error } = await getClient().rpc('admin_delete_product', {
        pass: getAdminPass(),
        product_id: id,
      });
      if (error) throw error;
      await loadCatalogFromDb();
      renderAdminPage();
    } catch (e) {
      alert(errMsg(e));
    }
  };

  async function loadMessagesPanel() {
    const { data, error } = await getClient().rpc('admin_list_messages', { pass: getAdminPass() });
    if (error) throw error;
    if (!data?.length) return '<div class="admin-empty">No messages.</div>';
    return data
      .map(
        (m) => `<div class="admin-card admin-card-sm">
        <div class="admin-card-hd"><strong>${esc(m.subject)}</strong><span>${fmtDate(m.created_at)}</span></div>
        <div class="admin-sub">${esc(m.name)} · ${esc(m.email)}${m.order_number ? ' · Order ' + esc(m.order_number) : ''}</div>
        <p style="font-size:13px;color:rgba(255,255,255,.55);margin-top:8px;line-height:1.6">${esc(m.message)}</p>
      </div>`
      )
      .join('');
  }

  async function loadNewsletterPanel() {
    const { data, error } = await getClient().rpc('admin_list_subscribers', { pass: getAdminPass() });
    if (error) throw error;
    if (!data?.length) return '<div class="admin-empty">No subscribers yet.</div>';
    return `<div class="admin-table-wrap"><table class="admin-table">
      <thead><tr><th>Email</th><th>Subscribed</th></tr></thead>
      <tbody>${data.map((r) => `<tr><td>${esc(r.email)}</td><td>${fmtDate(r.created_at)}</td></tr>`).join('')}</tbody>
    </table></div>`;
  }

  window.renderAdminPage = async function () {
    const root = document.getElementById('admin-root');
    if (!root) return;
    if (!adminSessionActive()) {
      renderAdminLogin();
      return;
    }
    isAdmin = true;
    root.innerHTML = adminNav() + '<div class="orders-loading">Loading…</div>';
    try {
      let body = '';
      if (adminTab === 'dashboard') body = await loadDashboard();
      else if (adminTab === 'orders') body = await loadOrdersPanel();
      else if (adminTab === 'products') body = await loadProductsPanel();
      else if (adminTab === 'messages') body = await loadMessagesPanel();
      else if (adminTab === 'newsletter') body = await loadNewsletterPanel();
      root.innerHTML = adminNav() + '<div class="admin-panel-body">' + body + '</div>';
      if (editingProductId && adminTab === 'products') {
        setTimeout(() => adminEditProduct(editingProductId), 0);
      }
    } catch (e) {
      root.innerHTML = adminNav() + `<div class="admin-empty">Error: ${esc(errMsg(e))}</div>`;
    }
  };

  window.goToAdmin = function () {
    go('admin');
  };

  setTimeout(() => {
    if (typeof loadCatalogFromDb === 'function') loadCatalogFromDb();
    if (adminSessionActive()) isAdmin = true;
  }, 200);

  if (location.hash === '#admin') {
    setTimeout(() => goToAdmin(), 600);
  }
})();
