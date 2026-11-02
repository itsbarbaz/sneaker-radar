-- Hypewise: contatore di visite semplice e anonimo (nessun cookie, nessun IP salvato).
-- Incolla tutto nel SQL Editor di Supabase e premi Run. Si puo' rilanciare senza problemi.

create table if not exists public.site_visits (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  path text not null check (char_length(path) <= 200),
  ref text check (char_length(ref) <= 100),
  lang text check (char_length(lang) <= 10),
  w int check (w between 0 and 20000),
  sid text check (char_length(sid) <= 40)
);

alter table public.site_visits enable row level security;

drop policy if exists "anyone can add a visit" on public.site_visits;
create policy "anyone can add a visit" on public.site_visits for insert to anon with check (true);
grant insert on public.site_visits to anon;
-- Nessuna policy di lettura: le righe restano private. Si leggono solo i totali con visit_stats().

create or replace function public.visit_stats(days int default 30)
returns json language sql security definer set search_path = public as $$
  select json_build_object(
    'daily', (select coalesce(json_agg(r order by r.d), '[]'::json) from (
        select created_at::date as d, count(*) as views, count(distinct sid) as sessions
        from site_visits where created_at > now() - make_interval(days => days) group by 1) r),
    'pages', (select coalesce(json_agg(r), '[]'::json) from (
        select path, count(*) as views from site_visits
        where created_at > now() - make_interval(days => days) group by 1 order by 2 desc limit 15) r),
    'refs', (select coalesce(json_agg(r), '[]'::json) from (
        select ref, count(*) as sessions from site_visits
        where ref is not null and created_at > now() - make_interval(days => days) group by 1 order by 2 desc limit 10) r),
    'langs', (select coalesce(json_agg(r), '[]'::json) from (
        select coalesce(lang, '?') as lang, count(*) as views from site_visits
        where created_at > now() - make_interval(days => days) group by 1 order by 2 desc limit 6) r),
    'total', json_build_object('views', (select count(*) from site_visits), 'sessions', (select count(distinct sid) from site_visits))
  );
$$;
revoke all on function public.visit_stats(int) from public;
grant execute on function public.visit_stats(int) to anon;
