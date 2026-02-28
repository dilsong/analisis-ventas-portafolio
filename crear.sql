CREATE DATABASE ventas_portafolio;
USE ventas_portafolio;
CREATE TABLE vendedores (
    ID INT PRIMARY KEY,
    Nombre VARCHAR(100),
    Apellido VARCHAR(100),
    Region VARCHAR(100),
    FechaIngreso DATE
) ENGINE=InnoDB;
CREATE TABLE ventas (
    ID INT PRIMARY KEY,
    Fecha DATE,
    Cliente INT,
    Producto INT,
    Vendedor INT,
    Cantidad INT,
    PrecioVenta DECIMAL(10,2),
    Descuento DECIMAL(10,2),
    TotalVenta DECIMAL(10,2)
) ENGINE=InnoDB;
CREATE TABLE categorias (
    ID INT PRIMARY KEY,
    Nombre VARCHAR(100)
) ENGINE=InnoDB;
CREATE TABLE regiones (
    ID INT PRIMARY KEY,
    Nombre VARCHAR(100)
) ENGINE=InnoDB;
CREATE TABLE clientes (
    ID INT PRIMARY KEY,
    Nombre VARCHAR(100),
    Apellido VARCHAR(100),
    Email VARCHAR(150),
    Region VARCHAR(100),
    FechaRegistro DATE
) ENGINE=InnoDB;
CREATE TABLE productos (
    ID INT PRIMARY KEY,
    Nombre VARCHAR(100),
    Categoria INT,
    Costo DECIMAL(10,2),
    PrecioVenta DECIMAL(10,2)
) ENGINE=InnoDB;