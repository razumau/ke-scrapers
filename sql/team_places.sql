with br_teams as (
    select br.team_one_id as team_id, br.stage_id, s.tournament_id,
           (team_one_points - team_two_points) * 100 +
           coalesce(team_one_shootout - team_two_shootout, 0) as result
    from br_game br
    left join stage s on br.stage_id = s.id

    union all

    select br.team_two_id as team_id, br.stage_id, s.tournament_id,
           (team_two_points - team_one_points) * 100 +
           coalesce(team_two_shootout - team_one_shootout, 0) as result
    from br_game br
    left join stage s on br.stage_id = s.id
),

br_results as (
    select team_id, tournament_id, max(stage_id) as max_stage
    from br_teams
    group by team_id, tournament_id
),

br_third as (
    select br.team_id, br.tournament_id,
           case when br.result > 0 then '3'
            else '4' end as place
    from br_teams br
    join stage s on br.stage_id = s.id
    where s.name = 'Бой за третье место'
),

br_finals as (
    select br.team_id, br.tournament_id, count(*) as wins
    from br_teams br
    join stage s on br.stage_id = s.id
    where s.name = 'Финал'
        and br.result > 0
    group by br.team_id, br.tournament_id
    order by s.tournament_id desc
),

br_winners as (
    select * from br_finals
    where wins = 2
),

br_places as (
    select br.team_id as team_tournament_id,
            case
                when s.name = 'Бой за третье место' then bt.place
                when s.name = 'Финал' and bw.team_id is not null then '1'
                when s.name = 'Финал' and bw.team_id is null then '2'
            else s.name
            end as place
    from br_results br
    join stage s on br.max_stage = s.id
    left join br_third bt using (tournament_id, team_id)
    left join br_winners bw using (tournament_id, team_id)
    join team_tournament tt on br.team_id = tt.id
        and br.tournament_id = tt.tournament_id
),

chgk_places as (
    select cr.team_tournament_id,
           row_number() over (partition by tt.tournament_id
               order by 100 * sum + coalesce(shootout, 0) desc) as place
    from chgk_results cr
    left join team_tournament tt on cr.team_tournament_id = tt.id
),

eq_finals as (
    select egtr.team_tournament_id, egtr.place
    from eq_game eg
    left join stage s on eg.stage_id = s.id
    left join eq_game_team_result egtr on eg.id = egtr.game_id
    where s.name = 'Финал'
),

eq_stages as (
    select egtr.team_tournament_id, max(eg.stage_id) as max_stage
    from eq_game eg
    join eq_game_team_result egtr on eg.id = egtr.game_id
    group by egtr.team_tournament_id
),

eq_places as (
    select es.team_tournament_id,
           coalesce(ef.place, s.name) as place
    from eq_stages es
    left join eq_finals ef using (team_tournament_id)
    join stage s on es.max_stage = s.id
),

team_places as (
    select tt.id as team_tournament_id,
           t.id,
           coalesce(cp.place, '—') as chgk_place,
           coalesce(br.place, '—') as br_place,
           coalesce(eq.place, '—') as eq_place
    from team_tournament tt
    left join chgk_places cp on tt.id = cp.team_tournament_id
    left join br_places br on tt.id = br.team_tournament_id
    left join eq_places eq on tt.id = eq.team_tournament_id
    left join team t on tt.team_id = t.id
)

select * from team_places;
