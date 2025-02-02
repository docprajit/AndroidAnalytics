--
-- DROP USER and DATABASE
--

DROP USER `googleplaystore`@`%`;
DROP DATABASE IF EXISTS `googleplaystore`;

-- --------------------------------------------------------

--
-- User: `googleplaystore`
--

CREATE USER `googleplaystore`@`%` IDENTIFIED BY 'password';

-- --------------------------------------------------------

--
-- Database: `googleplaystore`
--

CREATE DATABASE IF NOT EXISTS `googleplaystore` DEFAULT CHARACTER SET utf8;
GRANT ALL PRIVILEGES ON `googleplaystore`.* TO `googleplaystore`@`%`;
GRANT ALL PRIVILEGES ON `googleplaystore\_%`.* TO `googleplaystore`@`%`;
FLUSH PRIVILEGES;
USE `googleplaystore`;

-- --------------------------------------------------------

--
-- Table structure for table `appurls`
-- privacy_grade_data 0 - data not collected, 1 - data collected, 2 - no data found
--

CREATE TABLE IF NOT EXISTS `appurls`(
  `id` int(10) unsigned PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `app_pkg_name` text(750) NOT NULL,
  `app_url` text(1000) NOT NULL,
  `urls_extracted` int(1) NOT NULL DEFAULT 0,
  `parsed` int(1) NOT NULL DEFAULT 0,
  `parsed_privacy_grade` int(1) NOT NULL DEFAULT 0,
  `downloaded` int(1) NOT NULL DEFAULT 0,
  `perm_extracted` int(1) NOT NULL DEFAULT 0,
  `playdrone_metadata_url` text(1000) NOT NULL,
  `playdrone_apk_url` text(1000) NOT NULL,
  `privacy_grade_url` text(1000) NOT NULL,
  `dt_modified` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8;

-- --------------------------------------------------------

--
-- Indexes for table `appurls`
--
ALTER TABLE `appurls` 
	ADD UNIQUE KEY `app_pkg_name` (`app_pkg_name`(255)),
	ADD KEY `urls_extracted_idx` (`urls_extracted`),
  ADD KEY `parsed_idx` (`parsed`),
  ADD KEY `perm_extracted_idx` (`perm_extracted`),
	ADD KEY `downloaded_idx` (`downloaded`);

-- --------------------------------------------------------

--
-- Table structure for table `appcategories`
--

CREATE TABLE IF NOT EXISTS `appcategories`(
  `id` int(10) unsigned PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `url` varchar(250) NOT NULL,
  `dt_modified` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8;

-- --------------------------------------------------------

--
-- Indexes for table `appcategories`
--
ALTER TABLE `appcategories` 
  ADD KEY `name_idx` (`name`),
  ADD UNIQUE KEY `url_idx` (`url`(250));

-- --------------------------------------------------------

--
-- Table structure for table `permissionGroups`
--

CREATE TABLE IF NOT EXISTS `permissionGroups`(
  `id` int(10) unsigned PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `name` text(500) NOT NULL,
  `priority` int(10) unsigned NOT NULL,
  `dt_modified` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8;

-- --------------------------------------------------------

--
-- Indexes for table `permissionGroups`
--
ALTER TABLE `permissionGroups` 
  ADD UNIQUE KEY `name_idx` (`name`(255));

-- --------------------------------------------------------
--
-- Table structure for table `permissions`
--

CREATE TABLE IF NOT EXISTS `permissions`(
  `id` int(10) unsigned PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `name` text(500) NOT NULL,
  `protection_level` varchar(200),
  `permission_group_id` int(10) unsigned NOT NULL,
  `permission_flags` text(500),
  `dt_modified` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `fk_perm_grp_id` FOREIGN KEY (`permission_group_id`) REFERENCES `permissionGroups`(`id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8;

-- --------------------------------------------------------

--
-- Indexes for table `permissions`
--
ALTER TABLE `permissions` 
  ADD UNIQUE KEY `name_idx` (`name`(255)),
  ADD KEY `protection_level_idx` (`protection_level`);

-- --------------------------------------------------------

--
-- Table structure for table `broadcasts`
--

CREATE TABLE IF NOT EXISTS `broadcasts`(
  `id` int(10) unsigned PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `name` text(500) NOT NULL,
  `dt_modified` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8;

-- --------------------------------------------------------

--
-- Indexes for table `broadcasts`
--
ALTER TABLE `broadcasts` 
  ADD UNIQUE KEY `name_idx` (`name`(255));

-- --------------------------------------------------------
--
-- Table structure for table `developer`
--

CREATE TABLE IF NOT EXISTS `developer`(
  `id` int(10) unsigned PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `name` text(500) NOT NULL,
  `website` text(500),
  `email` text(500),
  `country` text(1000),
  `dt_modified` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8;

-- --------------------------------------------------------

--
-- Indexes for table `developer`
--
ALTER TABLE `developer` 
  ADD UNIQUE KEY `name_idx` (`name`(255));

-- --------------------------------------------------------

--
-- Table structure for table `appdata`
--

CREATE TABLE IF NOT EXISTS `appdata`(
  `id` int(10) unsigned PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `app_pkg_name` text(750) NOT NULL,
  `app_name` text(750) NOT NULL,
  `developer_id` int(10) unsigned NOT NULL,
  `app_category_id` int(10) unsigned NOT NULL,
  `review_rating` decimal(2,1) NOT NULL DEFAULT '0.0',
  `review_count` int(10) NOT NULL DEFAULT '0',
  `desc` text(65535) DEFAULT NULL,
  `whats_new` text(65535),
  `updated` date NOT NULL,
  `installs` int(10) DEFAULT '0',
  `version` varchar(50) DEFAULT NULL,
  `android_reqd` varchar(50) DEFAULT NULL,
  `content_rating` varchar(100) DEFAULT NULL,
  `paid` int(1) NOT NULL DEFAULT '0',
  `dt_modified` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `still_in_googleplaystore` int(1) NOT NULL DEFAULT '1',
  CONSTRAINT `fk_developer_id` FOREIGN KEY (`developer_id`) REFERENCES `developer`(`id`) ON UPDATE CASCADE,
  CONSTRAINT `fk_app_category_id` FOREIGN KEY (`app_category_id`) REFERENCES `appcategories`(`id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8;

-- --------------------------------------------------------

--
-- Indexes for table `appdata`
--
ALTER TABLE `appdata` 
  ADD UNIQUE KEY `app_data_pkg_name_idx` (`app_pkg_name`(255)),
  ADD KEY `dev_id_idx` (`developer_id`),
  ADD KEY `app_cat_id_idx` (`app_category_id`),
  ADD KEY `content_rating_idx` (`content_rating`);

-- --------------------------------------------------------

--
-- Table structure for table `appperm`
--

CREATE TABLE IF NOT EXISTS `appperm`(
  `app_id` int(10) unsigned NOT NULL,
  `perm_id` int(10) unsigned NOT NULL,
  `dt_modified` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT pk_apperm PRIMARY KEY (app_id,perm_id),
  CONSTRAINT `fk_app_id` FOREIGN KEY (`app_id`) REFERENCES `appdata`(`id`) ON UPDATE CASCADE,
  CONSTRAINT `fk_perm_id` FOREIGN KEY (`perm_id`) REFERENCES `permissions`(`id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8;

-- --------------------------------------------------------

--
-- Indexes for table `appperm`
--
ALTER TABLE `appperm` 
  ADD KEY `app_id_name` (`app_id`),
  ADD KEY `perm_id_idx` (`perm_id`);

-- --------------------------------------------------------

--
-- Table structure for table `policy`
--

CREATE TABLE IF NOT EXISTS `policy` (
  `id` int(10) unsigned PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `app_pkg_name` text(750) NOT NULL,
  `review_rating` decimal(2,1) NOT NULL DEFAULT '0.0',
  `review_count` int(10) NOT NULL DEFAULT '0',
  `google_play_category` varchar(100) NOT NULL,
  `annotated_category` varchar(100) DEFAULT 'unknown',
  `accounts` double NOT NULL DEFAULT '0',
  `browser` double NOT NULL DEFAULT '0',
  `calendar` double NOT NULL DEFAULT '0',
  `calling` double NOT NULL DEFAULT '0',
  `clipboard` double NOT NULL DEFAULT '0',
  `contacts` double NOT NULL DEFAULT '0',
  `dict` double NOT NULL DEFAULT '0',
  `email` double NOT NULL DEFAULT '0',
  `identification` double NOT NULL DEFAULT '0',
  `internet` double NOT NULL DEFAULT '0',
  `ipc` double NOT NULL DEFAULT '0',
  `location` double NOT NULL DEFAULT '0',
  `media` double NOT NULL DEFAULT '0',
  `messages` double NOT NULL DEFAULT '0',
  `network` double NOT NULL DEFAULT '0',
  `nfc` double NOT NULL DEFAULT '0',
  `notifications` double NOT NULL DEFAULT '0',
  `overlay` double NOT NULL DEFAULT '0',
  `phone` double NOT NULL DEFAULT '0',
  `sensors` double NOT NULL DEFAULT '0',
  `shell` double NOT NULL DEFAULT '0',
  `storage` double NOT NULL DEFAULT '0',
  `system` double NOT NULL DEFAULT '0',
  `webview` double NOT NULL DEFAULT '0',
  `dt_modified` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Indexes for table `annotations`
--
ALTER TABLE `policy` ADD UNIQUE KEY `policy_app_pkg_name_idx` (`app_pkg_name`(255));

-- --------------------------------------------------------

--
-- Table structure for table `annotations`
--

CREATE TABLE IF NOT EXISTS `annotations` (
  `id` int(10) unsigned PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `app_pkg_name` text(750) NOT NULL,
  `google_play_category` varchar(100) NOT NULL,
  `annotated_category` varchar(100) DEFAULT 'unknown',
  `dt_modified` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Indexes for table `annotations`
--
ALTER TABLE `annotations` ADD UNIQUE KEY `annotations_app_pkg_name_idx` (`app_pkg_name`(255));
