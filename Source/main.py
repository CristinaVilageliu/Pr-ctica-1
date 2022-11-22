from fcbscraper import fcbscraper
import pandas


femeni = fcbscraper('https://www.fcbarcelona.es/es/entradas/femenino','Futbol_femeni')
df_femeni = fcbscraper.scrap_matches_url(femeni)

masculi = fcbscraper('https://www.fcbarcelona.es/es/entradas/futbol','Futbol_masculi')
df_masculi = fcbscraper.scrap_matches_url(masculi)

atletic = fcbscraper('https://www.fcbarcelona.es/es/entradas/barca-atletic','Futbol_masculi_atletic')
df_atletic = fcbscraper.scrap_matches_url(atletic)

futsal = fcbscraper('https://www.fcbarcelona.es/es/entradas/futbol-sala','Futbol_sala')
df_futsal = fcbscraper.scrap_matches_url(futsal)

basket = fcbscraper('https://www.fcbarcelona.es/es/entradas/baloncesto','Basket')
df_basket = fcbscraper.scrap_matches_url(basket)

balonmano = fcbscraper('https://www.fcbarcelona.es/es/entradas/balonmano','Handbol')
df_balonmano = fcbscraper.scrap_matches_url(balonmano)

hockey = fcbscraper('https://www.fcbarcelona.es/es/entradas/hockey-patines','Hockey_patins')
df_hockey = fcbscraper.scrap_matches_url(hockey)


df = pd.concat([df_femeni, df_mmasculi, df_atletic, df_futsal, df_basket, df_balonmano, df_hockey])
df.to_csv('dataset.csv')

