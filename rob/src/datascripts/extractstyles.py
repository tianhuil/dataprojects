

# scan beer list and extra styles
# export to styles.json

import json

ids = []
with open('data/beers.json', 'r') as bes, open('data/styles.json', 'w') as st:
  for be_j in bes:
    b = json.loads(be_j)
    if b["style_num"] not in ids:
      style = {
        "id": b["style_num"],
        "name": b["style"]
      }
      
      st.write(json.dumps(style) + "\n")
      ids.append(b["style_num"])
