USE `uefa`;

-- Job 7: UEFA EURO 2012
SELECT g.matchid, g.player
FROM goal g
WHERE g.teamid='GER';

SELECT id, stadium, team1, team2
FROM game
WHERE id=1012;

SELECT goal.player, goal.teamid, game.stadium, game.mdate
FROM goal
JOIN game ON game.id = goal.matchid
WHERE goal.teamid='GER';

SELECT game.team1, game.team2, goal.player
FROM goal
JOIN game ON game.id = goal.matchid
WHERE goal.player LIKE 'Mario %';

SELECT goal.player, goal.teamid, eteam.teamname, eteam.coach, goal.gtime
FROM goal
JOIN eteam ON eteam.id = goal.teamid;

SELECT goal.player, goal.teamid, eteam.coach, goal.gtime
FROM goal
JOIN eteam ON eteam.id = goal.teamid
WHERE goal.gtime <= 10;

SELECT game.mdate, eteam.teamname
FROM game
JOIN eteam ON eteam.id = game.team1
WHERE eteam.coach = 'Fernando Santos'
ORDER BY game.mdate;

SELECT game.id AS match_id, goal.player, goal.gtime
FROM game
JOIN goal ON goal.matchid = game.id
WHERE game.stadium = 'National Stadium, Warsaw'
ORDER BY game.id, goal.gtime;

SELECT teamid, COUNT(*) AS total_goals
FROM goal
GROUP BY teamid
ORDER BY total_goals DESC;

SELECT game.stadium, COUNT(*) AS goals
FROM game
JOIN goal ON goal.matchid = game.id
GROUP BY game.stadium
ORDER BY goals DESC;

SELECT game.id, game.mdate, COUNT(*) AS fra_goals
FROM game
JOIN goal ON goal.matchid = game.id
WHERE goal.teamid = 'FRA'
GROUP BY game.id, game.mdate
ORDER BY game.mdate;
