select
  exception_id,
  domain,
  source_system,
  region,
  asset_class,
  missing_field_count,
  age_days,
  break_amount,
  price_movement_pct,
  duplicate_flag,
  currency_mismatch_flag,
  refresh_delay_hours
from historical_exceptions;
