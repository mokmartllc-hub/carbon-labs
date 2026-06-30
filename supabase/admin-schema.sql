-- Carbon Labs Admin — run in Supabase SQL Editor after schema.sql

alter table public.profiles
  add column if not exists is_admin boolean not null default false;

create table if not exists public.products (
  id text primary key,
  name text not null,
  cat text not null,
  tag text not null default '',
  badge text,
  exp text,
  "desc" text,
  bullets jsonb not null default '[]'::jsonb,
  storage text,
  sizes jsonb not null default '[]'::jsonb,
  active boolean not null default true,
  sort_order int not null default 0,
  updated_at timestamptz not null default now()
);

create or replace function public.is_admin()
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select coalesce(
    (select is_admin from public.profiles where id = auth.uid()),
    false
  );
$$;

alter table public.products enable row level security;

drop policy if exists "Public read active products" on public.products;
create policy "Public read active products"
  on public.products for select
  using (active = true or public.is_admin());

drop policy if exists "Admins insert products" on public.products;
create policy "Admins insert products"
  on public.products for insert
  with check (public.is_admin());

drop policy if exists "Admins update products" on public.products;
create policy "Admins update products"
  on public.products for update
  using (public.is_admin());

drop policy if exists "Admins delete products" on public.products;
create policy "Admins delete products"
  on public.products for delete
  using (public.is_admin());

drop policy if exists "Admins read all orders" on public.orders;
create policy "Admins read all orders"
  on public.orders for select
  using (public.is_admin());

drop policy if exists "Admins update orders" on public.orders;
create policy "Admins update orders"
  on public.orders for update
  using (public.is_admin());

drop policy if exists "Admins read contact" on public.contact_messages;
create policy "Admins read contact"
  on public.contact_messages for select
  using (public.is_admin());

drop policy if exists "Admins read newsletter" on public.newsletter_subscribers;
create policy "Admins read newsletter"
  on public.newsletter_subscribers for select
  using (public.is_admin());

-- Make yourself admin (replace with your user email):
-- update public.profiles set is_admin = true
-- where id = (select id from auth.users where email = 'your@email.com');
