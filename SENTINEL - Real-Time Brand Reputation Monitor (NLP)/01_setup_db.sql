CREATE DATABASE SENTINEL_DB;
GO
USE SENTINEL_DB;
GO

-- Tabela de Ingestão (O "Twitter" joga aqui)
CREATE TABLE Raw_Posts (
    ID_Post INT IDENTITY(1,1) PRIMARY KEY,
    Data_Post DATETIME DEFAULT GETDATE(),
    Usuario VARCHAR(50),
    Texto_Original NVARCHAR(MAX), -- Texto livre (Unicode)
    Processado BIT DEFAULT 0 -- Flag: 0=Novo, 1=Já lido pelo robô
);

-- Tabela Refinada (Onde a IA guarda o resultado)
CREATE TABLE Gold_Analytics (
    ID_Analise INT IDENTITY(1,1) PRIMARY KEY,
    ID_Post INT, -- Link com a original
    Data_Post DATETIME,
    Texto_Limpo NVARCHAR(MAX),
    Sentimento_Predito VARCHAR(20), -- 'Positivo', 'Negativo', 'Neutro'
    Probabilidade FLOAT -- Quão certeza a IA tem?
);