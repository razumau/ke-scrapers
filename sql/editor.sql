create table if not exists editor (
    id integer primary key autoincrement,
    name text not null,
    player_id integer
);

insert into editor
select distinct null, name, player_id from editor_details;
