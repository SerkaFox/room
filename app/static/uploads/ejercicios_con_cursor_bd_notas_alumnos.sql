-- Paso 1: Crear la base de datos y usarla
DROP DATABASE IF EXISTS notas_alumnos;
CREATE DATABASE notas_alumnos;
USE notas_alumnos;

-- Paso 2: Crear la tabla 'alumnos'
CREATE TABLE alumnos (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, -- Identificador único para cada alumno
    nombre VARCHAR(50) NOT NULL,                -- Nombre del alumno, no puede ser nulo
    apellido1 VARCHAR(50) NOT NULL,             -- Primer apellido, no puede ser nulo
    apellido2 VARCHAR(50),                      -- Segundo apellido, puede ser nulo
    nota FLOAT                                  -- Nota del alumno, puede ser decimal
);

-- Paso 4: Insertar datos en la tabla 'alumnos'
INSERT INTO alumnos (nombre, apellido1, apellido2, nota) VALUES ('Pepe', 'López', 'López', -1); -- Nota ajustada a 0 por el trigger
INSERT INTO alumnos (nombre, apellido1, apellido2, nota) VALUES ('María', 'Sánchez', 'Sánchez', 11); -- Nota ajustada a 10 por el trigger
INSERT INTO alumnos (nombre, apellido1, apellido2, nota) VALUES ('Juan', 'Pérez', 'Pérez', 8.5); -- Nota válida, no se ajusta

-- Paso 3: Crear triggers para validar la nota antes de insertar o actualizar
-- Crear un procedimiento para ajustar las notas

DELIMITER $$

CREATE PROCEDURE ajustar_nota(INOUT nota FLOAT)
BEGIN
    IF nota IS NULL THEN
        SET nota = 0;
    ELSEIF nota < 0 THEN
        SET nota = 0;
    ELSEIF nota > 10 THEN
        SET nota = 10;
    END IF;
END$$

DELIMITER ;

DELIMITER $$

-- Trigger para validar la nota antes de insertar
DROP TRIGGER IF EXISTS comprobar_nota_antes_insertar$$
CREATE TRIGGER comprobar_nota_antes_insertar
BEFORE INSERT ON alumnos FOR EACH ROW
BEGIN
    CALL ajustar_nota(NEW.nota);
END$$

-- Trigger para validar la nota antes de actualizar
DROP TRIGGER IF EXISTS comprobar_nota_antes_actualizar$$
CREATE TRIGGER comprobar_nota_antes_actualizar
BEFORE UPDATE ON alumnos FOR EACH ROW
BEGIN
    CALL ajustar_nota(NEW.nota);
END$$

DELIMITER ;

-- Paso 6: Actualizar la nota de un alumno y verificar el ajuste por el trigger
UPDATE alumnos SET nota = -4.09 WHERE id = 3; -- Nota ajustada a 0 por el trigger
UPDATE alumnos SET nota = 14.27 WHERE id = 1; -- Nota ajustada a 10 por el trigger
UPDATE alumnos SET nota = 9.57 WHERE id = 2; -- Nota válida, no se ajusta

DELIMITER $$

-- Crear un procedimiento para mostrar los datos
CREATE PROCEDURE mostrar_alumnos()
BEGIN
    DECLARE done INT DEFAULT 0; -- Indicador para finalizar el cursor
    DECLARE alumno_id INT; -- Variable para almacenar el id del alumno
    DECLARE info_completa VARCHAR(200); -- para almacenar nombre y apellidos
    
    DECLARE nota_alumno FLOAT;
    -- Variable para almacenar la nota del alumno

    -- Declarar el cursor
    DECLARE alumnos_cursor CURSOR FOR
    SELECT id, CONCAT(nombre, ' ', apellido1, ' ', COALESCE(apellido2, ''), ' - cualqier texto') AS info_completa, nota
    FROM alumnos;

    -- Manejar la finalización del cursor
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    -- Abrir el cursor
    OPEN alumnos_cursor;

    -- Recorrer los registros del cursor
    read_loop: LOOP
        FETCH alumnos_cursor INTO alumno_id, info_completa, nota_alumno;
        IF done THEN
            LEAVE read_loop; -- Salir del bucle si no hay más registros
        END IF;
        
        -- Mostrar el registro actual
        SELECT alumno_id AS 'ID', 
			info_completa AS 'Información Completa', 
            nota_alumno AS 'Nota';
END LOOP;
        
        
        

    -- Cerrar el cursor
    CLOSE alumnos_cursor;
END$$

DELIMITER ;

-- Llamar al procedimiento
CALL mostrar_alumnos();

DELIMITER $$

-- Crear un procedimiento usando un cursor
CREATE PROCEDURE mostrar_alumnos_cursor2()
BEGIN
    DECLARE done INT DEFAULT 0; -- Indicador para finalizar el cursor
    DECLARE alumno_id INT; -- Variable para almacenar el id del alumno
    DECLARE nombre_alumno VARCHAR(50); -- Variable para almacenar el nombre del alumno
    DECLARE apellido1_alumno VARCHAR(50); -- Variable para almacenar el primer apellido
    DECLARE apellido2_alumno VARCHAR(50); -- Variable para almacenar el segundo apellido
    DECLARE nota_alumno FLOAT; -- Variable para almacenar la nota del alumno

    -- Declarar el cursor
    DECLARE alumnos_cursor CURSOR FOR
        SELECT id, nombre, apellido1, apellido2, nota FROM alumnos;

    -- Manejar la finalización del cursor
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    -- Crear una tabla temporal para almacenar los datos
    CREATE TEMPORARY TABLE IF NOT EXISTS resultados (
        id INT,
        nombre VARCHAR(50),
        apellido1 VARCHAR(50),
        apellido2 VARCHAR(50),
        nota FLOAT
    );

    -- Abrir el cursor
    OPEN alumnos_cursor;

    -- Recorrer los registros del cursor
    read_loop: LOOP
        FETCH alumnos_cursor INTO alumno_id, nombre_alumno, apellido1_alumno, apellido2_alumno, nota_alumno;
        IF done THEN
            LEAVE read_loop; -- Salir del bucle si no hay más datos
        END IF;

        -- Insertar el registro actual en la tabla temporal
        INSERT INTO resultados (id, nombre, apellido1, apellido2, nota)
        VALUES (alumno_id, nombre_alumno, apellido1_alumno, apellido2_alumno, nota_alumno);
    END LOOP;

    -- Cerrar el cursor
    CLOSE alumnos_cursor;

    -- Mostrar todos los registros de la tabla temporal
    SELECT * FROM resultados;

    -- Eliminar la tabla temporal
    DROP TEMPORARY TABLE resultados;
END$$

DELIMITER ;

-- Llamar al procedimiento
CALL mostrar_alumnos_cursor2();
