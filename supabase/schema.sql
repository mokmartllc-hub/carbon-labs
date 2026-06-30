-- Carbon Labs — run this in Supabase Dashboard → SQL Editor

-- Profiles (extends auth.users)
create table if not exists public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  first_name text not null default '',
  last_name text not null default '',
  created_at timestamptz not null default now()
);

-- Carts (one per user)
create table if not exists public.carts (
  user_id uuid primary key references auth.users (id) on delete cascade,
  items jsonb not null default '[]'::jsonb,
  updated_at timestamptz not null default now()
);

-- Orders
create table if not exists public.orders (
  id bigserial primary key,
  user_id uuid not null references auth.users (id) on delete cascade,
  order_number text not null unique,
  status text not null default 'confirmed',
  items jsonb not null,
  subtotal numeric(10, 2) not null,
  savings numeric(10, 2) not null default 0,
  total numeric(10, 2) not null,
  shipping_name text not null,
  shipping_email text not null,
  shipping_phone text,
  shipping_address text not null,
  shipping_city text not null,
  shipping_state text not null,
  shipping_zip text not null,
  notes text,
  created_at timestamptz not null default now()
);

-- Contact form submissions
create table if not exists public.contact_messages (
  id bigserial primary key,
  name text not null,
  email text not null,
  order_number text,
  subject text not null,
  message text not null,
  created_at timestamptz not null default now()
);

-- Newsletter subscribers
create table if not exists public.newsletter_subscribers (
  id bigserial primary key,
  email text not null unique,
  created_at timestamptz not null default now()
);

-- Auto-create profile + cart on signup
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.profiles (id, first_name, last_name)
  values (
    new.id,
    coalesce(new.raw_user_meta_data ->> 'first_name', ''),
    coalesce(new.raw_user_meta_data ->> 'last_name', '')
  );
  insert into public.carts (user_id, items) values (new.id, '[]'::jsonb);
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- Row Level Security
alter table public.profiles enable row level security;
alter table public.carts enable row level security;
alter table public.orders enable row level security;
alter table public.contact_messages enable row level security;
alter table public.newsletter_subscribers enable row level security;

drop policy if exists "Users read own profile" on public.profiles;
create policy "Users read own profile"
  on public.profiles for select using (auth.uid() = id);

drop policy if exists "Users update own profile" on public.profiles;
create policy "Users update own profile"
  on public.profiles for update using (auth.uid() = id);

drop policy if exists "Users insert own profile" on public.profiles;
create policy "Users insert own profile"
  on public.profiles for insert with check (auth.uid() = id);

drop policy if exists "Users manage own cart" on public.carts;
create policy "Users manage own cart"
  on public.carts for all using (auth.uid() = user_id);

drop policy if exists "Users read own orders" on public.orders;
create policy "Users read own orders"
  on public.orders for select using (auth.uid() = user_id);

drop policy if exists "Users create own orders" on public.orders;
create policy "Users create own orders"
  on public.orders for insert with check (auth.uid() = user_id);

drop policy if exists "Anyone can submit contact" on public.contact_messages;
create policy "Anyone can submit contact"
  on public.contact_messages for insert with check (true);

drop policy if exists "Anyone can subscribe newsletter" on public.newsletter_subscribers;
create policy "Anyone can subscribe newsletter"
  on public.newsletter_subscribers for insert with check (true);
