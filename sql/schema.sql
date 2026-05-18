create table if not exists historical_exceptions (
  exception_id text primary key,
  exception_type text not null,
  domain text not null,
  source_system text not null,
  region text not null,
  asset_class text not null,
  severity text not null,
  owner text not null,
  sla_hours integer not null,
  age_days integer not null,
  break_amount real not null
);

create table if not exists triaged_exceptions (
  exception_id text primary key,
  predicted_exception_type text not null,
  severity text not null,
  priority_score real not null,
  owner_recommendation text not null,
  confidence_score real not null,
  sme_review_flag integer not null
);
