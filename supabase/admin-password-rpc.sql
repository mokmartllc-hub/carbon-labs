-- Password-based admin RPCs (no account login required)
-- Default password: CarbonLabs2026! — change in admin_config table

create table if not exists public.admin_config (
  id int primary key default 1 check (id = 1),
  password text not null
);

insert into public.admin_config (id, password)
values (1, 'CarbonLabs2026!')
on conflict (id) do update set password = excluded.password;

alter table public.admin_config enable row level security;

create or replace function public.admin_verify(pass text)
returns boolean
language sql
security definer
stable
set search_path = public
as $$
  select exists (
    select 1 from public.admin_config where id = 1 and admin_config.password = pass
  );
$$;

create or replace function public.admin_get_stats(pass text)
returns json
language plpgsql
security definer
set search_path = public
as $$
begin
  if not public.admin_verify(pass) then
    raise exception 'Access denied';
  end if;
  return (
    select json_build_object(
      'orders_count', (select count(*)::int from public.orders),
      'revenue', (select coalesce(sum(total), 0) from public.orders),
      'products_count', (select count(*)::int from public.products),
      'messages_count', (select count(*)::int from public.contact_messages),
      'subscribers_count', (select count(*)::int from public.newsletter_subscribers),
      'low_stock', coalesce((
        select json_agg(label)
        from (
          select p.id || ' · ' || (s.value->>'l') as label
          from public.products p
          cross join lateral jsonb_array_elements(p.sizes) as s(value)
          where coalesce((s.value->>'stock')::int, 0) <= 5
        ) t
      ), '[]'::json)
    )
  );
end;
$$;

create or replace function public.admin_list_orders(pass text)
returns setof public.orders
language plpgsql
security definer
set search_path = public
as $$
begin
  if not public.admin_verify(pass) then
    raise exception 'Access denied';
  end if;
  return query select * from public.orders order by created_at desc;
end;
$$;

create or replace function public.admin_update_order(pass text, order_id bigint, new_status text)
returns void
language plpgsql
security definer
set search_path = public
as $$
begin
  if not public.admin_verify(pass) then
    raise exception 'Access denied';
  end if;
  update public.orders set status = new_status where id = order_id;
end;
$$;

create or replace function public.admin_list_products(pass text)
returns setof public.products
language plpgsql
security definer
set search_path = public
as $$
begin
  if not public.admin_verify(pass) then
    raise exception 'Access denied';
  end if;
  return query select * from public.products order by sort_order, name;
end;
$$;

create or replace function public.admin_upsert_product(pass text, payload jsonb)
returns void
language plpgsql
security definer
set search_path = public
as $$
begin
  if not public.admin_verify(pass) then
    raise exception 'Access denied';
  end if;
  insert into public.products (
    id, name, cat, tag, badge, exp, "desc", bullets, storage, sizes, active, sort_order, updated_at
  ) values (
    payload->>'id',
    payload->>'name',
    payload->>'cat',
    coalesce(payload->>'tag', ''),
    nullif(payload->>'badge', ''),
    payload->>'exp',
    payload->>'desc',
    coalesce(payload->'bullets', '[]'::jsonb),
    payload->>'storage',
    coalesce(payload->'sizes', '[]'::jsonb),
    coalesce((payload->>'active')::boolean, true),
    coalesce((payload->>'sort_order')::int, 0),
    now()
  )
  on conflict (id) do update set
    name = excluded.name,
    cat = excluded.cat,
    tag = excluded.tag,
    badge = excluded.badge,
    exp = excluded.exp,
    "desc" = excluded."desc",
    bullets = excluded.bullets,
    storage = excluded.storage,
    sizes = excluded.sizes,
    active = excluded.active,
    sort_order = excluded.sort_order,
    updated_at = now();
end;
$$;

create or replace function public.admin_delete_product(pass text, product_id text)
returns void
language plpgsql
security definer
set search_path = public
as $$
begin
  if not public.admin_verify(pass) then
    raise exception 'Access denied';
  end if;
  delete from public.products where id = product_id;
end;
$$;

create or replace function public.admin_list_messages(pass text)
returns setof public.contact_messages
language plpgsql
security definer
set search_path = public
as $$
begin
  if not public.admin_verify(pass) then
    raise exception 'Access denied';
  end if;
  return query
    select * from public.contact_messages
    order by created_at desc
    limit 50;
end;
$$;

create or replace function public.admin_list_subscribers(pass text)
returns setof public.newsletter_subscribers
language plpgsql
security definer
set search_path = public
as $$
begin
  if not public.admin_verify(pass) then
    raise exception 'Access denied';
  end if;
  return query
    select * from public.newsletter_subscribers
    order by created_at desc
    limit 100;
end;
$$;

grant execute on function public.admin_verify(text) to anon, authenticated;
grant execute on function public.admin_get_stats(text) to anon, authenticated;
grant execute on function public.admin_list_orders(text) to anon, authenticated;
grant execute on function public.admin_update_order(text, bigint, text) to anon, authenticated;
grant execute on function public.admin_list_products(text) to anon, authenticated;
grant execute on function public.admin_upsert_product(text, jsonb) to anon, authenticated;
grant execute on function public.admin_delete_product(text, text) to anon, authenticated;
grant execute on function public.admin_list_messages(text) to anon, authenticated;
grant execute on function public.admin_list_subscribers(text) to anon, authenticated;
