PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE ColorTable (
    SrNo INT PRIMARY KEY,
    BaseColor VARCHAR(255) NOT NULL,
    Stock INT NOT NULL CHECK (Stock >= 0),
    Date DATE NOT NULL
);
INSERT INTO ColorTable VALUES(1,'Blue',NULL,'27 Sep 2024');
INSERT INTO ColorTable VALUES(2,'Green',NULL,'27 Sep 2024');
INSERT INTO ColorTable VALUES(3,'Red',NULL,'27 Sep 2024');
INSERT INTO ColorTable VALUES(4,'Yellow',NULL,'27 Sep 2024');
INSERT INTO ColorTable VALUES(5,'Pink',NULL,'27 Sep 2024');
INSERT INTO ColorTable VALUES(6,'Black',NULL,'27 Sep 2024');
INSERT INTO ColorTable VALUES(7,'White',NULL,'27 Sep 2024');
INSERT INTO ColorTable VALUES(8,'Clear',NULL,'27 Sep 2024');
INSERT INTO ColorTable VALUES(9,'Orange',NULL,'27 Sep 2024');
INSERT INTO ColorTable VALUES(10,'Mixer 1',NULL,'27 Sep 2024');
INSERT INTO ColorTable VALUES(11,'Mixer 2',NULL,'27 Sep 2024');
CREATE TABLE BOMHeading (
    SrNo INT PRIMARY KEY AUTO_INCREMENT,
    FinalColor TEXT NOT NULL,
    Date DATE NOT NULL
);
INSERT INTO BOMHeading VALUES(1,'Blue','27 Sep 2024');
INSERT INTO BOMHeading VALUES(2,'Green','27 Sep 2024');
INSERT INTO BOMHeading VALUES(3,'Red','27 Sep 2024');
INSERT INTO BOMHeading VALUES(4,'Yellow','27 Sep 2024');
INSERT INTO BOMHeading VALUES(5,'Pink','27 Sep 2024');
INSERT INTO BOMHeading VALUES(6,'Black','27 Sep 2024');
INSERT INTO BOMHeading VALUES(7,'White','27 Sep 2024');
INSERT INTO BOMHeading VALUES(8,'Clear','27 Sep 2024');
INSERT INTO BOMHeading VALUES(9,'Orange','27 Sep 2024');
INSERT INTO BOMHeading VALUES(10,'Mixer 1','27 Sep 2024');
INSERT INTO BOMHeading VALUES(11,'Mixer 2','27 Sep 2024');
CREATE TABLE BOMDetail (
    SrNo INT PRIMARY KEY AUTO_INCREMENT,
    FinalColor TEXT NOT NULL,
    BaseColor TEXT NOT NULL,
    Percentage REAL NOT NULL CHECK (Percentage BETWEEN 0 AND 100),
    Date DATE NOT NULL
);
INSERT INTO BOMDetail VALUES(1,'Blue','Blue',100.0,'27 Sep 2024');
INSERT INTO BOMDetail VALUES(2,'Green','Green',100.0,'27 Sep 2024');
INSERT INTO BOMDetail VALUES(3,'Red','Red',100.0,'27 Sep 2024');
INSERT INTO BOMDetail VALUES(4,'Yellow','Yellow',100.0,'27 Sep 2024');
INSERT INTO BOMDetail VALUES(5,'Pink','Pink',100.0,'27 Sep 2024');
INSERT INTO BOMDetail VALUES(6,'Black','Black',100.0,'27 Sep 2024');
INSERT INTO BOMDetail VALUES(7,'White','White',100.0,'27 Sep 2024');
INSERT INTO BOMDetail VALUES(8,'Clear','Clear',100.0,'27 Sep 2024');
INSERT INTO BOMDetail VALUES(9,'Orange','Orange',100.0,'27 Sep 2024');
INSERT INTO BOMDetail VALUES(10,'Mixer 1','Mixer 1',100.0,'27 Sep 2024');
INSERT INTO BOMDetail VALUES(11,'Mixer 2','Mixer 2',100.0,'27 Sep 2024');
CREATE TABLE DispensingHeading (
    SrNo INT PRIMARY KEY AUTO_INCREMENT,
    FinalColor TEXT NOT NULL,
    BatchNo TEXT NOT NULL,
    Quantity INTEGER NOT NULL CHECK (Quantity > 0),
    Date DATE NOT NULL,
    Duration INTEGER NOT NULL CHECK (Duration > 0)
);
INSERT INTO DispensingHeading VALUES(1,'Blue','Batch 1',100,'27 Sep 2024',10);
INSERT INTO DispensingHeading VALUES(2,'Green','Batch 2',100,'27 Sep 2024',10);
INSERT INTO DispensingHeading VALUES(3,'Red','Batch 3',100,'27 Sep 2024',10);
INSERT INTO DispensingHeading VALUES(4,'Yellow','Batch 4',100,'27 Sep 2024',10);
INSERT INTO DispensingHeading VALUES(5,'Pink','Batch 5',100,'27 Sep 2024',10);
INSERT INTO DispensingHeading VALUES(6,'Black','Batch 6',100,'27 Sep 2024',10);
INSERT INTO DispensingHeading VALUES(7,'White','Batch 7',100,'27 Sep 2024',10);
INSERT INTO DispensingHeading VALUES(8,'Clear','Batch 8',100,'27 Sep 2024',10);
INSERT INTO DispensingHeading VALUES(9,'Orange','Batch 9',100,'27 Sep 2024',10);
INSERT INTO DispensingHeading VALUES(10,'Mixer 1','Batch 10',100,'27 Sep 2024',10);
INSERT INTO DispensingHeading VALUES(11,'Mixer 2','Batch 11',100,'27 Sep 2024',10);
CREATE TABLE DispensingDetail (
    SrNo INT PRIMARY KEY AUTO_INCREMENT,
    FinalColor TEXT NOT NULL,
    BatchNo TEXT NOT NULL,
    BaseColor TEXT NOT NULL,
    Percentage REAL NOT NULL CHECK (Percentage BETWEEN 0 AND 100),
    Actual INTEGER NOT NULL CHECK (Actual >= 0),
    Date DATE NOT NULL
);
INSERT INTO DispensingDetail VALUES(1,'Blue','B001','Blue',100.0,100,'2024-09-27');
INSERT INTO DispensingDetail VALUES(2,'Green','B002','Green',100.0,100,'2024-09-27');
INSERT INTO DispensingDetail VALUES(3,'Red','B003','Red',100.0,100,'2024-09-27');
INSERT INTO DispensingDetail VALUES(4,'Yellow','B004','Yellow',100.0,100,'2024-09-27');
INSERT INTO DispensingDetail VALUES(5,'Pink','B005','Red',80.0,80,'2024-09-27');
INSERT INTO DispensingDetail VALUES(6,'Pink','B005','White',20.0,20,'2024-09-27');
INSERT INTO DispensingDetail VALUES(7,'Black','B006','Black',100.0,100,'2024-09-27');
INSERT INTO DispensingDetail VALUES(8,'White','B007','White',100.0,100,'2024-09-27');
INSERT INTO DispensingDetail VALUES(9,'Clear','B008','Clear',100.0,100,'2024-09-27');
INSERT INTO DispensingDetail VALUES(10,'Orange','B009','Red',60.0,60,'2024-09-27');
INSERT INTO DispensingDetail VALUES(11,'Orange','B009','Yellow',40.0,40,'2024-09-27');
INSERT INTO DispensingDetail VALUES(12,'Mixer 1','B010','Blue',50.0,50,'2024-09-27');
INSERT INTO DispensingDetail VALUES(13,'Mixer 1','B010','Green',50.0,50,'2024-09-27');
INSERT INTO DispensingDetail VALUES(14,'Mixer 2','B011','Red',70.0,70,'2024-09-27');
INSERT INTO DispensingDetail VALUES(15,'Mixer 2','B011','Yellow',30.0,30,'2024-09-27');
CREATE TABLE StockRecord (
    SrNo INT PRIMARY KEY,
    BaseColor TEXT NOT NULL,
    BatchNumber TEXT NOT NULL,
    InQuantity INT NOT NULL CHECK (InQuantity > 0),
    Date DATE NOT NULL
);
INSERT INTO StockRecord VALUES(1,'Blue','B001',100,'2024-09-27');
INSERT INTO StockRecord VALUES(2,'Green','B002',150,'2024-09-27');
INSERT INTO StockRecord VALUES(3,'Red','B003',200,'2024-09-27');
INSERT INTO StockRecord VALUES(4,'Yellow','B004',120,'2024-09-27');
INSERT INTO StockRecord VALUES(5,'Pink','B005',180,'2024-09-27');
INSERT INTO StockRecord VALUES(6,'Black','B006',250,'2024-09-27');
INSERT INTO StockRecord VALUES(7,'White','B007',220,'2024-09-27');
INSERT INTO StockRecord VALUES(8,'Clear','B008',280,'2024-09-27');
INSERT INTO StockRecord VALUES(9,'Orange','B009',300,'2024-09-27');
INSERT INTO StockRecord VALUES(10,'Mixer 1','B010',350,'2024-09-27');
INSERT INTO StockRecord VALUES(11,'Mixer 2','B011',380,'2024-09-27');
-- COMMIT;
