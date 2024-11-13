-- 序列 (Sequences)

-- DDL for Sequence MEMBER_MID_SEQ
CREATE SEQUENCE MEMBER_MID_SEQ
    START WITH 5
    INCREMENT BY 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 20;

-- DDL for Sequence CART_TNO_SEQ
CREATE SEQUENCE CART_TNO_SEQ
    START WITH 9
    INCREMENT BY 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 20;

-- DDL for Sequence PACKAGE_PLID_SEQ
CREATE SEQUENCE PACKAGE_PLID_SEQ
    START WITH 10
    INCREMENT BY 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 20;

-- DDL for Sequence TRANSACTION_TID_SEQ
CREATE SEQUENCE TRANSACTION_TID_SEQ
    START WITH 15
    INCREMENT BY 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 20;

-- DDL for Sequence DESTINATION_DID_SEQ
CREATE SEQUENCE DESTINATION_DID_SEQ
    START WITH 20
    INCREMENT BY 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 20;

-- DDL for Sequence ACCOMMODATION_AID_SEQ
CREATE SEQUENCE ACCOMMODATION_AID_SEQ
    START WITH 25
    INCREMENT BY 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 20;


-- 會員 (Member Table)
CREATE TABLE MEMBER (
    MID BIGINT PRIMARY KEY DEFAULT NEXTVAL('MEMBER_MID_SEQ'),
    NAME VARCHAR(128) NOT NULL,       -- 名字
    ACCOUNT VARCHAR(128) NOT NULL,    -- 帳號
    PASSWORD VARCHAR(128) NOT NULL,   -- 密碼
    IDENTITY VARCHAR(128) NOT NULL    -- 身份
);

-- 購物車 (Cart Table)
CREATE TABLE CART (
    TNO BIGINT PRIMARY KEY DEFAULT NEXTVAL('CART_TNO_SEQ'),
    MID BIGINT REFERENCES MEMBER(MID),
    CARTTIME TIMESTAMP NOT NULL       -- 購物車創建時間
);

-- 旅遊套餐 (Package Table)
CREATE TABLE PACKAGE (
    PLID BIGINT PRIMARY KEY DEFAULT NEXTVAL('PACKAGE_PLID_SEQ'),
    STARTDATE DATE NOT NULL,          -- 開始日期
    ENDDATE DATE NOT NULL,            -- 結束日期
    TOTALPRICE BIGINT NOT NULL,       -- 總價格
    AMOUNT INT NOT NULL               -- 人數
);

-- 景點 (Destination Table)
CREATE TABLE DESTINATION (
    DESTINATIONID BIGINT PRIMARY KEY DEFAULT NEXTVAL('DESTINATION_DID_SEQ'),
    DNAME VARCHAR(128) NOT NULL,           -- 景點名稱
    LOCATION TEXT NOT NULL,                -- 位置描述
    DPRICE BIGINT NOT NULL,                -- 門票價格
    DPID BIGINT REFERENCES PACKAGE(PLID),  -- 所屬套餐ID
    DESCRIPTION TEXT                       -- 地點描述
);

-- 住宿 (Accommodation Table)
CREATE TABLE ACCOMMODATION (
    ACCID BIGINT PRIMARY KEY DEFAULT NEXTVAL('ACCOMMODATION_AID_SEQ'),
    ACCNAME VARCHAR(128) NOT NULL,    -- 住宿名稱
    ADDRESS TEXT NOT NULL,            -- 地址
    DAYS INT NOT NULL,                -- 天數
    ACCPRICE BIGINT NOT NULL,         -- 住宿價格
    ACCPID BIGINT REFERENCES PACKAGE(PLID) -- 所屬套餐ID
);

ALTER TABLE accommodation
ADD CONSTRAINT fk_accpid_package
FOREIGN KEY (accpid) REFERENCES package(plid);

-- 交易 (Transaction Table)
CREATE TABLE TRANSACTION (
    TRANSACTIONID BIGINT PRIMARY KEY DEFAULT NEXTVAL('TRANSACTION_TID_SEQ'),
    METHOD VARCHAR(50) NOT NULL,      -- 交易方式
    TRANSACTIONDATE DATE NOT NULL,    -- 交易日期
    TRANSMID BIGINT REFERENCES MEMBER(MID) -- 會員ID
);

-- 紀錄 (Records Table)
CREATE TABLE RECORDS (
    TRANSACTIONID BIGINT REFERENCES TRANSACTION(TRANSACTIONID),
    PLID BIGINT REFERENCES PACKAGE(PLID),
    PRICE BIGINT NOT NULL,            -- 價格
    AMOUNT INT NOT NULL               -- 數量
);

-- 訂單 (Order Table)
CREATE TABLE ORDER_LIST (
    OID BIGINT PRIMARY KEY DEFAULT NEXTVAL('CART_TNO_SEQ'),
    MID BIGINT REFERENCES MEMBER(MID),
    CARTTIME TIMESTAMP NOT NULL,      -- 購物車時間
    PLID BIGINT REFERENCES PACKAGE(PLID) -- 套餐ID
);

-- Insert data into MEMBER table
INSERT INTO MEMBER (MID, NAME, ACCOUNT, PASSWORD, IDENTITY)
VALUES ('1', '王大明', 'MINGWANG', 'TEST', 'user');
INSERT INTO MEMBER (MID, NAME, ACCOUNT, PASSWORD, IDENTITY)
VALUES ('2', '孫小美', 'MAY', 'TEST', 'user');
INSERT INTO MEMBER (MID, NAME, ACCOUNT, PASSWORD, IDENTITY)
VALUES ('3', '林大偉', 'WEILIN', 'TEST', 'user');
INSERT INTO MEMBER (MID, NAME, ACCOUNT, PASSWORD, IDENTITY)
VALUES ('4', '陳美環', 'MAYCHANG', 'TEST', 'user');

-- 購物車資料
INSERT INTO CART (MID, CARTTIME)
VALUES 
(1, '2024-11-02 12:00:00'),
(2, '2024-11-03 14:30:00');

-- 套餐資料 (10 筆針對不同島嶼的旅遊套餐)
INSERT INTO PACKAGE (STARTDATE, ENDDATE, TOTALPRICE, AMOUNT)
VALUES 
('2024-12-01', '2024-12-05', 15000, 2),  -- 濟州島
('2024-12-10', '2024-12-15', 20000, 2),  -- 普吉島
('2024-12-20', '2024-12-25', 25000, 4),  -- 巴厘島
('2024-12-28', '2025-01-02', 18000, 2),  -- 長灘島
('2025-01-05', '2025-01-10', 22000, 2),  -- 富國島
('2025-02-01', '2025-02-07', 26000, 3),  -- 塞班島


-- 景點資料 (包括各地海島型景點)
INSERT INTO DESTINATION (DNAME, LOCATION, DPRICE, DPID, DESCRIPTION)
VALUES 
('漢拿山國家公園', '濟州島, 韓國', 2000, 1, '漢拿山國家公園位於濟州島的中心，是韓國的最高峰，以其壯麗的自然風光和豐富的生態系統著稱。'),
('西歸浦瀑布', '濟州島, 韓國', 1500, 1, '西歸浦瀑布是濟州島上著名的瀑布，擁有壯觀的水流和美麗的周圍景觀。'),
('普吉島大佛', '普吉島, 泰國', 1000, 2, '普吉島大佛是泰國普吉島上的著名地標，提供壯觀的視野和寧靜的氛圍。'),
('卡隆海灘', '普吉島, 泰國', 500, 2, '卡隆海灘是普吉島上受歡迎的沙灘，以其清澈的海水和白沙而著稱。'),
('烏魯瓦圖廟', '巴厘島, 印尼', 1800, 3, '烏魯瓦圖廟是巴厘島上著名的海岸寺廟，提供令人驚嘆的日落美景。'),
('聖猴森林', '巴厘島, 印尼', 1200, 3, '聖猴森林位於烏布，擁有豐富的文化遺產和活躍的猴子族群。'),
('白沙灘', '長灘島, 菲律賓', 800, 4, '長灘島的白沙灘以其純淨的白沙和清澈的海水而聞名，是熱門的度假勝地。'),
('麗貝島', '沙敦府, 泰國', 1500, 5, '麗貝島位於泰國南部，以其美麗的珊瑚礁和水下生態系統吸引潛水愛好者。'),
('瑪雅灣', '皮皮島, 泰國', 1000, 6, '瑪雅灣是皮皮島的著名景點，以其壯觀的峽灣和清澈的藍色海水而聞名。'),
('富國國家公園', '富國島, 越南', 1200, 7, '富國國家公園位於越南的富國島，以其豐富的生態和茂密的森林著稱。'),
('塞班島藍洞', '塞班島, 北馬里亞納群島', 2500, 8, '塞班島藍洞是深潛的理想地點，以其深邃的藍色海水吸引眾多潛水愛好者。'),
('薩摩亞阿波利馬島', '阿波利馬島, 薩摩亞', 700, 9, '阿波利馬島是薩摩亞的隱秘島嶼，擁有純淨的自然景觀和悠閒的氛圍。'),
('馬爾地夫清水潟湖', '馬爾地夫', 3000, 10, '馬爾地夫的清水潟湖以其清澈見底的水域和美麗的珊瑚礁著名。'),
('毛里求斯黑河峽谷', '毛里求斯', 1400, 11, '黑河峽谷是毛里求斯的一個自然奇觀，擁有壯觀的峽谷和瀑布。'),
('埃斯普蘭德斯島', '科蘇梅爾島, 墨西哥', 600, 12, '埃斯普蘭德斯島位於墨西哥的科蘇梅爾島，以其美麗的海灘和潛水點著稱。');

INSERT INTO ACCOMMODATION (ACCNAME, ADDRESS, DAYS, ACCPRICE, ACCPID)
VALUES 
('濟州Shilla酒店', '濟州市, 濟州島, 韓國', 4, 5000, 1),
('普吉島萬豪酒店', '卡隆海灘, 普吉島, 泰國', 5, 6000, 2),
('巴厘島Alila度假村', '烏布, 巴厘島, 印尼', 5, 8000, 3),
('長灘島Henann Regency Resort & Spa', '長灘島, 菲律賓', 4, 7000, 4),
('富國島Vinpearl Resort', '富國島, 越南', 4, 6500, 5),
('塞班島Fiesta Resort', '塞班島, 北馬里亞納群島', 6, 9000, 6),
('薩摩亞阿波利馬島Savaiian Hotel', '阿波利馬島, 薩摩亞', 3, 3000, 7),
('馬爾地夫Coco Palm Dhuni Kolhu', '馬爾地夫', 7, 15000, 8),
('科蘇梅爾島Occidental Cozumel', '科蘇梅爾島, 墨西哥', 4, 6000, 10);

-- 交易資料
INSERT INTO TRANSACTION (METHOD, TRANSACTIONDATE, TRANSMID)
VALUES 
('信用卡', '2024-11-01', 1),
('Paypal', '2024-11-02', 2);

-- 紀錄資料 (交易與套餐連結)
INSERT INTO RECORDS (TRANSACTIONID, PLID, PRICE, AMOUNT)
VALUES 
(1, 1, 15000, 2),
(2, 2, 20000, 2);

-- 訂單資料
INSERT INTO ORDER_LIST (MID, CARTTIME, PLID)
VALUES 
(1, '2024-11-01 12:34:56', 1),
(2, '2024-11-02 15:21:00', 2);

-- DDL for Trigger MEMBER_TRG
CREATE OR REPLACE FUNCTION SET_MEMBER_MID() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.MID IS NULL THEN
        NEW.MID := NEXTVAL('MEMBER_MID_SEQ');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE PLPGSQL;

CREATE TRIGGER MEMBER_TRG
BEFORE INSERT ON MEMBER
FOR EACH ROW
EXECUTE FUNCTION SET_MEMBER_MID();

-- DDL for Trigger ORDER_TRG
CREATE OR REPLACE FUNCTION SET_ORDER_OID() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.OID IS NULL THEN
        NEW.OID := NEXTVAL('ORDER_OID_SEQ');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE PLPGSQL;

CREATE TRIGGER ORDER_TRG
BEFORE INSERT ON ORDER_LIST
FOR EACH ROW
EXECUTE FUNCTION SET_ORDER_OID();

