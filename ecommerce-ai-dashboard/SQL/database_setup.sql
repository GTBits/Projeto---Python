DROP DATABASE IF EXISTS Ecommerce_DB;
GO
CREATE DATABASE Ecommerce_DB;
GO
USE Ecommerce_DB;
GO

CREATE TABLE Vendedores (
    ID_Vendedor INT IDENTITY(1,1) PRIMARY KEY,
    Nome_Vendedor VARCHAR(100),
    Regiao VARCHAR(50)
);

CREATE TABLE Categorias (
    ID_Categoria INT IDENTITY(1,1) PRIMARY KEY,
    Nome_Categoria VARCHAR(50)
);

CREATE TABLE Produtos (
    ID_Produto INT IDENTITY(1,1) PRIMARY KEY,
    ID_Categoria INT FOREIGN KEY REFERENCES Categorias(ID_Categoria),
    Nome_Produto VARCHAR(100),
    Preco_Custo DECIMAL(10,2),
    Preco_Venda DECIMAL(10,2)
);

CREATE TABLE Transportadoras (
    ID_Transportadora INT IDENTITY(1,1) PRIMARY KEY,
    Nome_Transportadora VARCHAR(50),
    Custo_Base DECIMAL(10,2)
);

CREATE TABLE Canais_Marketing (
    ID_Canal INT IDENTITY(1,1) PRIMARY KEY,
    Nome_Canal VARCHAR(50),
    Custo_Aquisicao_Medio DECIMAL(10,2)
);

CREATE TABLE Vendas (
    ID_Venda INT IDENTITY(1,1) PRIMARY KEY,
    Data_Venda DATE,
    ID_Produto INT FOREIGN KEY REFERENCES Produtos(ID_Produto),
    ID_Vendedor INT FOREIGN KEY REFERENCES Vendedores(ID_Vendedor),
    ID_Transportadora INT FOREIGN KEY REFERENCES Transportadoras(ID_Transportadora),
    ID_Canal INT FOREIGN KEY REFERENCES Canais_Marketing(ID_Canal),
    UF_Destino VARCHAR(2),
    Quantidade INT,
    Valor_Frete DECIMAL(10,2),
    Nota_Avaliacao INT 
);
GO

INSERT INTO Categorias VALUES ('Eletronicos'), ('Moda'), ('Casa'), ('Esportes');
INSERT INTO Vendedores VALUES ('Ricardo Silva', 'Sudeste'), ('Ana Paula', 'Sul'), ('Marcos Souza', 'Nordeste');
INSERT INTO Produtos VALUES 
(1, 'Smartphone X', 800, 1200), (1, 'Notebook Pro', 2500, 4000),
(2, 'Camisa Polo', 30, 89), (2, 'Tenis Corrida', 120, 299),
(3, 'Cafeteira', 100, 250), (3, 'Robo Aspirador', 400, 900),
(4, 'Bola de Futebol', 20, 120), (4, 'Bicicleta', 500, 1100);
INSERT INTO Transportadoras VALUES ('Correios Sedex', 25.00), ('Loggi', 15.00), ('Jadlog', 18.00);
INSERT INTO Canais_Marketing VALUES ('Google Ads', 50.00), ('Instagram', 35.00), ('Email Marketing', 5.00), ('Busca Organica', 0.00);
GO

DECLARE @Data DATE = '2023-01-01';
DECLARE @Estados TABLE (UF VARCHAR(2));
INSERT INTO @Estados VALUES ('SP'), ('RJ'), ('MG'), ('RS'), ('PR'), ('BA'), ('SC'), ('PE'), ('CE'), ('DF');

WHILE @Data <= '2025-12-31'
BEGIN
    DECLARE @Qtd_Vendas_Dia INT = (ABS(CHECKSUM(NEWID())) % 10) + 5;
    DECLARE @Contador INT = 0;

    WHILE @Contador < @Qtd_Vendas_Dia
    BEGIN
        IF MONTH(@Data) IN (11, 12) AND (ABS(CHECKSUM(NEWID())) % 100) < 30 CONTINUE;

        DECLARE @UF VARCHAR(2) = (SELECT TOP 1 UF FROM @Estados ORDER BY NEWID());
        DECLARE @Frete DECIMAL(10,2) = (ABS(CHECKSUM(NEWID())) % 50) + 15.00;
        
        DECLARE @Nota INT = (ABS(CHECKSUM(NEWID())) % 100);
        IF @Nota > 80 SET @Nota = 5;
        ELSE IF @Nota > 40 SET @Nota = 4;
        ELSE IF @Nota > 15 SET @Nota = 3;
        ELSE IF @Nota > 5 SET @Nota = 2;
        ELSE SET @Nota = 1;

        INSERT INTO Vendas (Data_Venda, ID_Produto, ID_Vendedor, ID_Transportadora, ID_Canal, UF_Destino, Quantidade, Valor_Frete, Nota_Avaliacao)
        VALUES (
            @Data, (ABS(CHECKSUM(NEWID())) % 8) + 1, (ABS(CHECKSUM(NEWID())) % 3) + 1, 
            (ABS(CHECKSUM(NEWID())) % 3) + 1, (ABS(CHECKSUM(NEWID())) % 4) + 1, 
            @UF, (ABS(CHECKSUM(NEWID())) % 4) + 1, @Frete, @Nota
        );
        SET @Contador = @Contador + 1;
    END
    SET @Data = DATEADD(DAY, 1, @Data);
END
GO
