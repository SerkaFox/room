
-- PREGUNTA 1
CREATE DATABASE examen;
USE examen;

CREATE TABLE alumnos (
id_alumno INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
nombre VARCHAR (50),
apellido1 VARCHAR (50),
apellido2 VARCHAR (50),
nota DECIMAL (4,2));

-- TRIGGER 1

DELIMITER $$

CREATE TRIGGER check_nota_before_insert 
BEFORE INSERT ON alumnos
FOR EACH ROW
BEGIN
    IF NEW.nota < 0 then
        SET NEW.nota = 0;
    END IF;
    
    IF NEW.nota > 10 then 
    SET NEW.nota = 10;
	END IF;
    
END$$

DELIMITER ;


-- TRIGGER 2

DELIMITER $$

CREATE TRIGGER check_nota_before_update
BEFORE UPDATE ON alumnos 
FOR EACH ROW
BEGIN
        IF NEW.nota < 0 then
        SET NEW.nota = 0;
    END IF;
    
    IF NEW.nota > 10 then 
    SET NEW.nota = 10;
	END IF;
    
END$$

DELIMITER ;


-- UNA VEZ CREADO INSERTAMOS LOS ALUMNOS Y ACTUALIZAMOS LA TABLA


INSERT INTO alumnos (nombre, apellido1, apellido2, nota) VALUES
('Juan', 'Pérez', 'González', 9.75),
('Ana', 'Gómez', 'Sánchez', 8.50),
('Luis', 'Martínez', 'López', 7.30),
('María', 'Fernández', 'Ramírez', 9.00),
('Carlos', 'Díaz', 'Jiménez', 6.85),
('Laura', 'Hernández', 'Gutiérrez', 10.00),
('Pedro', 'Moreno', 'Torres', 8.25),
('Elena', 'Ruiz', 'Vázquez', 9.40),
('Miguel', 'Álvarez', 'Castro', 7.95),
('Sara', 'Jiménez', 'Molina', 6.60);


UPDATE alumnos
SET nota = -5
WHERE id_alumno=1;


UPDATE alumnos
SET nota = 15
WHERE id_alumno=2;


-- 2. CREAR NUEVA TABLA Y PROCEDURE

CREATE TABLE cuadrados (
numero INT UNSIGNED,
cuadrado INT UNSIGNED);


-- DROP PROCEDURE calcular_cuadrados;

DELIMITER $$

CREATE PROCEDURE calcular_cuadrados(IN tope INT UNSIGNED)
BEGIN
    DECLARE i INT UNSIGNED DEFAULT 1; 
    TRUNCATE TABLE cuadrados;
    WHILE i <= tope DO
	INSERT INTO cuadrados (numero, cuadrado)
        VALUES (i, i * i);
        SET i = i + 1;
    END WHILE;
END $$

DELIMITER ;


CALL calcular_cuadrados(10);

SELECT * FROM cuadrados;

-- 3. funcion que devuelve total de alumnos
DELIMITER $$

CREATE FUNCTION contar_alumnos()
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE total_alumnos INT;
    SELECT COUNT(*) INTO total_alumnos
    FROM alumnos;
    
    RETURN total_alumnos;
END $$

DELIMITER ;

SELECT contar_alumnos();








