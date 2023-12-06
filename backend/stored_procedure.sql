DELIMITER //
CREATE PROCEDURE PlayerRank()
BEGIN
	DECLARE varRateeId INT;
	DECLARE varName VARCHAR(50);
	DECLARE varScore DOUBLE;
	DECLARE varRank VARCHAR(2);
	DECLARE done BOOLEAN DEFAULT FALSE;
	DECLARE cur CURSOR FOR (SELECT RateeId, Name, (IFNULL(Rating/Average, 0)*0.8+CommentCount*0.2) AS Score FROM RatingComment NATURAL JOIN DisciplineAverage);
	DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
	DROP TEMPORARY TABLE IF EXISTS RatingComment; 
DROP TEMPORARY TABLE IF EXISTS DisciplineAverage; 
	CREATE TEMPORARY TABLE RatingComment AS
	(SELECT RateeId, Name, CommentCount, (SumofRating/NULLIF(NumofRating, 0)) AS Rating, Discipline FROM Athlete NATURAL JOIN Ratee NATURAL JOIN (SELECT Target AS RateeId, COUNT(*) AS CommentCount FROM Comment GROUP BY Target) AS Temp);
	CREATE TEMPORARY TABLE DisciplineAverage AS
	(SELECT Discipline, AVG(SumofRating/NULLIF(NumofRating, 0)) AS Average FROM Ratee NATURAL JOIN Athlete GROUP BY Discipline);
	DROP TABLE IF EXISTS FinalTable;
	CREATE TABLE FinalTable (RateeId INT PRIMARY KEY, Name VARCHAR(50), PlayerRank VARCHAR(2), Score DOUBLE);
	OPEN cur;
		Cloop: LOOP
		FETCH cur INTO varRateeId, varName, varScore;
	IF done THEN
		LEAVE cloop;
	END IF;

	IF varScore >= 5.1 THEN
		SET varRank = 'A';
	ELSEIF varScore >= 2.8 THEN
		SET varRank = 'B';
	ELSE
		SET varRank = 'C';
	END IF;

	INSERT INTO FinalTable VALUE (varRateeId, varName, varRank, varScore);
	END LOOP cloop;
	CLOSE cur;

	SELECT * FROM FinalTable ORDER BY Score DESC;
END//
DELIMITER ;