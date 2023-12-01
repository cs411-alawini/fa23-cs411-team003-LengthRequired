DELIMITER //
CREATE TRIGGER RatingTrig
	AFTER INSERT ON Rates
		FOR EACH ROW
	BEGIN
		SET @sum = (SELECT SumofRating 
			FROM Ratee
			WHERE RateeId = new.Target);
		SET @num  = (SELECT NumofRating 
			FROM Ratee
			WHERE RateeId = new.Target);
		IF @sum IS NOT NULL THEN
			UPDATE Ratee
			SET SumofRating = (@sum+new.RatingValue), NumofRating = (@num+1)
			WHERE RateeId = new.Target;
		END IF;
	END;//
DELIMITER ;

DELIMITER //
CREATE TRIGGER AthleteTrig 
	BEFORE INSERT ON Athlete 
		FOR EACH ROW 
	BEGIN 
		SET @lastRateeId = (SELECT MAX(RateeId)  FROM Ratee); 
		SET new.RateeId = @lastRateeId+1; 
		INSERT INTO Ratee VALUES (new.RateeId, 'Athlete', 0, 0); 
	END;//
DELIMITER ;

DELIMITER //
CREATE TRIGGER CoachTrig 
	BEFORE INSERT ON Coach 
		FOR EACH ROW 
	BEGIN 
		SET @lastRateeId = (SELECT MAX(RateeId)  FROM Ratee); 
		SET new.RateeId = @lastRateeId+1; 
		INSERT INTO Ratee VALUES (new.RateeId, 'Coach', 0, 0); 
	END;//
DELIMITER ;

DELIMITER //
CREATE TRIGGER TeamTrig 
	BEFORE INSERT ON Team 
		FOR EACH ROW 
	BEGIN 
		SET @lastRateeId = (SELECT MAX(RateeId)  FROM Ratee); 
		SET new.RateeId = @lastRateeId+1; 
		INSERT INTO Ratee VALUES (new.RateeId, 'Team', 0, 0); 
	END;//
DELIMITER ;