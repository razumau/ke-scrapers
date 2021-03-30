drop table medals;

create table medals
(
	id INT,
	first_name TEXT,
	last_name TEXT,
	gold INTEGER,
	silver INTEGER,
	bronze INTEGER,
	total INTEGER,
	gold_chgk INTEGER,
	silver_chgk INTEGER,
	bronze_chgk INTEGER,
	gold_eq INTEGER,
	silver_eq INTEGER,
	bronze_eq INTEGER,
	gold_br INTEGER,
	silver_br INTEGER,
	bronze_br INTEGER,
	gold_si INTEGER,
	silver_si INTEGER,
	bronze_si INTEGER
);



insert into medals
    with counts as (
        select id,
               first_name,
               last_name,
               (select count(*) from player_places pp2 where chgk_place = 1 and pp.id = pp2.id) as gold_chgk,
               (select count(*) from player_places pp2 where chgk_place = 2 and pp.id = pp2.id) as silver_chgk,
               (select count(*) from player_places pp2 where chgk_place = 3 and pp.id = pp2.id) as bronze_chgk,
               (select count(*) from player_places pp2 where eq_place = 1 and pp.id = pp2.id)   as gold_eq,
               (select count(*) from player_places pp2 where eq_place = 2 and pp.id = pp2.id)   as silver_eq,
               (select count(*) from player_places pp2 where eq_place = 3 and pp.id = pp2.id)   as bronze_eq,
               (select count(*) from player_places pp2 where br_place = '1' and pp.id = pp2.id)   as gold_br,
               (select count(*) from player_places pp2 where br_place = '2' and pp.id = pp2.id)   as silver_br,
               (select count(*) from player_places pp2 where br_place = '3' and pp.id = pp2.id)   as bronze_br,
               (select count(*) from player_places pp2 where si_place = 1 and pp.id = pp2.id)   as gold_si,
               (select count(*) from player_places pp2 where si_place = 2 and pp.id = pp2.id)   as silver_si,
               (select count(*) from player_places pp2 where si_place = 3 and pp.id = pp2.id)   as bronze_si
        from player_places pp
        group by id, first_name, last_name,
                 gold_chgk, silver_chgk, bronze_chgk,
                 gold_eq, silver_eq, bronze_eq,
                 gold_br, silver_br, bronze_br,
                 gold_si, silver_si, bronze_si
    )

    select gold_chgk + gold_eq + gold_br + gold_si as gold,
           silver_chgk + silver_eq + silver_br + silver_si as silver,
           bronze_chgk + bronze_eq + bronze_br + bronze_si as bronze,
           gold_chgk + gold_eq + gold_br + gold_si +
           silver_chgk + silver_eq + silver_br + silver_si +
           bronze_chgk + bronze_eq + bronze_br + bronze_si as total,
           *
    from counts
