USE `BIS698W1830_GRP12`;


CREATE TABLE `users` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `email` varchar(255) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('customer','admin','staff') NOT NULL,
  `active_status` int(1) NOT NULL DEFAULT 1,
  `pwd_change_req` int(1) NOT NULL DEFAULT 1,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `phone` (`phone`)
)  ;


CREATE TABLE `car` (
  `car_id` int(11) NOT NULL AUTO_INCREMENT,
  `make` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  `year` int(11) NOT NULL,
  `VIN` varchar(50) NOT NULL,
  `drivetrain` varchar(50) DEFAULT NULL,
  `price` decimal(10,2) NOT NULL,
  `mileage` int(11) NOT NULL,
  `fuel_type` varchar(50) NOT NULL,
  `transmission` varchar(50) NOT NULL,
  `car_color` varchar(50) NOT NULL,
  `car_condition` enum('Excellent','Good','Average') NOT NULL,
  `status` varchar(50) NOT NULL,
  `description` text DEFAULT NULL,
  `title` varchar(255) NOT NULL,
  `economy` decimal(11,0) NOT NULL,
  `main_image_id` int(11) DEFAULT NULL,
  `staff_id` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`car_id`),
  UNIQUE KEY `VIN` (`VIN`),
  KEY `staff_id` (`staff_id`),
  CONSTRAINT `` FOREIGN KEY (`staff_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ;



CREATE TABLE `carimages` (
  `image_id` int(11) NOT NULL AUTO_INCREMENT,
  `car_id` int(11) NOT NULL,
  `image` longblob NOT NULL,
  `is_main_image` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`image_id`),
  KEY `car_id` (`car_id`),
  CONSTRAINT `carimages_ibfk_1` FOREIGN KEY (`car_id`) REFERENCES `car` (`car_id`) ON DELETE CASCADE
) ;



CREATE TABLE `salesinvoice` (
  `sale_id` int(11) NOT NULL AUTO_INCREMENT,
  `car_id` int(11) NOT NULL,
  `customer_id` int(11) NOT NULL,
  `customer_first_name` varchar(255) NOT NULL,
  `customer_last_name` varchar(45) NOT NULL,
  `customer_email` varchar(255) NOT NULL,
  `customer_phone` varchar(20) NOT NULL,
  `id_type` varchar(50) NOT NULL,
  `id_number` varchar(50) NOT NULL,
  `address` text DEFAULT NULL,
  `listing_price` decimal(10,2) NOT NULL,
  `discount` decimal(10,2) NOT NULL DEFAULT 0.00,
  `tax_percent` decimal(3,2) NOT NULL DEFAULT 0.00,
  `tax_amount` decimal(10,2) NOT NULL DEFAULT 0.00,
  `total_price` decimal(10,2) NOT NULL,
  `payment_method` varchar(50) NOT NULL,
  `payment_reference` varchar(100) NOT NULL,
  `invoice_number` varchar(100) NOT NULL,
  `sale_date` timestamp NOT NULL DEFAULT current_timestamp(),
  `staff_id` int(11) NOT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`sale_id`),
  UNIQUE KEY `invoice_number` (`invoice_number`),
  KEY `car_id` (`car_id`),
  KEY `customer_id` (`customer_id`),
  KEY `staff_id` (`staff_id`),
  CONSTRAINT `salesinvoice_ibfk_1` FOREIGN KEY (`car_id`) REFERENCES `car` (`car_id`) ON DELETE CASCADE,
  CONSTRAINT `salesinvoice_ibfk_2` FOREIGN KEY (`customer_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `salesinvoice_ibfk_3` FOREIGN KEY (`staff_id`) REFERENCES `users` (`user_id`) ON DELETE SET NULL
) ;



CREATE TABLE `testdrivebooking` (
  `test_drive_id` int(11) NOT NULL AUTO_INCREMENT,
  `car_id` int(11) NOT NULL,
  `customer_id` int(11) NOT NULL,
  `staff_id` int(11) DEFAULT NULL,
  `preferred_date` date NOT NULL,
  `preferred_time` time NOT NULL,
  `status` enum('Pending','Confirmed','Completed','Cancelled') DEFAULT 'Pending',
  `reschedule_date` date DEFAULT NULL,
  `reschedule_time` time DEFAULT NULL,
  `cancellation_reason` text DEFAULT NULL,
  `location` varchar(100) DEFAULT 'PCDS, 1011 S Main St, Mt Pleasant, MI, USA - 48858',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`test_drive_id`),
  KEY `car_id` (`car_id`),
  KEY `customer_id` (`customer_id`),
  KEY `staff_id` (`staff_id`),
  CONSTRAINT `testdrivebooking_ibfk_1` FOREIGN KEY (`car_id`) REFERENCES `car` (`car_id`) ON DELETE CASCADE,
  CONSTRAINT `testdrivebooking_ibfk_2` FOREIGN KEY (`customer_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `testdrivebooking_ibfk_3` FOREIGN KEY (`staff_id`) REFERENCES `users` (`user_id`) ON DELETE SET NULL
)  ;



CREATE TABLE `customerinquiries` (
  `message_id` int(11) NOT NULL AUTO_INCREMENT,
  `car_id` int(11) NOT NULL,
  `customer_id` int(11) NOT NULL,
  `staff_id` int(11) DEFAULT NULL,
  `message_text` text NOT NULL,
  `response_text` text DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`message_id`),
  KEY `car_id` (`car_id`),
  KEY `customer_id` (`customer_id`),
  KEY `staff_id` (`staff_id`),
  CONSTRAINT `customerinquiries_ibfk_1` FOREIGN KEY (`car_id`) REFERENCES `car` (`car_id`) ON DELETE CASCADE,
  CONSTRAINT `customerinquiries_ibfk_2` FOREIGN KEY (`customer_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `customerinquiries_ibfk_3` FOREIGN KEY (`staff_id`) REFERENCES `users` (`user_id`) ON DELETE SET NULL
)  ;




CREATE TABLE `reviewandrating` (
  `review_id` int(11) NOT NULL AUTO_INCREMENT,
  `car_id` int(11) NOT NULL,
  `customer_id` int(11) NOT NULL,
  `rating` int(11) DEFAULT NULL,
  `review_text` text DEFAULT NULL,
  `response_text` text DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`review_id`),
  KEY `car_id` (`car_id`),
  KEY `customer_id` (`customer_id`),
  CONSTRAINT `reviewandrating_ibfk_1` FOREIGN KEY (`car_id`) REFERENCES `car` (`car_id`) ON DELETE CASCADE,
  CONSTRAINT `reviewandrating_ibfk_2` FOREIGN KEY (`customer_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `reviewandrating_chk_1` CHECK (`rating` between 1 and 5)
)  ;




INSERT INTO users (
    user_id, first_name, last_name, email, phone, password,
    role, active_status, pwd_change_req, created_at, updated_at
) VALUES (
    1, 'VIJAY', 'ATLA', 'ADMIN@PCDS.COM', '9896210000',
    'e86f78a8a3caf0b60d8e74e5942aa6d86dc150cd3c03338aef25b7d2d7e3acc7',
    'admin', 1, 0, '2025-04-16 08:21:56', '2025-05-05 00:53:37'
),
(
    2, 'ARUN', 'KUMAR', 'arun@cmu.com', '9876543201',
    'dfd48f36338aa36228ebb9e204bba6b4e18db0b623e25c458901edc831fb18e9',
    'staff', 1, 0, '2025-04-20 07:03:44', '2025-04-29 10:01:28'
),
(
    3, 'VINESH', 'KEMIDI', 'vinesh@cmu.com', '9876543206',
    '5914e563d046f963cc694f471354a8effae2cca171927d5782b0db104116d978',
    'customer', 1, 0, '2025-04-29 06:19:07', '2025-04-29 06:19:07'
);



