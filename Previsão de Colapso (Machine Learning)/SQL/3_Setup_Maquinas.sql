CREATE DATABASE Tunel_Maquinas;
GO

USE Tunel_Maquinas;
GO

CREATE TABLE Dim_Equipamento (
    ID_Equipamento INT PRIMARY KEY,
    Frota VARCHAR(20),
    Modelo VARCHAR(50),
    Tipo VARCHAR(30)
);

CREATE TABLE Fato_Telemetria_Maquinas (
    ID_Leitura INT IDENTITY(1,1) PRIMARY KEY,
    ID_Equipamento INT FOREIGN KEY REFERENCES Dim_Equipamento(ID_Equipamento),
    Data_Hora DATETIME NOT NULL,
    Temp_Motor_C DECIMAL(5,1) NOT NULL,
    Pressao_Oleo_Bar DECIMAL(5,1) NOT NULL,
    Combustivel_Pct INT NOT NULL
);
GO

INSERT INTO Dim_Equipamento (ID_Equipamento, Frota, Modelo, Tipo) VALUES
(1, 'ESC-01', 'Escavadeira CAT 336', 'Escavacao'),
(2, 'CAM-14', 'Caminhao Volvo A40G', 'Transporte'),
(3, 'CAM-15', 'Caminhao Volvo A40G', 'Transporte');
GO

INSERT INTO Fato_Telemetria_Maquinas (ID_Equipamento, Data_Hora, Temp_Motor_C, Pressao_Oleo_Bar, Combustivel_Pct) VALUES
(1, GETDATE(), 112.5, 1.2, 35),  
(2, GETDATE(), 88.0, 4.5, 78),   
(3, GETDATE(), 90.5, 4.2, 12);   
GO

CREATE VIEW vw_Status_Maquinario AS
SELECT 
    e.Frota,
    e.Modelo,
    e.Tipo,
    f.Temp_Motor_C,
    f.Pressao_Oleo_Bar,
    f.Combustivel_Pct,
    CASE 
        WHEN f.Temp_Motor_C >= 105.0 THEN '[CRITICO] Superaquecimento'
        WHEN f.Pressao_Oleo_Bar < 2.0 THEN '[CRITICO] Pressao do Oleo Baixa'
        WHEN f.Combustivel_Pct <= 15 THEN '[ALERTA] Abastecimento Necessario'
        ELSE '[NORMAL] Operando'
    END AS Status_Maquina
FROM Fato_Telemetria_Maquinas f
INNER JOIN Dim_Equipamento e ON f.ID_Equipamento = e.ID_Equipamento;
GO
