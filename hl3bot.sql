
CREATE TABLE IF NOT EXISTS `hl3bot` (
  `PostID` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`PostID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;


CREATE TABLE IF NOT EXISTS `hl3cleanup` (
  `PostID` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`PostID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
