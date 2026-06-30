const fs = require('fs');
const path = require('path');

const url = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL;
const key = process.env.SUPABASE_ANON_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

if (!url || !key) {
  console.error('Missing env vars: SUPABASE_URL and SUPABASE_ANON_KEY');
  process.exit(1);
}

const out = `window.SUPABASE_URL=${JSON.stringify(url)};window.SUPABASE_ANON_KEY=${JSON.stringify(key)};\n`;
const target = path.join(__dirname, '..', 'public', 'config.js');
fs.writeFileSync(target, out);
console.log('Wrote public/config.js for deployment');
