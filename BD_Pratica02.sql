-- CRIAÇÃO DAS TABELAS
CREATE TABLE compras(
	id INT,
	produto VARCHAR(32)
);

CREATE TABLE inventario(
	TRANSACTION INT,
	Item VARCHAR(32),
	date_time VARCHAR(32),
	period_day VARCHAR(16),
	weekday_weekend VARCHAR(16)
);
