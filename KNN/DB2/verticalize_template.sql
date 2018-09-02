CONNECT TO CS240A

DROP TABLE vTRAINST
CREATE TABLE vTRAINST (
	TupleId INTEGER,
	ColNum  INTEGER,
	ColName VARCHAR(50),
	ColVal  VARCHAR(100),
	IsCont  INTEGER DEFAULT '0' NOT NULL,
	Weight  DECIMAL DEFAULT '1.0' NOT NULL
)

DROP TABLE trOUTCOME
CREATE TABLE trOUTCOME (
	TupleId INTEGER,
	ClassLL VARCHAR(50),
	Weight  DECIMAL DEFAULT '1.0' NOT NULL
)

DROP TABLE vTESTST
CREATE TABLE vTESTST LIKE vTRAINST

DROP TABLE teOUTCOME
CREATE TABLE teOUTCOME LIKE trOUTCOME


CREATE OR REPLACE PROCEDURE getTotalColumns(IN TabName VARCHAR(100), OUT TotCols INTEGER)
LANGUAGE SQL
BEGIN
	SET TotCols = (	SELECT count(*)
			FROM   SYSIBM.SYSCOLUMNS
			WHERE  tbname = TabName );
END


CREATE OR REPLACE PROCEDURE getColumnName(IN TabName VARCHAR(100), IN ColNum INTEGER, OUT ColName VARCHAR(100))
LANGUAGE SQL
BEGIN
	SET ColName = (	SELECT name
			FROM   SYSIBM.SYSCOLUMNS
			WHERE  tbname = TabName AND colno = ColNum );
END


CREATE OR REPLACE PROCEDURE verticalize(IN TabName VARCHAR(50), IN otV VARCHAR(50), IN otC VARCHAR(50))
LANGUAGE SQL
BEGIN
	DECLARE TCol INTEGER;
	DECLARE CNo  INTEGER;
	DECLARE CNam VARCHAR(100);
  	DECLARE STMT VARCHAR(200);

	CALL getTotalColumns(TabName, TCol);

	SET CNo = 1;
	WHILE CNo < TCol - 1
	DO
		CALL getColumnName(TabName, CNo, CNam);

		-- Exercise for the students
		-- SET STMT = 'INSERT INTO ....';		
		-- EXECUTE IMMEDIATE STMT;

		SET CNo = CNo + 1;
	END WHILE;

	CALL getColumnName(TabName, TCol-1, CNam);
	
	-- Exercise for the students
	-- SET STMT = '';		
	-- EXECUTE IMMEDIATE STMT;

	-- Handling Missing Class Values
	-- Exercise for the students
	-- SET STMT = '';		
	-- EXECUTE IMMEDIATE STMT;

	
END


CREATE OR REPLACE PROCEDURE performVerticalize()
LANGUAGE SQL
BEGIN
	CALL verticalize('TRAINSET','vTRAINST','trOUTCOME');
	CALL verticalize('TESTSET','vTESTST','teOUTCOME');
END

