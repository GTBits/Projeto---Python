CREATE DATABASE Tunel_Ops;
GO

USE Tunel_Ops;
GO

CREATE TABLE Leitura_Convergencia (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    Nome_Instrumento VARCHAR(50),
    Dias_Apos_Escavacao INT,
    Valor_Deformacao_mm DECIMAL(10,2),
    Geologia VARCHAR(100)
);
GO

-- Inserindo dados simulados para a IA de Regressao Linear ter o que ler
INSERT INTO Leitura_Convergencia (Nome_Instrumento, Dias_Apos_Escavacao, Valor_Deformacao_mm, Geologia) VALUES
('Estaca 160m', 1, 2.0, 'Maciço com Falha'),
('Estaca 160m', 2, 4.5, 'Maciço com Falha'),
('Estaca 160m', 3, 6.1, 'Maciço com Falha'),
('Estaca 180m', 1, 1.5, 'Maciço com Falha'),
('Estaca 180m', 2, 3.2, 'Maciço com Falha'),
('Estaca 180m', 3, 5.0, 'Maciço com Falha'),
('Estaca 200m', 1, 3.0, 'Maciço com Falha'),
('Estaca 200m', 2, 6.5, 'Maciço com Falha'),
('Estaca 200m', 3, 9.8, 'Maciço com Falha'),
('Estaca 220m', 1, 4.0, 'Maciço com Falha'),
('Estaca 220m', 2, 8.2, 'Maciço com Falha'),
('Estaca 220m', 3, 15.5, 'Maciço com Falha'),
('Estaca 240m', 1, 5.0, 'Maciço com Falha'),
('Estaca 240m', 2, 12.0, 'Maciço com Falha'),
('Estaca 240m', 3, 22.5, 'Maciço com Falha');
GO

CREATE VIEW vw_Monitoramento_Tunel AS
SELECT Nome_Instrumento, Dias_Apos_Escavacao, Valor_Deformacao_mm, Geologia
FROM Leitura_Convergencia;
GO
