/* Carbon Labs — Supabase integration */
(function () {
  let sb = null;
  let cartSaveTimer = null;

  function requireConfig() {
    if (!window.SUPABASE_URL || !window.SUPABASE_ANON_KEY) {
      throw new Error(
        'Supabase is not configured. Copy public/config.example.js to public/config.js and add your keys.'
      );
    }
  }

  function getSupabase() {
    requireConfig();
    if (!sb) {
      sb = supabase.createClient(window.SUPABASE_URL, window.SUPABASE_ANON_KEY);
    }
    return sb;
  }

  function cap(s) {
    return s ? s.charAt(0).toUpperCase() + s.slice(1).toLowerCase() : '';
  }

  function mapUser(user) {
    const meta = user.user_metadata || {};
    return {
      id: user.id,
      first: cap(meta.first_name || meta.first || ''),
      last: cap(meta.last_name || meta.last || ''),
      email: user.email || '',
    };
  }

  function errMsg(error) {
    return error?.message || 'Request failed';
  }
  window.errMsg = errMsg;

  function mergeCarts(local, remote) {
    const map = new Map();
    (remote || []).forEach((i) => map.set(i.k, { ...i }));
    (local || []).forEach((i) => {
      const ex = map.get(i.k);
      if (ex) ex.qty += i.qty;
      else map.set(i.k, { ...i });
    });
    return Array.from(map.values());
  }

  async function loadCart() {
    if (!currentUser) return [];
    const { data, error } = await getSupabase()
      .from('carts')
      .select('items')
      .eq('user_id', currentUser.id)
      .maybeSingle();
    if (error) throw error;
    return data?.items || [];
  }

  async function saveCart() {
    if (!currentUser) return;
    const { error } = await getSupabase()
      .from('carts')
      .upsert({
        user_id: currentUser.id,
        items: cart,
        updated_at: new Date().toISOString(),
      });
    if (error) throw error;
  }

  function scheduleCartSave() {
    if (!currentUser) return;
    clearTimeout(cartSaveTimer);
    cartSaveTimer = setTimeout(() => {
      saveCart().catch((e) => console.warn('Cart sync failed', e));
    }, 400);
  }

  function wrapCartFns() {
    const origAdd = window.addC;
    const origRm = window.rmC;
    const origSetQty = window.setCartQty;
    window.addC = function (p, sz, qty) {
      const stock = typeof getProductStock === 'function' ? getProductStock(p.id, sz.l) : null;
      if (stock != null && stock <= 0) {
        alert('This item is out of stock.');
        return;
      }
      origAdd(p, sz, qty);
      scheduleCartSave();
    };
    window.rmC = function (k) {
      origRm(k);
      scheduleCartSave();
    };
    if (origSetQty) {
      window.setCartQty = function (k, delta) {
        if (delta > 0) {
          const ex = cart.find((i) => i.k === k);
          if (ex && typeof getProductStock === 'function') {
            const stock = getProductStock(ex.id, ex.size);
            if (stock != null && ex.qty + delta > stock) {
              alert('Not enough stock available.');
              return;
            }
          }
        }
        origSetQty(k, delta);
        scheduleCartSave();
      };
    }
  }

  async function syncCartAfterLogin() {
    const localCart = [...cart];
    const remote = await loadCart();
    cart = mergeCarts(localCart, remote);
    updCC();
    renderCart();
    await saveCart();
  }

  async function restoreSession() {
    try {
      requireConfig();
      const client = getSupabase();
      const {
        data: { session },
      } = await client.auth.getSession();
      if (!session) return;
      currentUser = mapUser(session.user);
      updateNavAuth();
      if (typeof refreshAdminAccess === 'function') refreshAdminAccess();
      const items = await loadCart();
      if (items.length) {
        cart = mergeCarts(cart, items);
        updCC();
        renderCart();
      }
    } catch (e) {
      console.warn('Session restore failed', e);
      currentUser = null;
    }
  }

  window.doLogin = async function () {
    const email = document.getElementById('login-email')?.value.trim();
    const pass = document.getElementById('login-pass')?.value;
    const err = document.getElementById('login-err');
    if (!email?.includes('@') || !pass) {
      err.textContent = 'Please enter a valid email and password.';
      err.classList.add('show');
      return;
    }
    err.classList.remove('show');
    const btn = document.querySelector('#panel-login .auth-btn');
    const prev = btn?.textContent;
    if (btn) {
      btn.textContent = 'Logging in…';
      btn.disabled = true;
    }
    try {
      const { data, error } = await getSupabase().auth.signInWithPassword({ email, password: pass });
      if (error) throw error;
      currentUser = mapUser(data.user);
      await syncCartAfterLogin();
      updateNavAuth();
      document.getElementById('auth-success-title').textContent = 'Logged In!';
      document.getElementById('auth-success-msg').textContent =
        'Welcome back, ' + currentUser.first + '. Your cart is ready.';
      switchAuthTab('success');
    } catch (e) {
      err.textContent = errMsg(e);
      err.classList.add('show');
    } finally {
      if (btn) {
        btn.textContent = prev;
        btn.disabled = false;
      }
    }
  };

  window.doSignup = async function () {
    const first = document.getElementById('su-first')?.value.trim();
    const last = document.getElementById('su-last')?.value.trim();
    const email = document.getElementById('su-email')?.value.trim();
    const pass = document.getElementById('su-pass')?.value;
    const pass2 = document.getElementById('su-pass2')?.value;
    const agree = document.getElementById('su-agree')?.checked;
    const err = document.getElementById('signup-err');
    if (!first || !last || !email || !pass) {
      err.textContent = 'Please fill in all fields.';
      err.classList.add('show');
      return;
    }
    if (!email.includes('@')) {
      err.textContent = 'Please enter a valid email.';
      err.classList.add('show');
      return;
    }
    if (pass.length < 8) {
      err.textContent = 'Password must be at least 8 characters.';
      err.classList.add('show');
      return;
    }
    if (pass !== pass2) {
      err.textContent = 'Passwords do not match.';
      err.classList.add('show');
      return;
    }
    if (!agree) {
      err.textContent = 'Please confirm the research use agreement.';
      err.classList.add('show');
      return;
    }
    err.classList.remove('show');
    const btn = document.querySelector('#panel-signup .auth-btn');
    const prev = btn?.textContent;
    if (btn) {
      btn.textContent = 'Creating account…';
      btn.disabled = true;
    }
    try {
      const { data, error } = await getSupabase().auth.signUp({
        email,
        password: pass,
        options: { data: { first_name: first, last_name: last } },
      });
      if (error) throw error;
      if (!data.session) {
        document.getElementById('auth-success-title').textContent = 'Check Your Email';
        document.getElementById('auth-success-msg').textContent =
          'We sent a confirmation link to ' + email + '. Click it, then log in.';
        switchAuthTab('success');
        return;
      }
      currentUser = mapUser(data.user);
      await saveCart();
      updateNavAuth();
      document.getElementById('auth-success-title').textContent = 'Account Created!';
      document.getElementById('auth-success-msg').textContent =
        'Welcome to Carbon Labs, ' + currentUser.first + '. Your cart has been saved.';
      switchAuthTab('success');
    } catch (e) {
      err.textContent = errMsg(e);
      err.classList.add('show');
    } finally {
      if (btn) {
        btn.textContent = prev;
        btn.disabled = false;
      }
    }
  };

  window.doReset = async function () {
    const email = document.getElementById('reset-email')?.value.trim();
    if (!email || !email.includes('@')) return;
    try {
      const { error } = await getSupabase().auth.resetPasswordForEmail(email, {
        redirectTo: window.location.origin + '/?type=recovery',
      });
      if (error) throw error;
      document.getElementById('auth-success-title').textContent = 'Check Your Email';
      document.getElementById('auth-success-msg').textContent =
        'If an account exists for ' + email + ', a reset link has been sent.';
      switchAuthTab('success');
    } catch (e) {
      alert(errMsg(e));
    }
  };

  window.doSignOut = async function () {
    await getSupabase().auth.signOut();
    currentUser = null;
    updateNavAuth();
    go('home');
  };

  window.submitForm = async function (btn) {
    const card = btn.closest('.contact-form-card');
    const name = card?.querySelector('#cf-name')?.value.trim();
    const email = card?.querySelector('#cf-email')?.value.trim();
    const orderNum = card?.querySelector('#cf-order')?.value.trim();
    const subject = card?.querySelector('#cf-subject')?.value.trim();
    const message = card?.querySelector('#cf-message')?.value.trim();
    if (!name || !email || !subject || !message) {
      alert('Please fill in all required fields.');
      return;
    }
    btn.textContent = 'Sending…';
    btn.disabled = true;
    try {
      const { error } = await getSupabase().from('contact_messages').insert({
        name,
        email,
        order_number: orderNum || null,
        subject,
        message,
      });
      if (error) throw error;
      card.innerHTML =
        '<div style="text-align:center;padding:40px 0"><div style="font-size:48px;margin-bottom:16px">✅</div><h3 style="font-size:18px;font-weight:800;color:white;margin-bottom:10px">Message Sent!</h3><p style="font-size:14px;color:rgba(255,255,255,.42);line-height:1.7">We\'ll get back to you within 2 hours.<br>Check your email for a confirmation.</p></div>';
    } catch (e) {
      alert(errMsg(e));
      btn.textContent = 'Send Message';
      btn.disabled = false;
    }
  };

  window.subscribeNewsletter = async function () {
    const input = document.getElementById('nl-email');
    const btn = document.getElementById('nl-btn');
    const email = input?.value.trim();
    if (!email || !email.includes('@')) {
      alert('Please enter a valid email.');
      return;
    }
    if (btn) {
      btn.textContent = '…';
      btn.disabled = true;
    }
    try {
      const { error } = await getSupabase().from('newsletter_subscribers').insert({ email });
      if (error && error.code !== '23505') throw error;
      input.value = '';
      input.placeholder = 'Subscribed! ✓';
      if (btn) btn.textContent = 'Subscribed';
    } catch (e) {
      alert(errMsg(e));
      if (btn) {
        btn.textContent = 'Subscribe';
        btn.disabled = false;
      }
    }
  };

  function ensureCheckoutModal() {
    if (document.getElementById('checkout-modal')) return;
    const el = document.createElement('div');
    el.id = 'checkout-modal';
    el.className = 'checkout-modal';
    el.innerHTML = `
      <div class="checkout-backdrop" onclick="closeCheckout()"></div>
      <div class="checkout-panel">
        <button class="checkout-close" onclick="closeCheckout()">×</button>
        <h2>Checkout</h2>
        <p class="checkout-sub">Free shipping · Ships in 24–48 business hours</p>
        <div class="auth-err" id="checkout-err"></div>
        <div class="auth-field"><label>Full Name</label><input class="auth-input" id="co-name" type="text"></div>
        <div class="auth-field"><label>Email</label><input class="auth-input" id="co-email" type="email"></div>
        <div class="auth-field"><label>Phone (optional)</label><input class="auth-input" id="co-phone" type="tel"></div>
        <div class="auth-field"><label>Street Address</label><input class="auth-input" id="co-address" type="text"></div>
        <div style="display:flex;gap:10px">
          <div class="auth-field" style="flex:2"><label>City</label><input class="auth-input" id="co-city" type="text"></div>
          <div class="auth-field" style="flex:1"><label>State</label><input class="auth-input" id="co-state" type="text"></div>
          <div class="auth-field" style="flex:1"><label>ZIP</label><input class="auth-input" id="co-zip" type="text"></div>
        </div>
        <div class="auth-field"><label>Order Notes (optional)</label><input class="auth-input" id="co-notes" type="text"></div>
        <div class="checkout-total">Total: <span id="co-total">$0.00</span></div>
        <button class="auth-btn" id="co-submit" onclick="placeOrder()">Place Order →</button>
      </div>`;
    document.body.appendChild(el);
    const style = document.createElement('style');
    style.textContent = `
      .checkout-modal{display:none;position:fixed;inset:0;z-index:400;align-items:center;justify-content:center;padding:20px}
      .checkout-modal.open{display:flex}
      .checkout-backdrop{position:absolute;inset:0;background:rgba(0,0,0,.65);backdrop-filter:blur(4px)}
      .checkout-panel{position:relative;background:#141414;border:1px solid rgba(255,255,255,.12);border-radius:20px;padding:32px;width:100%;max-width:480px;max-height:90vh;overflow-y:auto;z-index:1}
      .checkout-panel h2{font-size:22px;font-weight:900;color:white;margin-bottom:6px}
      .checkout-sub{font-size:13px;color:rgba(255,255,255,.4);margin-bottom:20px}
      .checkout-close{position:absolute;top:14px;right:16px;background:none;border:none;color:rgba(255,255,255,.4);font-size:24px;cursor:pointer}
      .checkout-total{font-size:16px;font-weight:800;color:white;margin:16px 0;text-align:right}
      .checkout-total span{color:var(--a2)}
    `;
    document.head.appendChild(style);
  }

  window.closeCheckout = function () {
    document.getElementById('checkout-modal')?.classList.remove('open');
  };

  window.openCheckout = function () {
    ensureCheckoutModal();
    const deal = calcDeal(cart);
    const sub = cart.reduce((s, i) => s + i.price * i.qty, 0);
    const total = sub - deal.savings;
    document.getElementById('co-total').textContent = '$' + total.toFixed(2);
    if (currentUser) {
      document.getElementById('co-name').value =
        (currentUser.first + ' ' + (currentUser.last || '')).trim();
      document.getElementById('co-email').value = currentUser.email || '';
    }
    document.getElementById('checkout-err')?.classList.remove('show');
    document.getElementById('checkout-modal').classList.add('open');
  };

  function orderNumber() {
    return 'CL-' + String(Math.floor(10000 + Math.random() * 90000));
  }

  window.placeOrder = async function () {
    const err = document.getElementById('checkout-err');
    const subtotal = cart.reduce((s, i) => s + i.price * i.qty, 0);
    const savings = calcDeal(cart).savings;
    const total = subtotal - savings;
    const payload = {
      user_id: currentUser.id,
      order_number: orderNumber(),
      status: 'confirmed',
      items: cart,
      subtotal,
      savings,
      total,
      shipping_name: document.getElementById('co-name')?.value.trim(),
      shipping_email: document.getElementById('co-email')?.value.trim(),
      shipping_phone: document.getElementById('co-phone')?.value.trim() || null,
      shipping_address: document.getElementById('co-address')?.value.trim(),
      shipping_city: document.getElementById('co-city')?.value.trim(),
      shipping_state: document.getElementById('co-state')?.value.trim(),
      shipping_zip: document.getElementById('co-zip')?.value.trim(),
      notes: document.getElementById('co-notes')?.value.trim() || null,
    };
    if (!payload.shipping_name || !payload.shipping_email || !payload.shipping_address) {
      err.textContent = 'Please fill in shipping name, email, and address.';
      err.classList.add('show');
      return;
    }
    if (typeof getProductStock === 'function') {
      for (const item of cart) {
        const stock = getProductStock(item.id, item.size);
        if (stock != null && item.qty > stock) {
          err.textContent = `${item.name} (${item.size}) only has ${stock} in stock.`;
          err.classList.add('show');
          return;
        }
      }
    }
    const btn = document.getElementById('co-submit');
    btn.textContent = 'Placing order…';
    btn.disabled = true;
    try {
      const { error } = await getSupabase().from('orders').insert(payload);
      if (error) throw error;
      cart = [];
      await saveCart();
      updCC();
      renderCart();
      closeCart();
      closeCheckout();
      go('orders');
    } catch (e) {
      err.textContent = errMsg(e);
      err.classList.add('show');
      btn.textContent = 'Place Order →';
      btn.disabled = false;
    }
  };

  window.startCheckout = function () {
    if (!currentUser) {
      authReturnAction = 'checkout';
      closeCart();
      go('auth');
      setTimeout(() => switchAuthTab('signup'), 50);
      return;
    }
    if (!cart.length) {
      alert('Your cart is empty.');
      return;
    }
    closeCart();
    openCheckout();
  };

  window.postAuthAction = function () {
    if (authReturnAction === 'checkout') {
      authReturnAction = null;
      openCheckout();
    } else if (authReturnAction === 'account' || authReturnAction === 'orders') {
      const dest = authReturnAction;
      authReturnAction = null;
      go(dest);
    } else if (authReturnAction === 'admin') {
      authReturnAction = null;
      go('admin');
    } else go('home');
  };

  function fmtDate(iso) {
    return new Date(iso).toLocaleString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    });
  }

  function fmtMoney(n) {
    return '$' + Number(n).toFixed(2);
  }

  function esc(s) {
    return String(s ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  async function fetchProfile() {
    const { data, error } = await getSupabase()
      .from('profiles')
      .select('first_name, last_name, created_at')
      .eq('id', currentUser.id)
      .maybeSingle();
    if (error) throw error;
    return data;
  }

  async function saveProfile(first, last) {
    const { error } = await getSupabase().from('profiles').upsert({
      id: currentUser.id,
      first_name: first,
      last_name: last,
    });
    if (error) throw error;
    const { error: authErr } = await getSupabase().auth.updateUser({
      data: { first_name: first, last_name: last },
    });
    if (authErr) throw authErr;
    currentUser = { ...currentUser, first: cap(first), last: cap(last) };
    updateNavAuth();
  }

  async function fetchOrders() {
    const { data, error } = await getSupabase()
      .from('orders')
      .select('*')
      .eq('user_id', currentUser.id)
      .order('created_at', { ascending: false });
    if (error) throw error;
    return data || [];
  }

  window.renderAccountPage = async function () {
    const root = document.getElementById('account-root');
    if (!root) return;
    root.innerHTML = '<div class="orders-loading">Loading account…</div>';
    try {
      const profile = await fetchProfile();
      const memberSince = profile?.created_at
        ? new Date(profile.created_at).toLocaleDateString(undefined, {
            month: 'long',
            year: 'numeric',
          })
        : '—';
      const first = profile?.first_name || currentUser.first || '';
      const last = profile?.last_name || currentUser.last || '';
      root.innerHTML = `
        <div class="acct-layout">
          <aside class="acct-nav">
            <a class="active">Profile</a>
            <a onclick="go('orders')">Order History</a>
            <a onclick="go('shop')">Continue Shopping</a>
          </aside>
          <div>
            <div class="acct-card" style="margin-bottom:20px">
              <h2>Profile Information</h2>
              <p class="acct-sub">Update your name and contact details. Member since ${esc(memberSince)}.</p>
              <div class="auth-err" id="acct-err"></div>
              <div class="acct-row">
                <div class="auth-field"><label>First Name</label><input class="auth-input" id="acct-first" type="text" value="${esc(first)}"></div>
                <div class="auth-field"><label>Last Name</label><input class="auth-input" id="acct-last" type="text" value="${esc(last)}"></div>
              </div>
              <div class="auth-field"><label>Email</label><input class="auth-input" id="acct-email" type="email" value="${esc(currentUser.email)}" disabled></div>
              <p class="acct-email-note">Email is managed through your login credentials and cannot be changed here.</p>
              <button class="auth-btn" id="acct-save" onclick="saveAccountProfile()">Save Changes →</button>
              <div class="acct-saved" id="acct-saved">Profile updated successfully.</div>
            </div>
            <div class="acct-card">
              <h2>Change Password</h2>
              <p class="acct-sub">Choose a strong password with at least 8 characters.</p>
              <div class="auth-err" id="acct-pass-err"></div>
              <div class="auth-field"><label>New Password</label><input class="auth-input" id="acct-new-pass" type="password" placeholder="At least 8 characters"></div>
              <div class="auth-field"><label>Confirm New Password</label><input class="auth-input" id="acct-new-pass2" type="password" placeholder="Repeat password"></div>
              <button class="auth-btn" onclick="saveAccountPassword()">Update Password →</button>
            </div>
          </div>
        </div>`;
    } catch (e) {
      root.innerHTML = `<div class="orders-empty"><h3>Could not load account</h3><p>${esc(errMsg(e))}</p></div>`;
    }
  };

  window.saveAccountProfile = async function () {
    const first = document.getElementById('acct-first')?.value.trim();
    const last = document.getElementById('acct-last')?.value.trim();
    const err = document.getElementById('acct-err');
    const saved = document.getElementById('acct-saved');
    const btn = document.getElementById('acct-save');
    if (!first || !last) {
      err.textContent = 'Please enter your first and last name.';
      err.classList.add('show');
      return;
    }
    err.classList.remove('show');
    saved?.classList.remove('show');
    const prev = btn?.textContent;
    if (btn) {
      btn.textContent = 'Saving…';
      btn.disabled = true;
    }
    try {
      await saveProfile(first, last);
      saved?.classList.add('show');
    } catch (e) {
      err.textContent = errMsg(e);
      err.classList.add('show');
    } finally {
      if (btn) {
        btn.textContent = prev;
        btn.disabled = false;
      }
    }
  };

  window.saveAccountPassword = async function () {
    const p1 = document.getElementById('acct-new-pass')?.value;
    const p2 = document.getElementById('acct-new-pass2')?.value;
    const err = document.getElementById('acct-pass-err');
    if (!p1 || p1.length < 8) {
      err.textContent = 'Password must be at least 8 characters.';
      err.classList.add('show');
      return;
    }
    if (p1 !== p2) {
      err.textContent = 'Passwords do not match.';
      err.classList.add('show');
      return;
    }
    err.classList.remove('show');
    try {
      const { error } = await getSupabase().auth.updateUser({ password: p1 });
      if (error) throw error;
      document.getElementById('acct-new-pass').value = '';
      document.getElementById('acct-new-pass2').value = '';
      err.textContent = 'Password updated successfully.';
      err.style.background = 'rgba(80,180,120,.12)';
      err.style.borderColor = 'rgba(80,180,120,.3)';
      err.style.color = '#80d8a0';
      err.classList.add('show');
    } catch (e) {
      err.style.background = '';
      err.style.borderColor = '';
      err.style.color = '';
      err.textContent = errMsg(e);
      err.classList.add('show');
    }
  };

  function renderOrderItems(items) {
    return (items || [])
      .map(
        (i) =>
          `<div class="order-item"><span>${esc(i.name)} · ${esc(i.size)} × ${i.qty}</span><span>${fmtMoney(i.price * i.qty)}</span></div>`
      )
      .join('');
  }

  window.toggleOrderDetail = function (el) {
    el.closest('.order-card')?.classList.toggle('open');
  };

  window.renderOrdersPage = async function () {
    const root = document.getElementById('orders-root');
    if (!root) return;
    root.innerHTML = '<div class="orders-loading">Loading orders…</div>';
    try {
      const orders = await fetchOrders();
      if (!orders.length) {
        root.innerHTML = `
          <div class="orders-empty">
            <h3>No orders yet</h3>
            <p>When you place an order, it will appear here with full details and status.</p>
            <button class="auth-btn" style="max-width:220px;margin:24px auto 0" onclick="go('shop')">Browse Products →</button>
          </div>`;
        return;
      }
      root.innerHTML = `
        <div class="acct-layout">
          <aside class="acct-nav">
            <a onclick="go('account')">My Account</a>
            <a class="active">Order History</a>
            <a onclick="go('shop')">Continue Shopping</a>
          </aside>
          <div>
            <div class="acct-card" style="padding:22px 24px 24px;margin-bottom:16px">
              <h2>${orders.length} Order${orders.length === 1 ? '' : 's'}</h2>
              <p class="acct-sub" style="margin-bottom:0">Click an order to view items and shipping details.</p>
            </div>
            <div class="orders-list">
              ${orders
                .map(
                  (o) => `
                <div class="order-card">
                  <div class="order-hd" onclick="toggleOrderDetail(this)">
                    <div>
                      <div class="order-num">${esc(o.order_number)}</div>
                      <div class="order-meta">${fmtDate(o.created_at)} · ${(o.items || []).reduce((s, i) => s + (i.qty || 0), 0)} item(s)</div>
                    </div>
                    <div class="order-hd-right">
                      <div class="order-total">${fmtMoney(o.total)}</div>
                      <div class="order-status ${esc(o.status)}">${esc(o.status)}</div>
                    </div>
                  </div>
                  <div class="order-bd">
                    <div class="order-items">${renderOrderItems(o.items)}</div>
                    <div style="display:flex;justify-content:space-between;font-size:13px;color:rgba(255,255,255,.55);padding-top:8px">
                      <span>Subtotal</span><span>${fmtMoney(o.subtotal)}</span>
                    </div>
                    ${
                      Number(o.savings) > 0
                        ? `<div style="display:flex;justify-content:space-between;font-size:13px;color:var(--a2);padding-top:4px"><span>Deal savings</span><span>-${fmtMoney(o.savings)}</span></div>`
                        : ''
                    }
                    <div style="display:flex;justify-content:space-between;font-size:14px;font-weight:800;color:white;padding-top:8px;margin-top:8px;border-top:1px solid rgba(255,255,255,.07)">
                      <span>Total</span><span>${fmtMoney(o.total)}</span>
                    </div>
                    <div class="order-ship">
                      <strong style="color:rgba(255,255,255,.65)">Ship to:</strong><br>
                      ${esc(o.shipping_name)}<br>
                      ${esc(o.shipping_address)}<br>
                      ${esc(o.shipping_city)}, ${esc(o.shipping_state)} ${esc(o.shipping_zip)}<br>
                      ${esc(o.shipping_email)}${o.shipping_phone ? '<br>' + esc(o.shipping_phone) : ''}
                      ${o.notes ? '<br><br><strong style="color:rgba(255,255,255,.65)">Notes:</strong> ' + esc(o.notes) : ''}
                    </div>
                  </div>
                </div>`
                )
                .join('')}
            </div>
          </div>
        </div>`;
    } catch (e) {
      root.innerHTML = `<div class="orders-empty"><h3>Could not load orders</h3><p>${esc(errMsg(e))}</p></div>`;
    }
  };

  window.goToAccount = function () {
    if (!currentUser) {
      authReturnAction = 'account';
      go('auth');
      return;
    }
    go('account');
  };

  window.goToOrders = function () {
    if (!currentUser) {
      authReturnAction = 'orders';
      go('auth');
      return;
    }
    go('orders');
  };

  window.showOrderHistory = function () {
    goToOrders();
  };

  function showPasswordResetPanel() {
    go('auth');
    const panel = document.getElementById('panel-reset');
    if (!panel) return;
    panel.innerHTML = `
      <div class="auth-title">Set New Password</div>
      <div class="auth-sub">Enter your new password below.</div>
      <div class="auth-err" id="reset-err"></div>
      <div class="auth-field"><label>New Password</label><input class="auth-input" id="new-pass" type="password"></div>
      <div class="auth-field"><label>Confirm Password</label><input class="auth-input" id="new-pass2" type="password"></div>
      <button class="auth-btn" onclick="submitPasswordReset()">Update Password →</button>`;
    switchAuthTab('reset');
    history.replaceState({}, '', window.location.pathname);
  }

  window.submitPasswordReset = async function () {
    const p1 = document.getElementById('new-pass')?.value;
    const p2 = document.getElementById('new-pass2')?.value;
    const err = document.getElementById('reset-err');
    if (!p1 || p1.length < 8) {
      err.textContent = 'Password must be at least 8 characters.';
      err.classList.add('show');
      return;
    }
    if (p1 !== p2) {
      err.textContent = 'Passwords do not match.';
      err.classList.add('show');
      return;
    }
    try {
      const { error } = await getSupabase().auth.updateUser({ password: p1 });
      if (error) throw error;
      document.getElementById('auth-success-title').textContent = 'Password Updated';
      document.getElementById('auth-success-msg').textContent = 'You can now log in with your new password.';
      switchAuthTab('success');
    } catch (e) {
      err.textContent = errMsg(e);
      err.classList.add('show');
    }
  };

  const origUpdateNav = window.updateNavAuth;
  window.updateNavAuth = function () {
    origUpdateNav();
    const dd = document.getElementById('user-dropdown');
    if (dd && currentUser) {
      const links = dd.querySelectorAll('a');
      if (links[0]) links[0].setAttribute('onclick', "go('account')");
      if (links[1]) links[1].setAttribute('onclick', "go('orders')");
    }
    if (typeof refreshAdminAccess === 'function') {
      refreshAdminAccess().then(() => {
        if (typeof appendAdminNavLink === 'function') appendAdminNavLink();
      });
    }
  };

  const origGo = window.go;
  window.go = function (pg) {
    if (pg === 'admin') {
      if (!currentUser) {
        authReturnAction = 'admin';
        origGo('auth');
        return;
      }
      if (typeof refreshAdminAccess === 'function') {
        refreshAdminAccess().then((ok) => {
          if (!ok) {
            const email = window._adminCheckEmail || currentUser?.email || 'your account';
            alert('You do not have admin access for ' + email + '. Sign in with mokmartllc@gmail.com or ask to be granted admin.');
            return;
          }
          origGo('admin');
          if (typeof renderAdminPage === 'function') renderAdminPage();
        });
      }
      return;
    }
    if ((pg === 'account' || pg === 'orders') && !currentUser) {
      authReturnAction = pg;
      origGo('auth');
      return;
    }
    origGo(pg);
    document.getElementById('user-dropdown')?.classList.remove('open');
    if (pg === 'account') renderAccountPage();
    if (pg === 'orders') renderOrdersPage();
  };

  wrapCartFns();
  restoreSession();
  if (typeof loadCatalogFromDb === 'function') {
    loadCatalogFromDb();
  }

  try {
    const client = getSupabase();
    client.auth.onAuthStateChange((event) => {
      if (event === 'PASSWORD_RECOVERY') showPasswordResetPanel();
    });
    if (new URLSearchParams(location.search).get('type') === 'recovery') {
      client.auth.getSession().then(({ data: { session } }) => {
        if (session) showPasswordResetPanel();
      });
    }
  } catch (_) {
    /* config.js not set up yet */
  }
})();
