/*
This file is for my own personal testing for the database
*/

select * from artist

select * from venue

select * from genre

select  v.name as venue_name 
    ,   g.name as genre_name
from    venue_genre vg
JOIN    venue v   
    on  vg.venue_id = v.id
join    genre g 
    on  vg.genre_id = g.id
