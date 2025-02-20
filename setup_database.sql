CREATE DATABASE sensor_data;

USE sensor_data;

CREATE TABLE movimentacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    posicao VARCHAR(50),
    estado INT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);