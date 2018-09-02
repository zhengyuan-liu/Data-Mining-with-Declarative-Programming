CONNECT TO SAMPLE

DROP TABLE VTRAIN
CREATE TABLE VTRAIN (
	PID INTEGER, 
	ColID INTEGER,
	ColValue DOUBLE
)

DROP TABLE TRAIN_LABEL
CREATE TABLE TRAIN_LABEL (
	PID INTEGER, 
	PLabel INTEGER
)

DROP TABLE VTEST
CREATE TABLE VTEST LIKE TRAIN

DROP TABLE TEST_LABEL
CREATE TABLE TEST_LABEL LIKE TRAIN_LABEL


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

	SET CNo = 1;  -- CNo = 0 is PID column
	WHILE CNo < TCol - 1
	DO
		CALL getColumnName(TabName, CNo, CNam);
		SET STMT = 'INSERT INTO ' || otV || ' (SELECT PID, ' || CNo || ', ' || CNam || ' FROM ' || TabName || ')';
		EXECUTE IMMEDIATE STMT;

		SET CNo = CNo + 1;
	END WHILE;

	CALL getColumnName(TabName, TCol-1, CNam);
	
	-- CNo = TCol-1 is class colunm
	SET STMT = 'INSERT INTO ' || otC || ' (SELECT PID, ' || CNam || ' FROM ' || TabName || ')';	
	EXECUTE IMMEDIATE STMT;
END


CREATE OR REPLACE PROCEDURE performVerticalize()
LANGUAGE SQL
BEGIN
	CALL verticalize('TRAINSET','VTRAIN','TRAIN_LABEL');
	CALL verticalize('TESTSET','VTEST','TEST_LABEL');
END