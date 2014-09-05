import SNER

text = "President Barack Obama met Fidel Castro at the United Nations in New York."

entities = SNER.get_NEs(text)

print entities
