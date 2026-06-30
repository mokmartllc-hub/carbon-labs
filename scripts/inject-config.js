const fs = require('fs');
const path = require('path');

const url = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL;
const key = process.env.SUPABASE_ANON_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
const adminPassword = process.env.ADMIN_PASSWORD;
const adminEmail = process.env.ADMIN_EMAIL || 'mokmartllc@gmail.com';

if (!url || !key) {
  console.error('Missing env vars: SUPABASE_URL and SUPABASE_ANON_KEY');
  process.exit(1);
}

const lines = [
  `window.SUPABASE_URL=${JSON.stringify(url)};`,
  `window.SUPABASE_ANON_KEY=${JSON.stringify(key)};`,
];
if (adminPassword) {
  lines.push(`window.ADMIN_PASSWORD=${JSON.stringify(adminPassword)};`);
}
if (adminEmail) {
  lines.push(`window.ADMIN_EMAIL=${JSON.stringify(adminEmail)};`);
}
lines.push('');

const target = path.join(__dirname, '..', 'public', 'config.js');
fs.writeFileSync(target, lines.join('\n'));
console.log('Wrote public/config.js for deployment');
