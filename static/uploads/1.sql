-- 1. Crear la base de datos y seleccionarla
CREATE DATABASE practica_mysql;
USE practica_mysql;

-- 2. Crear la tabla "test"
CREATE TABLE test (
    id INT PRIMARY KEY,
    name VARCHAR(50)
);

-- 3. Insertar datos en la tabla "test"
INSERT INTO test (id, name) VALUES (1, 'Hola'), (2, 'Mundo');

-- 4. Contar el número de filas en la tabla "test"
SELECT COUNT(*) FROM test;

-- 5. La tabla "test" tiene dos filas: (1, 'Hola') y (2, 'Mundo')

-- 6. Crear la tabla "empleados"
CREATE TABLE empleados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50),
    edad INT,
    fecha_contratacion DATE
);

-- 7. Insertar un empleado en la tabla "empleados"
INSERT INTO empleados (id, nombre, edad, fecha_contratacion) VALUES (1, 'Ana', 28, '2022-05-10');

-- 8. Actualizar la edad de "Ana" a 30
UPDATE empleados SET edad = 30 WHERE id = 1;

-- 9. Contar el número de empleados con edad mayor a 25
SELECT COUNT(*) FROM empleados WHERE edad > 25;

-- 10. Después de las consultas anteriores, la tabla "empleados" tendrá una fila: (1, 'Ana', 30, '2022-05-10')

-- 11. Crear un procedimiento almacenado que devuelva los empleados mayores de 30 años
DELIMITER //
CREATE PROCEDURE GetEmpleadosMayores()
BEGIN
    SELECT * FROM empleados WHERE edad > 30;
END;
//
DELIMITER ;

-- 12. Crear un trigger para registrar la inserción de un empleado en "logs"
DELIMITER //
CREATE TRIGGER AfterInsertEmpleado
AFTER INSERT ON empleados
FOR EACH ROW
INSERT INTO logs (operacion, fecha) VALUES ('Insert', NOW());
//
DELIMITER ;

-- 13. Eliminar empleados con edad menor a 25
DELETE FROM empleados WHERE edad < 25;

-- 14. Crear la tabla "logs"
CREATE TABLE logs (
    id INT PRIMARY KEY,
    operacion VARCHAR(50),
    fecha DATE
);

-- 15. Después de las consultas anteriores, la tabla "logs" tendrá una fila por cada empleado insertado, con la operación registrada como "Insert".

-- 16. Agregar columna "salario" a la tabla "empleados"
ALTER TABLE empleados ADD salario DECIMAL(10,2);

-- 17. Consultar nombres y salarios de empleados cuyo salario sea mayor a 3000
SELECT nombre, salario FROM empleados WHERE salario > 3000;

-- 18. Crear la tabla "departamentos"
CREATE TABLE departamentos (
    id INT PRIMARY KEY,
    nombre VARCHAR(50)
);

-- 18.1. Agregar columna "departamento_id" en "empleados" y configurarla como clave foránea
ALTER TABLE empleados ADD departamento_id INT;
ALTER TABLE empleados ADD CONSTRAINT FOREIGN KEY (departamento_id) REFERENCES departamentos(id);

-- 19. Consultar empleados unidos a los departamentos por clave foránea
SELECT * FROM empleados JOIN departamentos ON empleados.departamento_id = departamentos.id;

-- 20. La consulta de la pregunta 17 devolvería todos los empleados con salario mayor a 3000.

-- 21. Eliminar columna "salario" de "empleados"
ALTER TABLE empleados DROP COLUMN salario;

-- 21.1. Agregar la columna "salario" a la tabla "empleados"
ALTER TABLE empleados ADD salario DECIMAL(10,2);

-- 22. Consultar el promedio de salario por departamento
SELECT departamentos.nombre, AVG(empleados.salario) FROM empleados JOIN departamentos ON empleados.departamento_id = departamentos.id GROUP BY departamentos.nombre;

-- 23. Agregar una restricción NOT NULL a la columna "nombre" en "departamentos"
ALTER TABLE departamentos MODIFY nombre VARCHAR(50) NOT NULL;

-- 24. Crear la vista "vista_empleados"
CREATE VIEW vista_empleados AS SELECT nombre, edad FROM empleados;

-- 25. La restricción NOT NULL en la columna "nombre" de "departamentos" no permitirá insertar valores nulos en esa columna.

-- 26. Eliminar empleados con salario menor a 1000
DELETE FROM empleados WHERE salario < 1000;

-- 27. Agregar clave foránea "departamento_id" en "empleados" que haga referencia a "id" en "departamentos"
ALTER TABLE empleados ADD FOREIGN KEY (departamento_id) REFERENCES departamentos(id);

-- 28. Actualizar el salario de todos los empleados en un 10%
UPDATE empleados SET salario = salario * 1.10;

-- 29. Crear la tabla "proyectos"
CREATE TABLE proyectos (
    id INT PRIMARY KEY,
    nombre VARCHAR(50),
    presupuesto DECIMAL(10,2)
);

-- 30. La clave foránea "departamento_id" en "empleados" ahora requiere que las inserciones coincidan con "id" en "departamentos".

-- 31. Crear la función para calcular el impuesto sobre el salario
DELIMITER //
CREATE FUNCTION calcular_impuesto(salario DECIMAL, porcentaje DECIMAL) RETURNS DECIMAL DETERMINISTIC
BEGIN
    RETURN salario * (porcentaje / 100);
END;
//
DELIMITER ;

-- 32. Crear procedimiento para aumentar el salario de empleados con más de 5 años en la empresa
DELIMITER //
CREATE PROCEDURE aumentar_salario()
BEGIN
    UPDATE empleados SET salario = salario * 1.05 WHERE TIMESTAMPDIFF(YEAR, fecha_contratacion, CURDATE()) > 5;
END;
//
DELIMITER ;

-- 33. Crear un trigger para registrar los cambios en el salario en "historial_salarios"
DELIMITER //
CREATE TRIGGER actualizar_historial
AFTER UPDATE ON empleados
FOR EACH ROW
INSERT INTO historial_salarios (empleado_id, salario_antiguo, salario_nuevo, fecha)
VALUES (OLD.id, OLD.salario, NEW.salario, NOW());
//
DELIMITER ;

-- 34. Consulta para calcular el total de presupuestos en la tabla "proyectos"
SET @total_presupuesto = 0;
SELECT SUM(presupuesto) INTO @total_presupuesto FROM proyectos;

-- 35. Los procedimientos y funciones definidos son: calcular_impuesto, aumentar_salario, actualizar_historial.

-- 36. Crear función para calcular el promedio de salarios por departamento
DELIMITER //
CREATE FUNCTION promedio_salario_departamento(departamento_id INT) RETURNS DECIMAL READS SQL DATA
BEGIN
    RETURN (SELECT AVG(salario) FROM empleados WHERE departamento_id = departamento_id);
END;
//
DELIMITER ;

-- 37. Crear procedimiento para eliminar proyectos con presupuesto menor al promedio
DELIMITER //
CREATE PROCEDURE eliminar_proyectos()
BEGIN
    DELETE FROM proyectos WHERE presupuesto < (SELECT AVG(presupuesto) FROM proyectos);
END;
//
DELIMITER ;

-- 38. Crear un trigger para impedir la inserción de empleados con un salario menor a 500
DELIMITER //
CREATE TRIGGER impedir_salarios
BEFORE INSERT ON empleados
FOR EACH ROW
IF NEW.salario < 500 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Salario demasiado bajo';
END IF;
//
DELIMITER ;

-- 39. Consulta con CASE para clasificar empleados por salario
SELECT nombre, CASE
    WHEN salario > 3000 THEN 'Alto'
    WHEN salario BETWEEN 1000 AND 3000 THEN 'Medio'
    ELSE 'Bajo'
END AS categoria
FROM empleados;

-- 40. Las categorías de salario definidas en la pregunta 39 son "Alto", "Medio", "Bajo"; y los empleados se clasifican según estas categorías.

-- 41. Insertar a "Paco Picapiedra" en la tabla "empleados"
INSERT INTO empleados (id, nombre, salario, fecha_contratacion) VALUES (NULL, 'Paco Picapiedra', 3000, '2020-12-12');

-- 42. Insertar en la tabla "departamentos" un nuevo departamento "Cueva Creativa"
INSERT INTO departamentos (nombre) VALUES ('Cueva Creativa');

-- 43. Añadir en la tabla "logs" un registro manual
INSERT INTO logs (id, operacion, fecha) VALUES (1, 'Picoteo de datos', NOW());

-- 44. Actualizar el salario de "Paco Picapiedra" a 3500
UPDATE empleados SET salario = 3500 WHERE nombre = 'Paco Picapiedra';

-- 45. Los cambios realizados en "empleados" y "logs" incluyen la actualización del salario de "Paco Picapiedra" y un registro en "logs" sobre la operación de picoteo.

-- 46. Insertar el departamento "Chistes y Memes"
INSERT INTO departamentos (nombre) VALUES ('Chistes y Memes');

-- 47. Añadir un registro en "logs" para la creación de "Chistes y Memes"
INSERT INTO logs (id, operacion, fecha) VALUES (2, 'Creación Chistes y Memes', CURRENT_DATE);

-- 48. Consultar el número total de empleados
SELECT COUNT(*) FROM empleados;

-- 49. Insertar "Juan Risueño" en la tabla "empleados"
INSERT INTO empleados (id, nombre, salario, fecha_contratacion) VALUES (6, 'Juan Risueño', 1800, '2023-01-10');

-- 50. Los registros agregados en "empleados" y "logs" incluyen "Juan Risueño" en "empleados" y un registro sobre la creación de "Chistes y Memes" en "logs".
