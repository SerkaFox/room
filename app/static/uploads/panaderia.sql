-- POR SI NOS DA ERROR CUANDO QUEREMOS MODIFICAR DATOS EN CUALQUIER BD
-- set sql_safe_updates=0;

-- SI NOS DA ERROR Y QUEREMOS DESACTIVAR TEMPORALMENTE UNA FK
-- SET FOREIGN_KEY_CHECKS = 0;

-- PARA DEJAR DE NUEVO ACTIVADAS LAS FK
-- SET FOREIGN_KEY_CHECKS = 1;

DROP DATABASE IF EXISTS panaderia;
CREATE DATABASE IF NOT EXISTS panaderia;
use panaderia;

CREATE TABLE departamentos
(
id_departamento INT PRIMARY KEY AUTO_INCREMENT,
nombre VARCHAR(100)
);

CREATE TABLE empleados
(
id_empleado INT PRIMARY KEY AUTO_INCREMENT,
nombre VARCHAR(100),
apellido VARCHAR(100),
email VARCHAR(100),
telefono VARCHAR(12),
domicilio VARCHAR(100),
departamento_id INT,
CONSTRAINT fk_departamentos
FOREIGN KEY (departamento_id) 
REFERENCES departamentos (id_departamento)
);

CREATE TABLE proveedores
(   id_proveedor INT PRIMARY KEY AUTO_INCREMENT,
	nombre VARCHAR(100),
    email VARCHAR(100),
    telefono VARCHAR(12),
    direccion VARCHAR(100)
);

CREATE TABLE categorias
(
id_categoria INT PRIMARY KEY AUTO_INCREMENT,
nombre VARCHAR(100)
);


CREATE TABLE productos
(
	id_producto INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100),
    tipo_producto SET('PRIMARIO','PROCESADO','INMOBILIARIO'),
    cantidad INT NOT NULL,
    precio DECIMAL(8,2),
    proveedor_id INT,
    categoria_id INT,
    CONSTRAINT fk_proveedor
    FOREIGN KEY (proveedor_id)
    REFERENCES proveedores (id_proveedor),
    CONSTRAINT fk_categoria
    FOREIGN KEY (categoria_id)
    REFERENCES categorias (id_categoria)
);

CREATE TABLE clientes
(   id_cliente INT PRIMARY KEY AUTO_INCREMENT,
	nombre VARCHAR(100),
    email VARCHAR(100),
    telefono VARCHAR(12),
    direccion VARCHAR(100)
);

CREATE TABLE compras
(id_compra INT PRIMARY KEY AUTO_INCREMENT,
cantidad INT,
producto_id INT,
proveedor_id INT,
importe_total DECIMAL(10,2),
fecha_compra datetime NOT NULL,
estado_compra SET('pedido','enviado',
'recibido','cancelado','devuelto'),
CONSTRAINT fk_producto
FOREIGN KEY (producto_id) REFERENCES productos (id_producto),
CONSTRAINT fk_proveedor_2
FOREIGN KEY (proveedor_id) REFERENCES proveedores (id_proveedor)
);

CREATE TABLE ventas
(id_ventas INT PRIMARY KEY AUTO_INCREMENT,
cantidad INT,
producto_id INT,
cliente_id INT,
importe_total DECIMAL(10,2),
fecha_venta datetime NOT NULL,
estado_venta SET('pedido','enviado',
'recibido','cancelado','devuelto','presupuesto'),
CONSTRAINT fk_producto_2
FOREIGN KEY (producto_id) REFERENCES productos (id_producto),
CONSTRAINT fk_cliente
FOREIGN KEY (cliente_id) REFERENCES clientes (id_cliente)
);

-- departamentos
INSERT INTO departamentos (nombre) VALUES
('Producción'),
('Ventas'),
('Logística'),
('Administración');

-- empleados
INSERT INTO empleados (nombre, apellido, email, telefono, domicilio, departamento_id) VALUES
('Juan', 'Pérez', 'juan.perez@panaderia.com', '1234567890', 'Calle Falsa 123', 1),
('María', 'Gómez', 'maria.gomez@panaderia.com', '0987654321', 'Avenida Siempre Viva 742', 2),
('Carlos', 'López', 'carlos.lopez@panaderia.com', '1122334455', 'Boulevard de los Sueños 456', 3),
('Ana', 'Martínez', 'ana.martinez@panaderia.com', '5566778899', 'Calle de la Paz 789', 4);

-- proveedores

INSERT INTO proveedores (nombre, email, telefono, direccion) VALUES
('Harinas del Norte', 'contacto@harinasnorte.com', '1231231234', 'Calle Harina 100'),
('Lácteos del Sur', 'ventas@lacteossur.com', '3213214321', 'Avenida Leche 200'),
('Frutas y Verduras S.A.', 'info@frutasyverduras.com', '4564564567', 'Camino Verde 300'),
('PROPIO', 'info@panaderia.com', '123451234', 'Bagatza 01'),
('Muebles Bagatza', 'info@mueblesbagatza.com', '432154321', 'Bagatza 05');

-- categorías

INSERT INTO categorias (nombre) VALUES
('Ingredientes básicos'),
('Pan'),
('Pasteles'),
('Bollería'),
('Bebidas'),
('mobiliario'),
('compra granel');

-- productos

INSERT INTO productos (nombre, tipo_producto, cantidad, precio, proveedor_id, categoria_id) VALUES
('Harina 50 GRAMOS', 'PRIMARIO', 100, 1.50, 4, 1),
('Croissant', 'PROCESADO', 50, 0.80, 4, 4),
('Tarta de Manzana', 'PROCESADO', 20, 15.00, 4, 3),
('horno leña', 'INMOBILIARIO', 30, 2.50, 5, 6),
('Pastel de arroz', 'PROCESADO', 20, 1.50, 4, 3),
('Carolina', 'PROCESADO', 20, 1.50, 4, 3),
('azúcar', 'PRIMARIO', 20, 15.0, 2, 7),
('Barra Integral', 'PROCESADO', 20, 1.50, 4, 2),
('Suso de crema', 'PROCESADO', 20, 1.50, 4, 4),
('almendras', 'PRIMARIO', 20, 22.0, 2, 7);
-- clientes

INSERT INTO clientes (nombre, email, telefono, direccion) VALUES
('Laura Fernández', 'laura.fernandez@gmail.com', '9876543210', 'Calle Luna 101'),
('Pedro Sánchez', 'pedro.sanchez@yahoo.com', '8765432109', 'Avenida Sol 202'),
('Lucía Ramírez', 'lucia.ramirez@hotmail.com', '7654321098', 'Plaza Estrella 303');

-- compras

INSERT INTO compras (cantidad, producto_id, proveedor_id, importe_total, fecha_compra, estado_compra) VALUES
(50, 1, 1, 75.00, '2023-10-01 10:00:00', 'recibido'),
(30, 2, 1, 24.00, '2023-10-02 11:00:00', 'enviado'),
(20, 3, 2, 300.00, '2023-10-03 12:00:00', 'pedido');

-- ventas

INSERT INTO ventas (cantidad, producto_id, cliente_id, importe_total, fecha_venta, estado_venta) VALUES
(10, 1, 1, 15.00, '2023-10-04 13:00:00', 'recibido'),
(5, 2, 2, 4.00, '2023-10-05 14:00:00', 'enviado'),
(2, 3, 3, 30.00, '2023-10-06 15:00:00', 'pedido');


-- productos:
-- crear columna con importe_neto (sin iva del 21%)

ALTER TABLE productos
ADD COLUMN precio_neto decimal(8,2);





-- Trigger donde se calcule ese importe neto y se aplique a la columna precio_neto
DELIMITER $$

CREATE TRIGGER actualizar_precios_netos
BEFORE UPDATE ON productos
FOR EACH ROW
BEGIN
    IF NEW.precio != OLD.precio THEN
        SET NEW.precio_neto = NEW.precio * 0.79;
    END IF;
END$$

DELIMITER ;

DELIMITER $$

CREATE TRIGGER insertar_precios_netos
BEFORE INSERT ON productos
FOR EACH ROW
BEGIN
    
        SET NEW.precio_neto = NEW.precio * 0.79;
    
END$$

DELIMITER ;

-- actualizar los productos actuales que ya tenemos incorporados y ponerles el precio_neto



DELIMITER $$
 DROP PROCEDURE IF EXISTS act_netos$$
 CREATE PROCEDURE act_netos()
 BEGIN
 UPDATE productos
 set precio_neto = precio / 1.21 ;
 END$$
 DELIMITER ;
 
 call act_netos;
 
 

 
-- ventas: 
-- procedure: que al realizar la venta en función de la cantidad haga un descuento. Si se compran más de 10 un 10% y si se compran más de 50 un 20%.

DELIMITER $$

CREATE PROCEDURE aplicar_descuento_venta(
IN p_producto_id INT,
IN p_cliente_id INT,
IN p_cantidad INT,
OUT p_descuento DECIMAL(8,2),
OUT p_total DECIMAL(10,2)
)
BEGIN
DECLARE precio_unitario DECIMAL (8,2);
DECLARE p_descuento DECIMAL (8,2) DEFAULT 0;

  -- OBTENER EL PRECIO DEL PRODUCTO
  SELECT precio INTO precio_unitario
  FROM productos
  -- WHERE id_producto = p_producto_id
  ;
  
   -- CALCULAMOS DESCUENTO
   IF p_cantidad > 50 THEN
   SET p_total = p_cantidad * precio_unitario * (1 - 0.20);
   ELSEIF p_cantidad > 10 THEN
   SET p_total = p_cantidad * precio_unitario * (1 - 0.10);
   
   END IF;

 -- CALCULO DEL IMPORTE TOTAL 
 -- SET p_total = p_cantidad * precio_unitario * (1 - p_descuento);
 
 
  -- REGISTRO LA VENTA EN LA TABLA DE VENTAS
  INSERT INTO ventas (cantidad, producto_id, Cliente_id, importe_total, fecha_venta, estado_venta)
  VALUES (p_cantidad, p_producto_id, p_Cliente_id, p_total, NOW(), 'pedido');
  END$$
  
  DELIMITER ;
  
  CALL aplicar_descuento_venta(1, 1, 1,@descuento, @total);
  SELECT @descuento, @total;




-- productos_old (tabla) = productos + fecha_cambio

-- drop table productos_old;
CREATE TABLE productos_old
(
	id_producto_old INT PRIMARY KEY AUTO_INCREMENT,
    id_producto INT,
    nombre VARCHAR(100),
    tipo_producto VARCHAR(100),
    cantidad INT,
    precio DECIMAL(8,2),
    proveedor_id INT,
    categoria_id INT,
    fecha_actualizacion datetime
);

-- Trigger donde se vuelcan los productos que actualizamos importes. Cada vez que actualizamos un importe de producto, queda guardado en la tabla productos_old el precio antiguo y la fecha en la que lo modificamos.


DELIMITER $$

CREATE TRIGGER actualizar_productos_old
BEFORE UPDATE ON productos
FOR EACH ROW
BEGIN
    IF NEW.precio != OLD.precio THEN
        INSERT INTO productos_old 
        VALUES (NULL, OLD.id_producto, OLD.nombre, OLD.tipo_producto, OLD.cantidad, OLD.precio, OLD.proveedor_id, OLD.categoria_id, NOW());
       
    END IF;
END$$

DELIMITER ;


-- insert into productos_old
update productos 
set precio = 125
where id_producto like 1;



-- productos_eliminados (tabla) = productos + fecha_elimnación
DROP TABLE productos_eliminados;
CREATE TABLE productos_eliminados
(
	id_producto_eliminado INT PRIMARY KEY AUTO_INCREMENT,
    id_producto INT,
    nombre VARCHAR(100),
    tipo_producto VARCHAR(100),
    cantidad INT,
    precio DECIMAL(8,2),
    proveedor_id INT,
    categoria_id INT,
    fecha_eliminacion datetime
);


-- Trigger donde se guardarán los productos que eliminemos con la fecha eliminación.

DELIMITER $$

CREATE TRIGGER guardar_productos_eliminados
BEFORE DELETE ON productos
FOR EACH ROW
BEGIN
    INSERT INTO productos_eliminados 
    VALUES (NULL, OLD.id_producto, OLD.nombre, OLD.tipo_producto, OLD.cantidad, OLD.precio, OLD.proveedor_id, OLD.categoria_id, NOW());
       
    
END$$

DELIMITER ;

/* simular la eliminación de un producto 



*/


-- Un trigger para actualizar automáticamente el estado de un producto cuando se realiza una venta.


/*

	ESTE LO VAMOS A ELIMINAR PORQUE GENERA ERROR, MEJOR CON EL PROCEDURE




DELIMITER $$

CREATE TRIGGER actualizar_cantidad_producto
AFTER INSERT ON ventas
FOR EACH ROW
BEGIN
    UPDATE productos
    SET cantidad = cantidad - NEW.cantidad
    WHERE id_producto = NEW.producto_id;
END$$

DELIMITER ;

*/


-- calcula el importe total, teniendo en cuenta la cantidad y el producto
-- drop Trigger calcular_importe_total_venta;
-- actualizamos también en tabla productos y restamos las unidades 
-- vendidas
-- CADA VEZ QUE VENDAMOS ALGO, NECESITAMOS QUE SE ACTUALICE EL STOCK
 -- DE ESOS PRODUCTOS QUE VENDEMOS. SI VENDEMOS UNA BARRA DE PAN
 -- EL SISTEMA DEBE ACTUALIZAR A (CANTIDAD -1) EN ESE PRODUCTO.

DELIMITER $$

CREATE TRIGGER calcular_importe_total_venta
BEFORE INSERT ON ventas
FOR EACH ROW
BEGIN
    DECLARE precio_unitario DECIMAL(8,2);
    DECLARE descuento DECIMAL(8,2) DEFAULT 0;

    -- Obtener el precio del producto
    SELECT precio INTO precio_unitario
    FROM productos
    WHERE id_producto = NEW.producto_id ;

    -- Calcular el descuento basado en la cantidad
    IF NEW.cantidad > 50 THEN
        SET descuento = 0.20;
    ELSEIF NEW.cantidad > 10 THEN
        SET descuento = 0.10;
    END IF;
    
	-- actualizamos en productos y restamos las unidades vendidas
	UPDATE productos
    SET cantidad = cantidad - NEW.cantidad
    WHERE id_producto = NEW.producto_id ;
    
    -- Calcular el nuevo importe total con descuento
    SET NEW.importe_total = NEW.cantidad * precio_unitario * (1 - descuento);
END$$

DELIMITER ;
 
 
-- COMPRAS
-- calcula el importe total, teniendo en cuenta la cantidad y el
-- producto que hemos pedido al proveedor
-- drop Trigger calcular_importe_total_compra;
-- actualizamos también en tabla productos y sumamos las unidades 
-- compradas

DELIMITER $$

CREATE TRIGGER calcular_importe_total_compra
BEFORE INSERT ON compras
FOR EACH ROW
BEGIN
    DECLARE precio_unitario DECIMAL(8,2);
    

    -- Obtener el precio del producto
    SELECT precio INTO precio_unitario
    FROM productos
    WHERE id_producto = NEW.producto_id ;

      
	-- actualizamos en productos y restamos las unidades vendidas
	UPDATE productos
    SET cantidad = cantidad + NEW.cantidad
    WHERE id_producto = NEW.producto_id ;
    
    -- Calcular el nuevo importe total
    SET NEW.importe_total = NEW.cantidad * precio_unitario;
    
END$$

DELIMITER ;
 
 
 
 
 /* agregar manualmente una venta  
  INSERT INTO ventas (cantidad, producto_id, cliente_id,estado_venta)
  values (51, 1, 1, 'pedido');
  */
  
 /* 
 
 NO VAMOS A USARLO YA QUE GENERA ERRORES, MEJOR USAR EL PROCEDURE Y LOS TRIGGERS EN PRODUCTOS
 
DELIMITER $$

CREATE TRIGGER verificar_stock_antes_de_venta
BEFORE INSERT ON ventas
FOR EACH ROW
BEGIN
    DECLARE stock_actual INT;

    -- Obtener el stock actual del producto
    SELECT cantidad INTO stock_actual
    FROM productos
    WHERE id_producto = NEW.producto_id;

    -- Verificar si la cantidad solicitada excede el stock disponible
    IF NEW.cantidad > stock_actual THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Advertencia: La cantidad solicitada excede el stock disponible.';
    END IF;
END$$

DELIMITER ;  
*/

/* agregar manualmente una venta
 INSERT INTO ventas (cantidad, producto_id, cliente_id, fecha_venta, estado_venta) VALUES (5, 1, 1, '2024-12-19 13:05:44', 'pedido');
*/  
  
-- cada vez que se haga una venta o un cambio en la cantidad de cualquier producto, -- que un trigger verifique
-- si el stock de ese producto baja de 10, para que nos avise.
  


INSERT INTO ventas (cantidad, producto_id, cliente_id, estado_venta) VALUES (21, 3, 1, 'recibido');

-- Error Code: 1690. BIGINT UNSIGNED value is out of range in 
-- '(`panaderia`.`productos`.`cantidad` - NEW.cantidad)'



DROP PROCEDURE IF EXISTS CheckProductQuantities;
DROP TRIGGER IF EXISTS trg_check_product_quantities_insert;
DROP TRIGGER IF EXISTS trg_check_product_quantities_update;
DROP TRIGGER IF EXISTS trg_check_product_quantities_delete;
DELIMITER $$

-- Crear el procedimiento para verificar los datos
CREATE PROCEDURE CheckProductQuantities(new_quantity INT, product_id INT)
BEGIN
    DECLARE current_quantity INT;
    DECLARE error_message TEXT;

    -- Obtener la cantidad actual del producto
    SELECT cantidad INTO current_quantity 
    FROM productos 
    WHERE id_producto = product_id;

    -- Si la nueva cantidad es menor a 0 (se vende más de lo disponible)
    IF new_quantity < 0 THEN
        IF (current_quantity + new_quantity) < 0 THEN
            SET error_message = CONCAT('Error: no se puede vender ', ABS(new_quantity), 
                                       ' unidades. Solo hay disponibles ', current_quantity, '.');
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = error_message;
        END IF;
    END IF;
END;
$$

DELIMITER ;

-- Crear los triggers para verificar los datos antes de los cambios
DELIMITER $$

-- Trigger para el evento BEFORE INSERT
CREATE TRIGGER trg_check_product_quantities_insert
BEFORE INSERT ON productos
FOR EACH ROW
BEGIN
    IF NEW.cantidad < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: la cantidad inicial no puede ser menor a cero.';
    END IF;
    CALL CheckProductQuantities(NEW.cantidad, NEW.id_producto);
END;
$$

-- Trigger para el evento BEFORE UPDATE
CREATE TRIGGER trg_check_product_quantities_update
BEFORE UPDATE ON productos
FOR EACH ROW
BEGIN
    IF NEW.cantidad < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: la nueva cantidad no puede ser menor a cero.';
    END IF;
    CALL CheckProductQuantities(NEW.cantidad - OLD.cantidad, OLD.id_producto);
END;
$$

-- Trigger para el evento BEFORE DELETE
CREATE TRIGGER trg_check_product_quantities_delete
BEFORE DELETE ON productos
FOR EACH ROW
BEGIN
    DECLARE error_message TEXT;

    -- No se puede eliminar si afecta la integridad de los datos
    SET error_message = 'Error: no se puede eliminar el producto mientras esté en uso en el sistema.';
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = error_message;
END;
$$

DELIMITER ;

/*
Escriba una función llamada contar_productos que reciba como entrada el nombre de la gama y devuelva el número de productos que existen dentro de esa gama.
*/

DELIMITER $$

 DROP FUNCTION IF EXISTS contar_productos$$
 CREATE FUNCTION contar_productos(gama VARCHAR(50))
 RETURNS INT UNSIGNED
 READS SQL DATA
 BEGIN
 -- Paso 1. Declaramos una variable local
 DECLARE total INT UNSIGNED;

 -- Paso 2. Contamos los productos
 SET total = (
 SELECT COUNT(*)
 FROM productos
 WHERE categoria_id = gama);

 -- Paso 3. Devolvemos el resultado
 RETURN total;
 END
 $$

 DELIMITER ;
 
 SELECT contar_productos(1);


/* esta función te devuelve los productos y el número de ellos que tienes.
*/
DELIMITER $$

DROP FUNCTION IF EXISTS contar_productos_por_categoria$$
CREATE FUNCTION contar_productos_por_categoria()
RETURNS TEXT
READS SQL DATA
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE categoria_id INT;
    DECLARE categoria_nombre TEXT;
    DECLARE total_productos INT;
    DECLARE resultado TEXT DEFAULT '';
    DECLARE cur CURSOR FOR SELECT id_categoria, nombre FROM categorias;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    OPEN cur;

    read_loop: LOOP
        FETCH cur INTO categoria_id, categoria_nombre;
        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Llamar a la función contar_productos para cada categoría
        SET total_productos = contar_productos(categoria_id);

        -- Concatenar el resultado
        SET resultado = CONCAT(resultado, categoria_nombre, ': '
        , total_productos,' <> ', '\n');
    END LOOP;

    CLOSE cur;

    RETURN resultado;
END$$

DELIMITER ;

SELECT contar_productos_por_categoria();