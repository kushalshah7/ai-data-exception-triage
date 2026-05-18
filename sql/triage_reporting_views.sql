create view if not exists owner_workload as
select owner_recommendation, count(*) as exception_count, avg(priority_score) as avg_priority
from triaged_exceptions
group by owner_recommendation;

create view if not exists high_priority_queue as
select *
from triaged_exceptions
where priority_score >= 70
order by priority_score desc;
