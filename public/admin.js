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

  async function checkAdmin() {
    try {
      const client = getClient();
      if (!client) {
        isAdmin = false;
        return false;
      }
      const {
        data: { user },
      } = await client.auth.getUser();
      if (!user) {
        isAdmin = false;
        return false;
      }
      const { data, error } = await client
        .from('profiles')
        .select('is_admin')
        .eq('id', user.id)
        .maybeSingle();
      if (error) throw error;
      isAdmin = !!data?.is_admin;
      window._adminCheckEmail = user.email || '';
      return isAdmin;
    } catch (e) {
      console.warn('Admin check failed', e);
      isAdmin = false;
      return false;
    }
  }

  window.refreshAdminAccess = checkAdmin;

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
      .join('')}</nav>`;
  }

  window.setAdminTab = function (tab) {
    adminTab = tab;
    renderAdminPage();
  };

  async function loadDashboard() {
    const client = getClient();
    const [orders, products, messages, subs] = await Promise.all([
      client.from('orders').select('total, created_at', { count: 'exact' }),
      client.from('products').select('id, sizes'),
      client.from('contact_messages').select('id', { count: 'exact', head: true }),
      client.from('newsletter_subscribers').select('id', { count: 'exact', head: true }),
    ]);
    const orderList = orders.data || [];
    const revenue = orderList.reduce((s, o) => s + Number(o.total), 0);
    const lowStock = [];
    (products.data || []).forEach((p) => {
      (p.sizes || []).forEach((s) => {
        if (s.stock != null && Number(s.stock) <= 5) {
          lowStock.push(`${p.id} · ${s.l}`);
        }
      });
    });
    return `
      <div class="admin-stats">
        <div class="admin-stat"><div class="n">${orders.count ?? orderList.length}</div><div class="l">Orders</div></div>
        <div class="admin-stat"><div class="n">${fmtMoney(revenue)}</div><div class="l">Revenue</div></div>
        <div class="admin-stat"><div class="n">${products.data?.length || 0}</div><div class="l">Products</div></div>
        <div class="admin-stat"><div class="n">${messages.count ?? 0}</div><div class="l">Messages</div></div>
        <div class="admin-stat"><div class="n">${subs.count ?? 0}</div><div class="l">Subscribers</div></div>
      </div>
      ${
        lowStock.length
          ? `<div class="admin-alert">Low stock: ${lowStock.map(esc).join(', ')}</div>`
          : '<div class="admin-note">All products have stock above 5 units.</div>'
      }`;
  }

  async function loadOrdersPanel() {
    const { data, error } = await getClient()
      .from('orders')
      .select('*')
      .order('created_at', { ascending: false });
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
      const { error } = await getClient().from('orders').update({ status }).eq('id', id);
      if (error) throw error;
    } catch (e) {
      alert(errMsg(e));
    }
  };

  async function loadProductsPanel() {
    const { data, error } = await getClient().from('products').select('*').order('sort_order');
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
      const { error } = await getClient().from('products').upsert(rows);
      if (error) throw error;
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
      const { data } = await getClient().from('products').select('*').eq('id', id).maybeSingle();
      p = data;
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
      const { error } = await getClient().from('products').upsert(payload);
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
      const { error } = await getClient().from('products').delete().eq('id', id);
      if (error) throw error;
      await loadCatalogFromDb();
      renderAdminPage();
    } catch (e) {
      alert(errMsg(e));
    }
  };

  async function loadMessagesPanel() {
    const { data, error } = await getClient()
      .from('contact_messages')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(50);
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
    const { data, error } = await getClient()
      .from('newsletter_subscribers')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(100);
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
    if (!isAdmin) {
      root.innerHTML = '<div class="admin-empty">Access denied. Admin account required.</div>';
      return;
    }
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

  window.appendAdminNavLink = function () {
    const dd = document.getElementById('user-dropdown');
    if (!dd || !isAdmin) return;
    if (dd.querySelector('[data-admin-link]')) return;
    const sep = dd.querySelector('.ud-sep');
    const adminLink = document.createElement('a');
    adminLink.setAttribute('data-admin-link', '1');
    adminLink.textContent = 'Admin';
    adminLink.setAttribute('onclick', "go('admin')");
    if (sep) dd.insertBefore(adminLink, sep);
    else dd.appendChild(adminLink);
  };

  setTimeout(() => {
    loadCatalogFromDb();
    checkAdmin().then(() => {
      if (typeof appendAdminNavLink === 'function') appendAdminNavLink();
    });
  }, 200);

  if (location.hash === '#admin') {
    setTimeout(() => goToAdmin(), 600);
  }
})();
