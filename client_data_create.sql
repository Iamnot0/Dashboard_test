CREATE DATABASE IF NOT EXISTS client_data;
USE client_data;

-- Create user for the application (optional - XAMPP can use root)
-- CREATE USER IF NOT EXISTS 'usird'@'localhost' IDENTIFIED BY 'usrid';
-- GRANT ALL PRIVILEGES ON client_data.* TO 'usird'@'localhost';
-- FLUSH PRIVILEGES;

CREATE TABLE IF NOT EXISTS clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    category VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    notes TEXT
);

-- Insert 100 clients across 10 categories
INSERT INTO clients (name, category) VALUES
-- Technology (10 clients)
('TechCorp Solutions', 'Technology'),
('Digital Innovations Inc', 'Technology'),
('ByteTech Systems', 'Technology'),
('CyberNet Solutions', 'Technology'),
('DataFlow Technologies', 'Technology'),
('CloudTech Partners', 'Technology'),
('SmartCode Solutions', 'Technology'),
('WebDev Masters', 'Technology'),
('IT Solutions Pro', 'Technology'),
('FutureTech Labs', 'Technology'),

-- Healthcare (10 clients)
('MedCare Plus', 'Healthcare'),
('HealthFirst Clinic', 'Healthcare'),
('Wellness Partners', 'Healthcare'),
('Medical Solutions Inc', 'Healthcare'),
('CareFirst Hospital', 'Healthcare'),
('HealthTech Systems', 'Healthcare'),
('PatientCare Network', 'Healthcare'),
('Medical Innovations', 'Healthcare'),
('Health Solutions Pro', 'Healthcare'),
('Wellness Technologies', 'Healthcare'),

-- Finance (10 clients)
('FinanceCorp Ltd', 'Finance'),
('MoneyFlow Bank', 'Finance'),
('Investment Partners', 'Finance'),
('Financial Solutions', 'Finance'),
('Capital Management', 'Finance'),
('WealthTech Systems', 'Finance'),
('Banking Solutions Pro', 'Finance'),
('Financial Innovations', 'Finance'),
('Money Management Inc', 'Finance'),
('Finance First', 'Finance'),

-- Education (10 clients)
('EduTech Solutions', 'Education'),
('Learning Partners', 'Education'),
('Academic Innovations', 'Education'),
('Education First', 'Education'),
('SchoolTech Systems', 'Education'),
('Learning Solutions Pro', 'Education'),
('Academic Partners', 'Education'),
('Education Technologies', 'Education'),
('School Solutions Inc', 'Education'),
('Learning First', 'Education'),

-- Immigration (10 clients)
('ImmigrationCorp Solutions', 'Immigration'),
('VisaTech Systems', 'Immigration'),
('Immigration Innovations', 'Immigration'),
('Legal Solutions Pro', 'Immigration'),
('Immigration Partners', 'Immigration'),
('VisaTech Innovations', 'Immigration'),
('Immigration Technologies', 'Immigration'),
('Legal Management Inc', 'Immigration'),
('Immigration Solutions First', 'Immigration'),
('VisaTech Partners', 'Immigration'),

-- Manufacturing (10 clients)
('ManufacturingCorp', 'Manufacturing'),
('FactoryTech Systems', 'Manufacturing'),
('Production Solutions', 'Manufacturing'),
('Manufacturing Pro', 'Manufacturing'),
('Factory Innovations', 'Manufacturing'),
('Production Partners', 'Manufacturing'),
('Manufacturing Tech', 'Manufacturing'),
('Factory Solutions Inc', 'Manufacturing'),
('Production First', 'Manufacturing'),
('Manufacturing Partners', 'Manufacturing'),

-- Real Estate (10 clients)
('RealEstateCorp', 'Real Estate'),
('PropertyTech Systems', 'Real Estate'),
('Real Estate Solutions', 'Real Estate'),
('Property Innovations', 'Real Estate'),
('Real Estate Pro', 'Real Estate'),
('Property Partners', 'Real Estate'),
('Real Estate Tech', 'Real Estate'),
('Property Solutions Inc', 'Real Estate'),
('Real Estate First', 'Real Estate'),
('Property Management', 'Real Estate'),

-- Transportation (10 clients)
('TransportCorp', 'Transportation'),
('LogisticsTech Systems', 'Transportation'),
('Transport Solutions', 'Transportation'),
('Logistics Innovations', 'Transportation'),
('Transport Pro', 'Transportation'),
('Logistics Partners', 'Transportation'),
('Transport Tech', 'Transportation'),
('Logistics Solutions Inc', 'Transportation'),
('Transport First', 'Transportation'),
('Logistics Management', 'Transportation'),

-- Marketing (10 clients)
('MarketingCorp', 'Marketing'),
('AdTech Systems', 'Marketing'),
('Marketing Solutions', 'Marketing'),
('Advertising Innovations', 'Marketing'),
('Marketing Pro', 'Marketing'),
('AdTech Partners', 'Marketing'),
('Marketing Tech', 'Marketing'),
('Advertising Solutions Inc', 'Marketing'),
('Marketing First', 'Marketing'),
('AdTech Management', 'Marketing'),

-- Consulting (10 clients)
('ConsultingCorp', 'Consulting'),
('ConsultTech Systems', 'Consulting'),
('Consulting Solutions', 'Consulting'),
('Consult Innovations', 'Consulting'),
('Consulting Pro', 'Consulting'),
('ConsultTech Partners', 'Consulting'),
('Consulting Tech', 'Consulting'),
('Consult Solutions Inc', 'Consulting'),
('Consulting First', 'Consulting'),
('ConsultTech Management', 'Consulting');