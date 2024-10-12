-- Simple DBT transformation
select
    message_id,
    date::date as date,
    lower(message) as cleaned_message
from {{ ref('combined_cleaned_data') }} 
where message is not null
