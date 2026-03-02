CREATE DATABASE Tunel_Gases;
GO

USE Tunel_Gases;
GO

CREATE TABLE Dim_Gas (
    ID_Gas INT PRIMARY KEY,
    Nome_Gas VARCHAR(50),
    Sigla VARCHAR(10),
    Limite_Alerta DECIMAL(5,2),
    Limite_Critico DECIMAL(5,2)
);

CREATE TABLE Dim_Estaca_Ventilacao (
    Estaca_Metros INT PRIMARY KEY,
    Capacidade_Exaustor_CFM INT
);

CREATE TABLE Fato_Telemetria_Gases (
    ID_Leitura INT IDENTITY(1,1) PRIMARY KEY,
    Estaca_Metros INT FOREIGN KEY REFERENCES Dim_Estaca_Ventilacao(Estaca_Metros),
    ID_Gas INT FOREIGN KEY REFERENCES Dim_Gas(ID_Gas),
    Data_Hora DATETIME NOT NULL,
    Concentracao DECIMAL(6,2) NOT NULL,
    Potencia_Exaustor_Pct INT NOT NULL
);
GO

INSERT INTO Dim_Gas (ID_Gas, Nome_Gas, Sigla, Limite_Alerta, Limite_Critico) VALUES
(1, 'Monoxido de Carbono', 'CO', 25.0, 39.0),
(2, 'Dioxido de Nitrogenio', 'NO2', 3.0, 5.0),
(3, 'Gas Combustivel', 'LEL', 10.0, 20.0);

INSERT INTO Dim_Estaca_Ventilacao (Estaca_Metros, Capacidade_Exaustor_CFM) VALUES 
(160, 50000), (180, 50000), (200, 50000), (220, 75000), (240, 75000);
GO

-- Injetando telemetria e o incidente na Frente 240m
DECLARE @estaca INT;
DECLARE @gas INT;
DECLARE @concentracao DECIMAL(6,2);
DECLARE @exaustor INT;

DECLARE cursor_estacas CURSOR FOR SELECT Estaca_Metros FROM Dim_Estaca_Ventilacao;
OPEN cursor_estacas;
FETCH NEXT FROM cursor_estacas INTO @estaca;

WHILE @@FETCH_STATUS = 0
BEGIN
    DECLARE cursor_gases CURSOR FOR SELECT ID_Gas FROM Dim_Gas;
    OPEN cursor_gases;
    FETCH NEXT FROM cursor_gases INTO @gas;
    
    WHILE @@FETCH_STATUS = 0
    BEGIN
        IF @estaca = 240 AND @gas = 1
        BEGIN
            SET @concentracao = 45.5; 
            SET @exaustor = 100;      
        END
        ELSE IF @estaca = 220 AND @gas = 1
        BEGIN
            SET @concentracao = 28.0; 
            SET @exaustor = 60;
        END
        ELSE
        BEGIN
            SET @concentracao = (RAND() * 2); 
            SET @exaustor = 30; 
        END

        INSERT INTO Fato_Telemetria_Gases (Estaca_Metros, ID_Gas, Data_Hora, Concentracao, Potencia_Exaustor_Pct)
        VALUES (@estaca, @gas, GETDATE(), @concentracao, @exaustor);
        
        FETCH NEXT FROM cursor_gases INTO @gas;
    END
    CLOSE cursor_gases;
    DEALLOCATE cursor_gases;
    
    FETCH NEXT FROM cursor_estacas INTO @estaca;
END
CLOSE cursor_estacas;
DEALLOCATE cursor_estacas;
GO

CREATE VIEW vw_Status_Qualidade_Ar AS
SELECT 
    f.Estaca_Metros,
    'Estaca ' + CAST(f.Estaca_Metros AS VARCHAR) + 'm' AS Nome_Local,
    g.Sigla,
    g.Nome_Gas,
    f.Concentracao,
    f.Potencia_Exaustor_Pct,
    CASE 
        WHEN f.Concentracao >= g.Limite_Critico THEN '[CRITICO]'
        WHEN f.Concentracao >= g.Limite_Alerta THEN '[ALERTA]'
        ELSE '[NORMAL]'
    END AS Status_Seguranca
FROM Fato_Telemetria_Gases f
INNER JOIN Dim_Gas g ON f.ID_Gas = g.ID_Gas;
GO
