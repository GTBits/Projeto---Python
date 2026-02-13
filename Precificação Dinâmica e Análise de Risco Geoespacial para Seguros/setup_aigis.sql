CREATE DATABASE AIGIS_DB;
GO
USE AIGIS_DB;
GO

-- Tabela de Clientes (Perfil)
CREATE TABLE Policyholders (
    PolicyID INT PRIMARY KEY,
    Nome VARCHAR(100),
    Idade INT,
    Genero VARCHAR(10),
    Estado_Civil VARCHAR(20),
    Score_Credito INT, -- 0 a 1000
    Latitude FLOAT,  -- Onde mora (para mapa de risco)
    Longitude FLOAT
);

-- Tabela de Veículos (O Bem Segurado)
CREATE TABLE Vehicles (
    VehicleID INT PRIMARY KEY,
    PolicyID INT FOREIGN KEY REFERENCES Policyholders(PolicyID),
    Modelo VARCHAR(50),
    Ano_Modelo INT,
    Valor_Fipe DECIMAL(10,2),
    Categoria_Risco INT -- 1 (Baixo) a 5 (Esportivo/Visado)
);

-- Tabela de Histórico (Sinistros e Pagamentos)
CREATE TABLE Claims_History (
    HistoryID INT PRIMARY KEY,
    PolicyID INT FOREIGN KEY REFERENCES Policyholders(PolicyID),
    Teve_Sinistro INT, -- 0 ou 1 (Target Modelo 1)
    Custo_Sinistro DECIMAL(10,2), -- Valor do conserto (Target Modelo 2)
    Premio_Anual_Pago DECIMAL(10,2) -- Quanto ele pagou no ano passado
);