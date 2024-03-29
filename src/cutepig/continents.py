#!/usr/bin/env python
#-*- coding:utf-8 -*-

# (c) 2011 Christian Holmberg
# This file is part of Pig browser.

# Foobar is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

continents = {
	"AF" : [
		"DZ", "AO", "BJ", "BW", "BF", "BI", "CM", "CV", 
		"CF", "TD", "KM", "CD", "CG", "CI", "DJ", "EG", 
		"GQ", "ER", "ET", "GA", "GM", "GH", "GN", "GW", 
		"KE", "LS", "LR", "LY", "MG", "MW", "ML", "MR", 
		"MU", "YT", "MA", "MZ", "NA", "NE", "NG", "RE", 
		"RW", "SH", "ST", "SN", "SC", "SL", "SO", "ZA", 
		"SD", "SZ", "TZ", "TG", "TN", "UG", "EH", "ZM", 
		"ZW", 
	],
	"NA" : [
		"AI", "AG", "AW", "BS", "BB", "BZ", "BM", "VG", 
		"CA", "KY", "CR", "CU", "DM", "DO", "SV", "GL", 
		"GD", "GP", "GT", "HT", "HN", "JM", "MQ", "MX", 
		"MS", "AN", "NI", "PA", "PR", "BL", "KN", "LC", 
		"MF", "PM", "VC", "TT", "TC", "US", "VI", 
	],
	"OC" : [
		"AS", "AU", "CK", "FJ", "PF", "GU", "KI", "MH", 
		"FM", "NR", "NC", "NZ", "NU", "NF", "MP", "PW", 
		"PG", "PN", "WS", "SB", "TK", "TO", "TV", "UM", 
		"VU", "WF", 
	],
	"AN" : [
		"AQ", "BV", "TF", "HM", "GS", 
	],
	"AS" : [
		"AF", "AM", "AZ", "BH", "BD", "BT", "IO", "BN", 
		"KH", "CN", "CX", "CC", "CY", "GE", "HK", "IN", 
		"ID", "IR", "IQ", "IL", "JP", "JO", "KZ", "KP", 
		"KR", "KW", "KG", "LA", "LB", "MO", "MY", "MV", 
		"MN", "MM", "NP", "OM", "PK", "PS", "PH", "QA", 
		"SA", "SG", "LK", "SY", "TW", "TJ", "TH", "TL", 
		"TR", "TM", "AE", "UZ", "VN", "YE", 
	],
	"EU" : [
		"AX", "AL", "AD", "AT", "BY", "BE", "BA", "BG", 
		"HR", "CZ", "DK", "EE", "FO", "FI", "FR", "DE", 
		"GI", "GR", "GG", "VA", "HU", "IS", "IE", "IM", 
		"IT", "JE", "LV", "LI", "LT", "LU", "MK", "MT", 
		"MD", "MC", "ME", "NL", "NO", "PL", "PT", "RO", 
		"RU", "SM", "RS", "SK", "SI", "ES", "SJ", "SE", 
		"CH", "UA", "GB", 
	],
	"SA" : [
		"AR", "BO", "BR", "CL", "CO", "EC", "FK", "GF", 
		"GY", "PY", "PE", "SR", "UY", "VE", 
	],
}

countries = {
	"BD" : "AS", "BE" : "EU", "BF" : "AF", "BG" : "EU", "BA" : "EU", "BB" : "NA", "WF" : "OC", "BL" : "NA", 
	"BM" : "NA", "BN" : "AS", "BO" : "SA", "BH" : "AS", "BI" : "AF", "BJ" : "AF", "BT" : "AS", "JM" : "NA", 
	"BV" : "AN", "BW" : "AF", "WS" : "OC", "BR" : "SA", "BS" : "NA", "JE" : "EU", "BY" : "EU", "BZ" : "NA", 
	"RU" : "EU", "RW" : "AF", "RS" : "EU", "TL" : "AS", "RE" : "AF", "TM" : "AS", "TJ" : "AS", "RO" : "EU", 
	"TK" : "OC", "GW" : "AF", "GU" : "OC", "GT" : "NA", "GS" : "AN", "GR" : "EU", "GQ" : "AF", "GP" : "NA", 
	"JP" : "AS", "GY" : "SA", "GG" : "EU", "GF" : "SA", "GE" : "AS", "GD" : "NA", "GB" : "EU", "GA" : "AF", 
	"GN" : "AF", "GM" : "AF", "GL" : "NA", "GI" : "EU", "GH" : "AF", "OM" : "AS", "TN" : "AF", "JO" : "AS", 
	"HR" : "EU", "HT" : "NA", "HU" : "EU", "HK" : "AS", "HN" : "NA", "HM" : "AN", "VE" : "SA", "PR" : "NA", 
	"PS" : "AS", "PW" : "OC", "PT" : "EU", "KN" : "NA", "AF" : "AS", "IQ" : "AS", "PA" : "NA", "PF" : "OC", 
	"PG" : "OC", "PE" : "SA", "PK" : "AS", "PH" : "AS", "PN" : "OC", "PL" : "EU", "PM" : "NA", "ZM" : "AF", 
	"EH" : "AF", "EE" : "EU", "EG" : "AF", "ZA" : "AF", "EC" : "SA", "IT" : "EU", "VN" : "AS", "SB" : "OC", 
	"ET" : "AF", "SO" : "AF", "ZW" : "AF", "SA" : "AS", "ES" : "EU", "ER" : "AF", "ME" : "EU", "MD" : "EU", 
	"MG" : "AF", "MF" : "NA", "MA" : "AF", "MC" : "EU", "UZ" : "AS", "MM" : "AS", "ML" : "AF", "MO" : "AS", 
	"MN" : "AS", "MH" : "OC", "MK" : "EU", "MU" : "AF", "MT" : "EU", "MW" : "AF", "MV" : "AS", "MQ" : "NA", 
	"MP" : "OC", "MS" : "NA", "MR" : "AF", "IM" : "EU", "UG" : "AF", "TZ" : "AF", "MY" : "AS", "MX" : "NA", 
	"IL" : "AS", "FR" : "EU", "AW" : "NA", "SH" : "AF", "SJ" : "EU", "FI" : "EU", "FJ" : "OC", "FK" : "SA", 
	"FM" : "OC", "FO" : "EU", "NI" : "NA", "NL" : "EU", "NO" : "EU", "NA" : "AF", "VU" : "OC", "NC" : "OC", 
	"NE" : "AF", "NF" : "OC", "NG" : "AF", "NZ" : "OC", "NP" : "AS", "NR" : "OC", "NU" : "OC", "CK" : "OC", 
	"CI" : "AF", "CH" : "EU", "CO" : "SA", "CN" : "AS", "CM" : "AF", "CL" : "SA", "CC" : "AS", "CA" : "NA", 
	"CG" : "AF", "CF" : "AF", "CD" : "AF", "CZ" : "EU", "CY" : "AS", "CX" : "AS", "CR" : "NA", "PY" : "SA", 
	"CV" : "AF", "CU" : "NA", "SZ" : "AF", "SY" : "AS", "KG" : "AS", "KE" : "AF", "SR" : "SA", "KI" : "OC", 
	"KH" : "AS", "SV" : "NA", "KM" : "AF", "ST" : "AF", "SK" : "EU", "KR" : "AS", "SI" : "EU", "KP" : "AS", 
	"KW" : "AS", "SN" : "AF", "SM" : "EU", "SL" : "AF", "SC" : "AF", "KZ" : "AS", "KY" : "NA", "SG" : "AS", 
	"SE" : "EU", "SD" : "AF", "DO" : "NA", "DM" : "NA", "DJ" : "AF", "DK" : "EU", "DE" : "EU", "YE" : "AS", 
	"DZ" : "AF", "US" : "NA", "UY" : "SA", "YT" : "AF", "UM" : "OC", "LB" : "AS", "LC" : "NA", "LA" : "AS", 
	"TV" : "OC", "TW" : "AS", "TT" : "NA", "TR" : "AS", "LK" : "AS", "LI" : "EU", "LV" : "EU", "TO" : "OC", 
	"LT" : "EU", "LU" : "EU", "LR" : "AF", "LS" : "AF", "TH" : "AS", "TF" : "AN", "TG" : "AF", "TD" : "AF", 
	"TC" : "NA", "LY" : "AF", "VA" : "EU", "VC" : "NA", "AE" : "AS", "AD" : "EU", "AG" : "NA", "VG" : "NA", 
	"AI" : "NA", "VI" : "NA", "IS" : "EU", "IR" : "AS", "AM" : "AS", "AL" : "EU", "AO" : "AF", "AN" : "NA", 
	"AQ" : "AN", "AS" : "OC", "AR" : "SA", "AU" : "OC", "AT" : "EU", "IO" : "AS", "IN" : "AS", "AX" : "EU", 
	"AZ" : "AS", "IE" : "EU", "ID" : "AS", "UA" : "EU", "QA" : "AS", "MZ" : "AF", 
}

# ch : added from makecountrynames.py -> countrynames.py
countrynames = {
	"BD" : "Bangladesh", "BE" : "Belgium", 
	"BF" : "Burkina Faso", "BG" : "Bulgaria", 
	"BA" : "Bosnia and Herzegovina", "BB" : "Barbados", 
	"WF" : "Wallis and Futuna", "BL" : "Saint Barthelemy", 
	"BM" : "Bermuda", "BN" : "Brunei Darussalam", 
	"BO" : "Bolivia", "BH" : "Bahrain", 
	"BI" : "Burundi", "BJ" : "Benin", 
	"BT" : "Bhutan", "JM" : "Jamaica", 
	"BV" : "Bouvet Island", "BW" : "Botswana", 
	"WS" : "Samoa", "BR" : "Brazil", 
	"BS" : "Bahamas", "JE" : "Jersey", 
	"BY" : "Belarus", "BZ" : "Belize", 
	"RU" : "Russian", "RW" : "Rwanda", 
	"RS" : "Serbia", "TL" : "Timor-Leste", 
	"RE" : "Reunion", "TM" : "Turkmenistan", 
	"TJ" : "Tajikistan", "RO" : "Romania", 
	"TK" : "Tokelau", "GW" : "Guinea-Bissau", 
	"GU" : "Guam", "GT" : "Guatemala", 
	"GS" : "South Georgia", "GR" : "Greece", 
	"GQ" : "Equatorial Guinea", "GP" : "Guadeloupe", 
	"JP" : "Japan", "GY" : "Guyana", 
	"GG" : "Guernsey", "GF" : "French Guiana", 
	"GE" : "Georgia", "GD" : "Grenada", 
	"GB" : "UK", "GA" : "Gabon", 
	"GN" : "Guinea", "GM" : "Gambia", 
	"GL" : "Greenland", "GI" : "Gibraltar", 
	"GH" : "Ghana", "OM" : "Oman", 
	"TN" : "Tunisia", "JO" : "Jordan", 
	"HR" : "Croatia", "HT" : "Haiti", 
	"HU" : "Hungary", "HK" : "Hong Kong", 
	"HN" : "Honduras", "HM" : "Heard Island", 
	"VE" : "Venezuela", "PR" : "Puerto Rico", 
	"PS" : "Palestina", "PW" : "Palau", 
	"PT" : "Portugal", "KN" : "Saint Kitts and Nevis", 
	"AF" : "Afghanistan", "IQ" : "Iraq", 
	"PA" : "Panama", "PF" : "French Polynesia", 
	"PG" : "Papua New Guinea", "PE" : "Peru", 
	"PK" : "Pakistan", "PH" : "Philippines", 
	"PN" : "Pitcairn Islands", "PL" : "Poland", 
	"PM" : "Saint Pierre", "ZM" : "Zambia", 
	"EH" : "Western Sahara", "EE" : "Estonia", 
	"EG" : "Egypt", "ZA" : "South Africa", 
	"EC" : "Ecuador", "IT" : "Italy", 
	"VN" : "Vietnam", "SB" : "Solomon Islands", 
	"ET" : "Ethiopia", "SO" : "Somalia", 
	"ZW" : "Zimbabwe", "SA" : "Saudi Arabia", 
	"ES" : "Spain", "ER" : "Eritrea", 
	"ME" : "Montenegro", "MD" : "Moldova", 
	"MG" : "Madagascar", "MF" : "Saint Martin", 
	"MA" : "Morocco", "MC" : "Monaco", 
	"UZ" : "Uzbekistan", "MM" : "Myanmar", 
	"ML" : "Mali", "MO" : "Macao", 
	"MN" : "Mongolia", "MH" : "Marshall Islands", 
	"MK" : "Macedonia", "MU" : "Mauritius", 
	"MT" : "Malta", "MW" : "Malawi", 
	"MV" : "Maldives", "MQ" : "Martinique", 
	"MP" : "Northern Mariana Islands", "MS" : "Montserrat", 
	"MR" : "Mauritania", "IM" : "Isle of Man", 
	"UG" : "Uganda", "TZ" : "Tanzania", 
	"MY" : "Malaysia", "MX" : "Mexico", 
	"IL" : "Israel", "FR" : "France", 
	"AW" : "Aruba", "SH" : "Saint Helena", 
	"SJ" : "Svalbard & Jan Mayen Islands", "FI" : "Finland", 
	"FJ" : "Fiji", "FK" : "Falkland Islands", 
	"FM" : "Micronesia", "FO" : "Faroe Islands", 
	"NI" : "Nicaragua", "NL" : "Netherlands", 
	"NO" : "Norway", "NA" : "Namibia", 
	"VU" : "Vanuatu", "NC" : "New Caledonia", 
	"NE" : "Niger", "NF" : "Norfolk Island", 
	"NG" : "Nigeria", "NZ" : "New Zealand", 
	"NP" : "Nepal", "NR" : "Nauru", 
	"NU" : "Niue", "CK" : "Cook Islands", 
	"CI" : "Cote d'Ivoire", "CH" : "Switzerland", 
	"CO" : "Colombia", "CN" : "China", 
	"CM" : "Cameroon", "CL" : "Chile", 
	"CC" : "Cocos", "CA" : "Canada", 
	"CG" : "Congo", "CF" : "Central African Republic", 
	"CD" : "Congo", "CZ" : "Czech Republic", 
	"CY" : "Cyprus", "CX" : "Christmas Island", 
	"CR" : "Costa Rica", "PY" : "Paraguay", 
	"CV" : "Cape Verde", "CU" : "Cuba", 
	"SZ" : "Swaziland", "SY" : "Syrian Arab Republic", 
	"KG" : "Kyrgyz Republic", "KE" : "Kenya", 
	"SR" : "Suriname", "KI" : "Kiribati", 
	"KH" : "Cambodia", "SV" : "El Salvador", 
	"KM" : "Comoros", "ST" : "Sao Tome and Principe", 
	"SK" : "Slovakia", "KR" : "Korea", 
	"SI" : "Slovenia", "KP" : "Korea", 
	"KW" : "Kuwait", "SN" : "Senegal", 
	"SM" : "San Marino", "SL" : "Sierra Leone", 
	"SC" : "Seychelles", "KZ" : "Kazakhstan", 
	"KY" : "Cayman Islands", "SG" : "Singapore", 
	"SE" : "Sweden", "SD" : "Sudan", 
	"DO" : "Dominican Republic", "DM" : "Dominica", 
	"DJ" : "Djibouti", "DK" : "Denmark", 
	"DE" : "Germany", "YE" : "Yemen", 
	"DZ" : "Algeria", "US" : "USA", 
	"UY" : "Uruguay", "YT" : "Mayotte", 
	"UM" : "United States Minor Outlying Islands", "LB" : "Lebanon", 
	"LC" : "Saint Lucia", "LA" : "Lao People's Democratic Republic", 
	"TV" : "Tuvalu", "TW" : "Taiwan", 
	"TT" : "Trinidad and Tobago", "TR" : "Turkey", 
	"LK" : "Sri Lanka", "LI" : "Liechtenstein", 
	"LV" : "Latvia", "TO" : "Tonga", 
	"LT" : "Lithuania", "LU" : "Luxembourg", 
	"LR" : "Liberia", "LS" : "Lesotho", 
	"TH" : "Thailand", "TF" : "French Southern Territories", 
	"TG" : "Togo", "TD" : "Chad", 
	"TC" : "Turks and Caicos Islands", "LY" : "Libyan Arab Jamahiriya", 
	"VA" : "Holy See", "VC" : "Saint Vincent and the Grenadines", 
	"AE" : "United Arab Emirates", "AD" : "Andorra", 
	"AG" : "Antigua and Barbuda", "VG" : "British Virgin Islands", 
	"AI" : "Anguilla", "VI" : "United States Virgin Islands", 
	"IS" : "Iceland", "IR" : "Iran", 
	"AM" : "Armenia", "AL" : "Albania", 
	"AO" : "Angola", "AN" : "Netherlands Antilles", 
	"AQ" : "Antarctica", "AS" : "American Samoa", 
	"AR" : "Argentina", "AU" : "Australia", 
	"AT" : "Austria", "IO" : "British Indian Ocean Territory", 
	"IN" : "India", "AX" : "Åland Islands", 
	"AZ" : "Azerbaijan", "IE" : "Ireland", 
	"ID" : "Indonesia", "UA" : "Ukraine", 
	"QA" : "Qatar", "MZ" : "Mozambique", 
	
}
