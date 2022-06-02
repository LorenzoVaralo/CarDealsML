CREATE TABLE links(
    Id INTEGER NOT NULL UNIQUE PRIMARY KEY,
    href TEXT NOT NULL UNIQUE,
    olx_code TEXT NOT NULL UNIQUE,
    explored INTEGER DEFAULT 0
);

CREATE TABLE CarInfoRaw(
    Id INTEGER NOT NULL UNIQUE PRIMARY KEY,
    listId INTEGER NOT NULL UNIQUE,
    sellerName TEXT,
    adDate TEXT,
    price TEXT,
    mainCategory TEXT,
    subCategory TEXT,
    mainCategoryID INTEGER,
    subCategoryID INTEGER,
    estado TEXT,
    ddd TEXT,
    brand TEXT,
    model TEXT,
    versao TEXT,
    gearbox TEXT,
    titulo TEXT,
    region TEXT,
    category TEXT,
    vehicle_model TEXT,
    cartype TEXT,
    regdate TEXT,
    mileage TEXT,
    motorpower TEXT,
    fuel TEXT,
    car_steering TEXT,
    carcolor TEXT,
    doors TEXT,
    end_tag TEXT,
    dono TEXT,
    exchange TEXT,
    financial TEXT,
    extra TEXT,
    addesc TEXT,
    pro_vendor INTEGER
);

CREATE TABLE fipe(
    Valor TEXT, 
    Marca TEXT, 
    Modelo TEXT, 
    AnoModelo INTEGER, 
    Combustivel TEXT, 
    CodigoFipe TEXT, 
    MesReferencia TEXT, 
    TipoVeiculo INTEGER, 
    SiglaCombustivel TEXT
);

SELECT "Sqlite3: Tables created successfully! ✔️"