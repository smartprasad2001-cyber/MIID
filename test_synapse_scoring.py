#!/usr/bin/env python3
"""
Score exact synapse from validator logs using rewards.py
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from MIID.validator.reward import (
    calculate_variation_quality,
    _grade_dob_variations,
    _grade_address_variations,
    MIID_REWARD_WEIGHTS
)


def score_synapse():
    """Score the exact synapse from validator logs."""
    
    print("="*80)
    print("SCORING SYNAPSE - Using rewards.py")
    print("="*80)
    print()
    
    # Exact variations from synapse (from logs)
    variations = {
        'Anatoly Vyborny': [['Anatoly Vyborny', '1965-06-08', '12 Tverskaya Street, Moscow, Moscow Oblast 125009, Russia'], ['Anatoliy Voborny', '1965-06-07', '3 Tverskaya Street, Moscow, Moscow Oblast 125009, Russia'], ['Anatoly Vyb', '1965-06-11', '1 Tverskaya Street, Moscow, Moscow Oblast 125009, Russia'], ['Anatoly Vybarny', '1965-06-13', '5 Tverskaya Street, Moscow, Moscow Oblast 125009, Russia'], ['Anatoliy Vyborni', '1965-06-18', '7 Tverskaya Street, Moscow, Moscow Oblast 125009, Russia'], ['Anatoly Vybunny', '1965-07-08', '9 Tverskaya Street, Moscow, Moscow Oblast 125009, Russia'], ['Anatoly Vybory', '1965-05-08', '11 Tverskaya Street, Moscow, Moscow Oblast 125009, Russia'], ['Anatoly Vybarniy', '1990-06-08', '13 Tverskaya Street, Moscow, Moscow Oblast 125009, Russia'], ['Anatoliy Vybornyy', '1990-06-10', '15 Tverskaya Street, Moscow, Moscow Oblast 125009, Russia'], ['Anatoliy Vyboryny', '1990-05-20', '17 Tverskaya Street, Moscow, Moscow Oblast 125009, Russia'], ['Anatoly Vybarny', '1990-07-15', '19 Tverskaya Street, Moscow, Moscow Oblast 125009, Russia'], ['Anatoly Vybunnyy', '1990-08-15', '21 Tverskaya Street, Moscow, Moscow Oblast 125009, Russia'], ['Anatoliy Vyborniy', '1990-09-15', '23 Tverskaya Street, Moscow, Moscow Oblast 125009, Russia'], ['Anatoly Vyboryy', '1990-05-08', '25 Tverskaya Street, Moscow, Moscow Oblast 125009, Russia'], ['Anatoly Vybarnyy', '1990-04-15', '27 Tverskaya Street, Moscow, Moscow Oblast 125009, Russia']],
        'رشدي مرمش': [['رشدي مرمش', '1956-03-23', '15 Wing Lung Street, Kennedy Town, Hong Kong Island, Hong Kong'], ['رشدي مرمش', '1956-03-24', 'Unit 10, 20-22 Tin Lok Lane, Wan Chai, Hong Kong Island, Hong Kong'], ['رشدي مرمش', '1956-03-22', 'Flat C, 12-14 Kau U Fong, Central, Hong Kong Island, Hong Kong'], ['رشدي مرمش', '1956-04-15', 'Shop 3, 8-10 Hollywood Road, Central, Hong Kong Island, Hong Kong'], ['رشدي مرمش', '1956-02-15', "100 Queen's Road Central, Central, Hong Kong Island, Hong Kong"], ['رشدي مرمش', '1955-03-23', 'G/F, 53-55 Graham Street, Central, Hong Kong Island, Hong Kong'], ['رشدي مرمش', '1957-03-23', '23-25 Jervois Street, Sheung Wan, Hong Kong Island, Hong Kong'], ['رشدي مرمش', '1956-03', '30 Des Voeux Road Central, Central, Hong Kong Island, Hong Kong'], ['رشدي مرمش', '1956-03-23', '120 Connaught Road West, Sai Ying Pun, Hong Kong Island, Hong Kong'], ['رشدي مرمش', '1956-03-23', "Suite 1801, 18/F, 30 Queen's Road, Central, Hong Kong Island, Hong Kong"], ['رشدي مرمش', '1956-03-23', 'Room 702, 7/F, 10 Des Voeux Road Central, Central, Hong Kong Island, Hong Kong'], ['رشدي مرمش', '1956-03-23', '18 Stanley Street, Central, Hong Kong Island, Hong Kong'], ['رشدي مرمش', '1956-03-23', 'Level 12, 100 Nathan Road, Tsim Sha Tsui, Kowloon, Hong Kong'], ['رشدي مرمش', '1956-03-23', '133-135 Wing Lok Street, Sheung Wan, Hong Kong Island, Hong Kong'], ['رشدي مرمش', '1956-03-23', '9-11 Gough Street, Central, Hong Kong Island, Hong Kong']],
        'Leonid Pasechnik': [['Leonid Pasechnik', '1970-03-15', '15 Khreshchatyk Street, Kyiv, Kyiv City 01001, Ukraine'], ['Leonid Pasek', '1970-03-16', '22 Velyka Vasylkivska Street, Kyiv, Kyiv City 01004, Ukraine'], ['Leonid Paschnik', '1970-03-14', '3 Soborna Square, Kyiv, Kyiv City 01021, Ukraine'], ['Leonid V. Pasechnik', '1970-03-01', '4 Andriyivskyy Descent, Podil, Kyiv, Kyiv City 04210, Ukraine'], ['Leonid Pasechnik Jr.', '1970-04-15', '5 vul. Hrushevskoho, Pechersk, Kyiv, Kyiv City 01021, Ukraine'], ['Leonid P. Syechnik', '1970-06-15', '6 Maidan Nezalezhnosti, Pechersk District, Kyiv, Kyiv City 01001, Ukraine'], ['Leonid Pasec', '1971-03-15', '7 vul. Instytutska, Pechersk, Kyiv, Kyiv City 01021, Ukraine'], ['Leonid Pasechny', '1969-03-15', '8 vul. Saksahanskoho, Shevchenkivskyi District, Kyiv, Kyiv City 01032, Ukraine'], ['Leonid Pasichnyk', '1970-01-15', '9 vul. Proreznaya, Shevchenkivskyi District, Kyiv, Kyiv City 01004, Ukraine'], ['Leonid Pasechnek', '1970-03-15', '10 vul. Lva Tolstogo, Shevchenkivskyi District, Kyiv, Kyiv City 01033, Ukraine'], ['Lyenid Pasechnik', '1970-03-15', '11 vul. Velyka Zhytomyrska, Shevchenkivskyi District, Kyiv, Kyiv City 01001, Ukraine'], ['Leonid Pasekny', '1970-03-15', '12 vul. Volodymyrska, Shevchenkivskyi District, Kyiv, Kyiv City 01001, Ukraine'], ['Leonid Paschenik', '1970-03-15', '13 vul. Tereshchenkivska, Shevchenkivskyi District, Kyiv, Kyiv City 01030, Ukraine'], ['Leonid Pasechnyk', '1970-03-15', '14 vul. Khreshchatyk, Pechersk District, Kyiv, Kyiv City 01001, Ukraine'], ['Leonid Pasechnyck', '1970-03-15', '16 vul. Bohdana Khmelnytskoho, Shevchenkivskyi District, Kyiv, Kyiv City 01030, Ukraine']],
        'Aliaksei Rymasheuski': [['Alexei Rymashevsky', '1981-06-28', '12 Nezavisimosti Avenue, Minsk, Minsk Region 220030, Belarus'], ['Alyaxei Rymasheuski', '1981-07-01', '34 Nezavisimosti Avenue, Minsk, Minsk Region 220030, Belarus'], ['Alexey Rimachevsky', '1981-06-29', '56 Nezavisimosti Avenue, Minsk, Minsk Region 220030, Belarus'], ['Aleksei Rymashauski', '1981-06-30', '78 Nezavisimosti Avenue, Minsk, Minsk Region 220030, Belarus'], ['Aliaksei Rymasheuski', '1981-06-29', '10 Nezavisimosti Avenue, Minsk, Minsk Region 220030, Belarus'], ['Alex Rimas', '1981-06-29', '90 Nezavisimosti Avenue, Minsk, Minsk Region 220030, Belarus'], ['A. Rymasheuski', '1981-06-29', '24 Nezavisimosti Avenue, Minsk, Minsk Region 220030, Belarus'], ['Aliaksei R.', '1981-06-29', '45 Nezavisimosti Avenue, Minsk, Minsk Region 220030, Belarus'], ['Alexei Rymashevsky', '1990-05-15', '15 Pervomayskaya Street, Minsk, Minsk Region 220000, Belarus'], ['Alyaxei Rymashauski', '1975-08-10', '25 Nezavisimosti Avenue, Minsk, Minsk Region 220030, Belarus'], ['Alexey Rimachevsky', '1989-04-20', '35 Nezavisimosti Avenue, Minsk, Minsk Region 220030, Belarus'], ['Aleksei Rymasheuski', '1991-05-10', '45 Nezavisimosti Avenue, Minsk, Minsk Region 220030, Belarus'], ['Aliaksei Rymashauski', '1981-06-29', '55 Nezavisimosti Avenue, Minsk, Minsk Region 220030, Belarus'], ['Alexei Rymash', '1981-06-29', '65 Nezavisimosti Avenue, Minsk, Minsk Region 220030, Belarus'], ['Aliaksei Rymasheuski', '1981-06', '75 Nezavisimosti Avenue, Minsk, Minsk Region 220030, Belarus']],
        'denis bonneau': [['Denis Bonneau', '1991-04-17', '15 Avenue Princesse Grace, Monte Carlo, Monaco 98000, Monaco'], ['Denys Bonneau', '1991-04-16', '2 Avenue de la Costa, Monte Carlo, Monaco 98000, Monaco'], ['Deniz Bonneau', '1991-04-18', '3 Boulevard du Larvotto, Monte Carlo, Monaco 98000, Monaco'], ['Denys Bonno', '1991-04-01', '4 Quai Antoine 1er, Port Hercule, Monaco 98000, Monaco'], ['Denis Bonno', '1991-05-16', '5 Place du Casino, Monte Carlo, Monaco 98000, Monaco'], ['Denys Bonneau', '1990-04-17', '6 Rue Princesse Caroline, Monaco-Ville, Monaco 98000, Monaco'], ['Denis Bonneau', '1992-04-17', '7 Avenue Saint-Michel, Monte Carlo, Monaco 98000, Monaco'], ['Denys Bonneau', '1991-03-20', '8 Boulevard Rainier III, Fontvieille, Monaco 98000, Monaco'], ['Denis Bonneau', '1991-06-15', '9 Avenue de la Condamine, Monaco-Ville, Monaco 98000, Monaco'], ['Deniz Bonno', '1989-04-17', '10 Chemin des Sculptures, Jardin Exotique, Monaco 98000, Monaco'], ['Denis Bonneau', '1991-04', '11 Rue de la Poste, Monte Carlo, Monaco 98000, Monaco'], ['Denys Bonneau', '1990-05-14', '12 Avenue des Beaux-Arts, Monte Carlo, Monaco 98000, Monaco'], ['Denis Bonneau', '1991-05-17', '13 Promenade Honoré V, Port Hercule, Monaco 98000, Monaco'], ['Denys Bonneau', '1991-02-28', '14 Rue du Portier, Monte Carlo, Monaco 98000, Monaco'], ['Denis Bonno', '1990-08-10', '15 Avenue Albert II, Fontvieille, Monaco 98000, Monaco']],
        'luce guyon': [['Lucian Guyon', '1998-03-03', '12 Sunset Drive, Providenciales, Turks and Caicos Islands TKCA 1ZZ, Turks and Caicos Islands'], ['Lucienne Guyon', '1995-03-02', '45 Ocean View Road, Grace Bay, Providenciales, Turks and Caicos Islands TKCA 1ZZ, Turks and Caicos Islands'], ['Lucian Guion', '1990-05-14', '78 Bay Road, Leeward, Providenciales, Turks and Caicos Islands TKCA 1ZZ, Turks and Caicos Islands'], ['Lucas Guyon', '1998-02-28', '99 Beachfront Lane, Long Bay, Providenciales, Turks and Caicos Islands TKCA 1ZZ, Turks and Caicos Islands'], ['Lucius Guyon', '1990-06-10', '11 Coral Way, Turtle Cove, Providenciales, Turks and Caicos Islands TKCA 1ZZ, Turks and Caicos Islands'], ['Lucian Guyonne', '1999-03-02', '23 Palm Tree Avenue, Blue Haven, Providenciales, Turks and Caicos Islands TKCA 1ZZ, Turks and Caicos Islands'], ['Luc Guyon', '1998-03-05', '34 Sandy Lane, Discovery Bay, Providenciales, Turks and Caicos Islands TKCA 1ZZ, Turks and Caicos Islands'], ['Lucian Guayon', '1998-05-15', '45 Coconut Grove, Royal Westmoreland, Providenciales, Turks and Caicos Islands TKCA 1ZZ, Turks and Caicos Islands'], ['Lucian Guyon', '1989-07-20', '56 Starfish Court, Sapodilla Bay, Providenciales, Turks and Caicos Islands TKCA 1ZZ, Turks and Caicos Islands'], ['Lucian Guyon', '1990-05', '67 Pelican Drive, Chalk Sound, Providenciales, Turks and Caicos Islands TKCA 1ZZ, Turks and Caicos Islands'], ['Lucian Guyon', '1998-03-01', '78 Sunset Drive, Providenciales, Turks and Caicos Islands TKCA 1ZZ, Turks and Caicos Islands'], ['Lucian Guyon', '1990-08-01', '89 Ocean View Road, Grace Bay, Providenciales, Turks and Caicos Islands TKCA 1ZZ, Turks and Caicos Islands'], ['Lucian Guyon', '1991-05-15', '99 Bay Road, Leeward, Providenciales, Turks and Caicos Islands TKCA 1ZZ, Turks and Caicos Islands'], ['Lucian Guyon', '1998-03-02', '10 Beachfront Lane, Long Bay, Providenciales, Turks and Caicos Islands TKCA 1ZZ, Turks and Caicos Islands'], ['Lucian Guyon', '1990-04-15', '11 Coral Way, Turtle Cove, Providenciales, Turks and Caicos Islands TKCA 1ZZ, Turks and Caicos Islands']],
        'purificación franch': {'variations': [['purificacion franch', '1982-09-09', 'Calle 15 #345, Vedado, Havana 10400, Cuba'], ['purificacion francho', '1982-09-10', 'Avenida 5 #202, Miramar, Havana 11300, Cuba'], ['purificacion franchi', '1982-09-08', 'Calle 23 y L, Plaza de la Revolución, Havana 10400, Cuba'], ['purificacion francha', '1983-09-09', 'Calle 10 #701, El Vedado, Havana 10400, Cuba'], ['purificacion franché', '1981-09-09', 'Calle 23, Vedado, Havana 10400, Cuba'], ['purificacion franch', '1982-09-09', 'Calle 1ra #101, Reparto Cubanacán, Havana 11700, Cuba'], ['purificacion franch', '1982-09-09', 'Calle 44 #315, Playa, Havana 11300, Cuba'], ['purificacion franch', '1982-09-09', 'Calle G #407, Vedado, Havana 10400, Cuba'], ['purificacion franch', '1982-09-09', 'Calle 17 #452, Vedado, Havana 10400, Cuba'], ['purificacion franch', '1982-09-09', 'Calle 21 #110, Vedado, Havana 10400, Cuba'], ['purificacion franch', '1982-09-09', 'Calle 23 #103, Vedado, Havana 10400, Cuba'], ['purificacion franch', '1982-09-09', 'Calle 23 #104, Vedado, Havana 10400, Cuba'], ['purificacion franch', '1982-09-09', 'Calle 23 #105, Vedado, Havana 10400, Cuba'], ['purificacion franch', '1982-09-09', 'Calle 23 #106, Vedado, Havana 10400, Cuba'], ['purificacion franch', '1982-09-09', 'Calle 23 #107, Vedado, Havana 10400, Cuba']], 'uav': {'address': 'Calle 3ra, Vedado, Havana', 'label': 'Missing street number and postal code', 'latitude': 23.1135, 'longitude': -82.3665}},
        'Ilya Buzin': [['Ilya Buzin', '1980-08-20', '15 Tverskaya Street, Moscow, Moscow Oblast 125009, Russia'], ['Ilya Buzin', '1980-08-22', '22 Arbat Street, Moscow, Moscow Oblast 119002, Russia'], ['Ilya Buzin', '1980-08-15', '35 Petrovka Street, Moscow, Moscow Oblast 107031, Russia'], ['Ilya Buzin', '1980-09-20', '10 Nikolskaya Street, Moscow, Moscow Oblast 109012, Russia'], ['Ilya Buzin', '1981-08-21', '42 Bolshaya Nikitskaya Street, Moscow, Moscow Oblast 125009, Russia'], ['Ilya Buzin', '1979-08-21', '55 Tverskaya Street, Moscow, Moscow Oblast 125009, Russia'], ['Ilya Buzin', '1980-05-21', '67 Arbat Street, Moscow, Moscow Oblast 119002, Russia'], ['Ilya Buzin', '1980-11-21', '79 Petrovka Street, Moscow, Moscow Oblast 107031, Russia'], ['Ilya Buzin', '1980-08', '81 Nikolskaya Street, Moscow, Moscow Oblast 109012, Russia'], ['Ilya Buzin', '1980-08-21', '123 Lenina Avenue, Saint Petersburg, Saint Petersburg 190000, Russia'], ['Ilya Buzin', '1980-08-21', '45 Nevsky Prospect, Saint Petersburg, Saint Petersburg 191025, Russia'], ['Ilya Buzin', '1980-08-21', '78 Sadovaya Street, Saint Petersburg, Saint Petersburg 191025, Russia'], ['Ilya Buzin', '1980-08-21', '101 Rubinsteina Street, Saint Petersburg, Saint Petersburg 191025, Russia'], ['Ilya Buzin', '1980-08-21', '134 Fontanka River Embankment, Saint Petersburg, Saint Petersburg 191025, Russia'], ['Ilya Buzin', '1980-08-21', '167 Griboyedov Canal Embankment, Saint Petersburg, Saint Petersburg 191025, Russia']],
        'thibaut marchal': [['Thibault Marchal', '1995-09-26', 'Rua da Alegria 15, Porto, Porto 4000-013, Portugal'], ['Thibaud Marchal', '1995-09-24', 'Avenida dos Aliados 30, Porto, Porto 4000-044, Portugal'], ['Thibaut Marchaux', '1995-10-01', 'Rua de Santa Catarina 200, Porto, Porto 4000-440, Portugal'], ['Thibaut Marchallet', '1995-08-25', 'Praça da Liberdade 50, Porto, Porto 4000-324, Portugal'], ['Thibaut Marchel', '1996-09-25', 'Rua das Flores 12, Porto, Porto 4050-480, Portugal'], ['Thibaut Marchall', '1994-09-25', 'Largo de São Francisco 10, Porto, Porto 4000-001, Portugal'], ['Thibaut Marcal', '1995-09-15', 'Rua de Mouzinho da Silveira 18, Porto, Porto 4050-001, Portugal'], ['Thibaut Marchal', '1995-06-25', 'Rua da Ribeira Negra 7, Porto, Porto 4050-510, Portugal'], ['Thibaut Marchal', '1995-09-25', 'Cais da Ribeira 1, Porto, Porto 4050-510, Portugal'], ['Thibaut Marchal', '1993-09-25', 'Rua do Infante D. Henrique 25, Porto, Porto 4050-297, Portugal'], ['Thibaut Marchal', '1995-05-25', 'Rua das Taipas 8, Porto, Porto 4000-528, Portugal'], ['Thibaut Marchal', '1995-09-25', 'Rua de D. Manuel II, Palácio de Cristal, Porto, Porto 4000-324, Portugal'], ['Thibaut Marchal', '1995-09-25', 'Avenida dos Aliados, Edifício Câmara Municipal, Porto, Porto 4000-440, Portugal'], ['Thibaut Marchal', '1995-09-25', 'Rua da Madeira 14, Porto, Porto 4000-400, Portugal'], ['Thibaut Marchal', '1995-09-25', 'Travessa da Rua das Flores 1, Porto, Porto 4050-480, Portugal']],
        'éric lebrun': [['eric lebrun', '1946-05-16', '15 Ratu Sukuna Road, Suva Central, Suva, Central Division 1700, Fiji'], ['eric lebrun', '1946-05-14', '20 Victoria Parade, Suva, Suva City, Central Division 1700, Fiji'], ['eric lebrun', '1946-05-01', '35 Gordon Street, Suva Central, Suva, Central Division 1700, Fiji'], ['eric lebrun', '1946-06-15', '50 Waimanu Road, Samabula, Suva, Central Division 1700, Fiji'], ['eric lebrun', '1946-02-15', '75 Renwick Road, Suva, Suva City, Central Division 1700, Fiji'], ['eric lebrun', '1945-05-15', '90 Marks Street, Suva Central, Suva, Central Division 1700, Fiji'], ['eric lebrun', '1947-05-15', '105 Princes Road, Samabula, Suva, Central Division 1700, Fiji'], ['eric lebrun', '1946-05-15', '120 Foster Road, Suva, Suva City, Central Division 1700, Fiji'], ['eric lebrun', '1946-05-15', '135 Butt Street, Suva Central, Suva, Central Division 1700, Fiji'], ['eric lebrun', '1946-05-15', '150 Cumming Street, Suva, Suva City, Central Division 1700, Fiji'], ['eric lebrun', '1946-05-15', '165 Carpenter Street, Suva Central, Suva, Central Division 1700, Fiji'], ['eric lebrun', '1946-05-15', "180 St. George's Parade, Suva, Suva City, Central Division 1700, Fiji"], ['eric lebrun', '1946-05-15', '195 Thomson Street, Suva Central, Suva, Central Division 1700, Fiji'], ['eric lebrun', '1946-05-15', '200 Loftus Street, Suva, Suva City, Central Division 1700, Fiji'], ['eric lebrun', '1946-05-15', '215 Victoria Parade, Suva Central, Suva, Central Division 1700, Fiji']],
        'zoé joseph': [['Zoe Joseph', '1979-08-09', '123 Sukhumvit Road, Khlong Toei, Bangkok 10110, Thailand'], ['Zoe Joseph', '1979-08-05', '456 Silom Road, Bang Rak, Bangkok 10500, Thailand'], ['Zoe Joseph', '1979-07-09', '789 Sathorn North Road, Khlong Toei, Bangkok 10110, Thailand'], ['Zoe Joseph', '1979-05-09', '101 Wireless Road, Lumphini, Bangkok 10330, Thailand'], ['Zoe Joseph', '1980-08-08', '202 Rama IV Road, Khlong Toei, Bangkok 10110, Thailand'], ['Zoe Joseph', '1978-08-08', '303 Charoen Krung Road, Bang Rak, Bangkok 10500, Thailand'], ['Zoe Joseph', '1979-08-08', '404 Phaya Thai Road, Ratchathewi, Bangkok 10400, Thailand'], ['Zoe Joseph', '1979-08-08', '505 Lat Phrao Road, Lat Phrao, Bangkok 10230, Thailand'], ['Zoe Joseph', '1979-08-08', '606 Phetchaburi Road, Ratchathewi, Bangkok 10400, Thailand'], ['Zoe Joseph', '1979-08-08', '707 Ramkhamhaeng Road, Huai Khwang, Bangkok 10310, Thailand'], ['Zoe Joseph', '1979-08-08', '808 Vibhavadi Rangsit Road, Din Daeng, Bangkok 10400, Thailand'], ['Zoe Joseph', '1979-08-08', '909 Ratchadaphisek Road, Huai Khwang, Bangkok 10310, Thailand'], ['Zoe Joseph', '1979-08-08', '1010 Asok Montri Road, Khlong Toei Nuea, Bangkok 10110, Thailand'], ['Zoe Joseph', '1979-08-08', '1111 Thong Lo Road, Khlong Tan Nuea, Bangkok 10110, Thailand'], ['Zoe Joseph', '1979-08-08', '1212 Ekkamai Road, Khlong Tan Nuea, Bangkok 10110, Thailand']],
        'ягода пачаръзка': [['ягода пачаръзка', '1994-09-25', '6 Оборище, София, София 1000, България'], ['ягода пачаръзка', '1994-09-27', '12 бул. Витоша, София, София 1000, България'], ['ягода пачаръзка', '1994-09-16', '3 Граф Игнатиев, София, София 1000, България'], ['ягода пачаръзка', '1994-11-20', '10 Сан Стефано, София, София 1000, България'], ['ягода пачаръзка', '1993-09-26', '15 Патриарх Евтимий, София, София 1000, България'], ['ягода пачаръзка', '1995-09-26', '7 Шипка, София, София 1000, България'], ['ягода пачаръзка', '1994-09', '17 Цар Иван Шишман, София, София 1000, България'], ['ягодка пачаръзка', '1994-09-26', '9 Московска, София, София 1000, България'], ['ягода пачарька', '1994-09-26', '5 Алабин, София, София 1000, България'], ['ягода пачаръзка', '1990-05-14', '21 Славянска, София, София 1000, България'], ['ягода пачаръзка', '1990-05-16', '19 Гурко, София, София 1000, България'], ['ягода пачаръзка', '1990-06-10', '25 Сердика, София, София 1000, България'], ['ягода пачаръзка', '1990-08-01', '29 Солунска, София, София 1000, България'], ['ягода пачаръзка', '1989-07-20', '11 Леге, София, София 1000, България'], ['ягода пачаръзка', '1994-05-26', '13 Хан Крум, София, София 1000, България']],
        'cesar taylor': [['Cesar Taylorson', '1928-07-25', '24 Juba Road, Juba City, Central Equatoria 10001, South Sudan'], ['Cesar Taylors', '1928-07-27', '18 Katur Street, Juba City, Central Equatoria 10002, South Sudan'], ['Cesare Taylor', '1928-07-10', '36 Nile Avenue, Juba City, Central Equatoria 10003, South Sudan'], ['Cesar Teylor', '1928-08-15', '50 Church Road, Juba City, Central Equatoria 10004, South Sudan'], ['Cesar Taylour', '1928-06-01', '12 Market Square, Juba City, Central Equatoria 10005, South Sudan'], ['Caesar Taylor', '1927-07-26', '7 Main Street, Juba City, Central Equatoria 10006, South Sudan'], ['Cesar Taylər', '1929-07-26', '30 University Drive, Juba City, Central Equatoria 10007, South Sudan'], ['Cesar Taylor Jr.', '1928-05-20', '8 Government Road, Juba City, Central Equatoria 10008, South Sudan'], ['Cesar Taylor Sr.', '1928-10-01', '42 Freedom Plaza, Juba City, Central Equatoria 10009, South Sudan'], ['Cesar Teylors', '1928-07-26', '16 Airport Road, Juba City, Central Equatoria 10010, South Sudan'], ['Cesar Teylorr', '1928-07-26', '22 Industrial Zone, Juba City, Central Equatoria 10011, South Sudan'], ['Cesar Taylör', '1928-07-26', '38 Residential Area, Juba City, Central Equatoria 10012, South Sudan'], ['Cesar Tayloer', '1928-07-26', '10 Hospital Street, Juba City, Central Equatoria 10013, South Sudan'], ['Cesar Taylorr', '1928-07-26', '28 Commercial Avenue, Juba City, Central Equatoria 10014, South Sudan'], ['Cesar Teylorr Jr.', '1928-07-26', '14 Peace Boulevard, Juba City, Central Equatoria 10015, South Sudan']],
        'Володимир Бандура': [['Володимир Бандура', '1990-07-15', 'вул. Хрещатик, 25, Київ, Київська область 01001, Україна'], ['Володимир Бандура', '1990-07-14', 'вул. Хрещатик, 25, Київ, Київська область 01001, Україна'], ['Володимир Бандура', '1990-07-16', 'вул. Хрещатик, 25, Київ, Київська область 01001, Україна'], ['Володимир Бандура', '1990-07-01', 'просп. Перемоги, 100, Київ, Київська область 03062, Україна'], ['Володимир Бандура', '1990-08-14', 'просп. Перемоги, 100, Київ, Київська область 03062, Україна'], ['Володимир Бандура', '1990-05-15', 'вул. Шолом-Алейхема, 5, Київ, Київська область 02002, Україна'], ['Володимир Бандура', '1989-07-15', 'вул. Шолом-Алейхема, 5, Київ, Київська область 02002, Україна'], ['Володимир Бандура', '1991-07-15', 'бульв. Лесі Українки, 20, Київ, Київська область 01133, Україна'], ['Володимир Бандура', '1990-07', 'бульв. Лесі Українки, 20, Київ, Київська область 01133, Україна'], ['Володимир Бандура', '1985-03-20', 'вул. Велика Васильківська, 12, Київ, Київська область 01004, Україна'], ['Володимир Бандура', '2000-12-25', 'вул. Велика Васильківська, 12, Київ, Київська область 01004, Україна'], ['Володимир Бандура', '1995-11-01', 'вул. Жилянська, 45, Київ, Київська область 01033, Україна'], ['Володимир Бандура', '1988-01-10', 'вул. Жилянська, 45, Київ, Київська область 01033, Україна'], ['Володимир Бандура', '1992-09-22', 'вул. Саксаганського, 115, Київ, Київська область 01032, Україна'], ['Володимир Бандура', '1998-04-05', 'вул. Саксаганського, 115, Київ, Київська область 01032, Україна']],
        'alfred boulay': [['Alfred Boulay', '1943-10-23', '15 Rue du Commerce, Abidjan Cocody, Abidjan 01 BP 1234, Ivory Coast'], ['Alfred Boulais', '1943-10-24', '23 Avenue Houphouët-Boigny, Abidjan Plateau, Abidjan 01 BP 5678, Ivory Coast'], ['Alfred Boulai', '1943-10-20', "47 Boulevard Valéry Giscard d'Estaing, Abidjan Treichville, Abidjan 01 BP 9012, Ivory Coast"], ['Alfred Boulle', '1943-11-23', '68 Rue Léopold Sédar Senghor, Abidjan Marcory, Abidjan 01 BP 3456, Ivory Coast'], ['Alfred Boullay', '1943-07-23', '81 Avenue Jean-Paul II, Abidjan Yopougon, Abidjan 01 BP 7890, Ivory Coast'], ['Alfread Boulay', '1944-10-23', '99 Rue des Jardins, Abidjan Cocody, Abidjan 01 BP 2345, Ivory Coast'], ['Alfred Buley', '1942-10-23', '11 Boulevard du Général de Gaulle, Abidjan Plateau, Abidjan 01 BP 6789, Ivory Coast'], ['Alfred Bouley', '1943-10-23', '33 Rue du Port, Abidjan Treichville, Abidjan 01 BP 0123, Ivory Coast'], ['Alfred Boulaye', '1943-04-23', '55 Avenue de la Paix, Abidjan Marcory, Abidjan 01 BP 4567, Ivory Coast'], ['Alfred Boulay', '1943-01-01', '77 Rue du Canal, Abidjan Yopougon, Abidjan 01 BP 8901, Ivory Coast'], ['Alfred Boulay', '1943-12-31', '91 Rue des Étoiles, Abidjan Cocody, Abidjan 01 BP 2345, Ivory Coast'], ['Alfred Boulay', '1943-05-15', '101 Avenue des Arbres, Abidjan Plateau, Abidjan 01 BP 6789, Ivory Coast'], ['Alfred Boulay', '1943-02-15', '111 Boulevard de la République, Abidjan Treichville, Abidjan 01 BP 0123, Ivory Coast'], ['Alfred Boulay', '1943-08-15', '121 Rue de la Liberté, Abidjan Marcory, Abidjan 01 BP 4567, Ivory Coast'], ['Alfred Boulay', '1943-10', '131 Avenue de la Nation, Abidjan Yopougon, Abidjan 01 BP 8901, Ivory Coast']]
    }
    
    # Seed data
    seed_names = list(variations.keys())
    seed_dob = ["1965-6-8", "1956-03-23", "1970-3-15", "1981-6-29", "1991-04-17", "1998-03-02", "1982-09-09", "1980-8-21", "1995-09-25", "1946-05-15", "1979-08-08", "1994-09-26", "1928-07-26", "1990-7-15", "1943-10-23"]
    seed_addresses = ["Russia", "Hong Kong", "Ukraine", "Belarus", "Monaco", "Turks and Caicos Islands", "Cuba", "Russia", "Portugal", "Fiji", "Thailand", "Bulgaria", "South Sudan", "Ukraine", "Ivory Coast"]
    
    # Query requirements
    phonetic_sim = {"Light": 0.2, "Medium": 0.6, "Far": 0.2}
    ortho_sim = {"Light": 0.3, "Medium": 0.4, "Far": 0.3}
    rule_based = {
        "selected_rules": ["shorten_name_to_initials", "swap_random_letter"],
        "rule_percentage": 60
    }
    variation_count = 8
    
    print(f"Scoring {len(seed_names)} names...")
    print()
    
    validator_uid = 1
    miner_uid = 1
    miner_metrics = {}
    
    total_name_score = 0.0
    total_dob_score = 0.0
    total_address_score = 0.0
    
    detailed_scores = {}
    
    # Score each name
    for i, name in enumerate(seed_names):
        if name not in variations:
            continue
        
        # Handle UAV format
        if isinstance(variations[name], dict) and 'variations' in variations[name]:
            variations_list = variations[name]['variations']
        else:
            variations_list = variations[name]
        
        if not variations_list:
            continue
        
        variations_dict = {name: variations_list}
        name_variations = [var[0].lower() if var[0] else "" for var in variations_list if len(var) > 0]
        
        # Name scoring
        name_quality, base_score, name_metrics = calculate_variation_quality(
            original_name=name,
            variations=name_variations,
            phonetic_similarity=phonetic_sim,
            orthographic_similarity=ortho_sim,
            expected_count=variation_count,
            rule_based=rule_based
        )
        
        # DOB scoring
        dob_result = _grade_dob_variations(variations_dict, [seed_dob[i]], miner_metrics)
        dob_score = dob_result.get("overall_score", 0.0)
        
        # Address scoring
        address_result = _grade_address_variations(
            variations_dict,
            [seed_addresses[i]],
            miner_metrics,
            validator_uid,
            miner_uid
        )
        address_score = address_result.get("overall_score", 0.0)
        
        total_name_score += name_quality
        total_dob_score += dob_score
        total_address_score += address_score
        
        detailed_scores[name] = {
            "name_quality": name_quality,
            "dob_score": dob_score,
            "address_score": address_score,
            "name_metrics": name_metrics
        }
        
        print(f"[{i+1}/{len(seed_names)}] {name[:30]:<30} | Name: {name_quality:.4f} | DOB: {dob_score:.4f} | Addr: {address_score:.4f}")
    
    # Calculate averages
    num_names = len([n for n in seed_names if n in variations and variations[n]])
    if num_names > 0:
        avg_name_score = total_name_score / num_names
        avg_dob_score = total_dob_score / num_names
        avg_address_score = total_address_score / num_names
    else:
        avg_name_score = 0.0
        avg_dob_score = 0.0
        avg_address_score = 0.0
    
    # Final score calculation
    name_component = avg_name_score * 0.2
    dob_component = avg_dob_score * 0.1
    address_component = avg_address_score * 0.7
    final_score = name_component + dob_component + address_component
    
    print()
    print("="*80)
    print("FINAL SCORE SUMMARY")
    print("="*80)
    print()
    print(f"Names Processed: {num_names}/15")
    print()
    print(f"Average Name Quality: {avg_name_score:.4f}")
    print(f"Average DOB Score: {avg_dob_score:.4f}")
    print(f"Average Address Score: {avg_address_score:.4f}")
    print()
    print(f"Name Component (20%):  {name_component:.4f}")
    print(f"DOB Component (10%):   {dob_component:.4f}")
    print(f"Address Component (70%): {address_component:.4f}")
    print(f"{'='*80}")
    print(f"FINAL SCORE: {final_score:.4f}")
    print(f"{'='*80}")
    print()
    
    # Save results
    results = {
        "scores": {
            "avg_name_quality": avg_name_score,
            "avg_dob_score": avg_dob_score,
            "avg_address_score": avg_address_score,
            "name_component": name_component,
            "dob_component": dob_component,
            "address_component": address_component,
            "final_score": final_score
        },
        "detailed_scores": detailed_scores
    }
    
    with open("test_synapse_scoring_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Results saved to: test_synapse_scoring_results.json")
    
    return final_score


if __name__ == "__main__":
    score = score_synapse()
    print(f"\n{'✅ PASS' if score >= 0.8 else '❌ FAIL'}: Final Score = {score:.4f} (Target: 0.8)")

