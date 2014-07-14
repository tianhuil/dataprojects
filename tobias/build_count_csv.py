psql_labels = [ 'math', 'q-bio', 'q-fin', 'stat.', 'math.AG', 'math.AT', 'math.AP', 'math.CT', 'math.CA', \
               'math.CO', 'math.AC', 'math.CV', 'math.DG', \
               'math.DS', 'math.FA', 'math.GM', 'math.GN', 'math.GT', 'math.GR', 'math.HO', 'math.IT', 'math.KT', \
               'math.LO', 'math.MP', 'math.MG', 'math.NT', 'math.NA', 'math.OA', 'math.OC', 'math.PR', 'math.QA', \
               'math.RT', 'math.RA', 'math.SP', 'math.ST', 'math.SG', 'astro-ph', 'gr-qc','hep-ex','hep-lat', \
               'hep-ph','hep-th','quant-ph', 'nucl-ex', 'nucl-th', 'nlin', 'cond-mat', 'math-ph', 'physics']
counts ={}
engine = create_engine('postgresql:///arXivdata')
cnx = engine.raw_connection() 
for item in psql_labels:
    counts[item]= pd.read_sql("SELECT COUNT(1) FROM arxivrand WHERE categories LIKE" + "'" + "%" + item + "%" + "'", cnx)
phys_ct = pd.read_sql("SELECT COUNT(1) FROM arxivrand WHERE categories LIKE '%astro-ph%' OR categories LIKE '%gr-qc%' OR categories LIKE '%hep%' OR categories LIKE '%ph%' OR categories LIKE '%nucl%' OR categories LIKE '%nlin%' OR categories LIKE '%cond-mat%'", cnx)
cs_ct = pd.read_sql("SELECT COUNT(1) FROM arxivrand WHERE categories LIKE '%u''cs%'", cnx)
cnx.close()
counts['u''cs.'] = cs_ct
counts['major_physics'] = phys_ct
for item in counts:
    counts[item]= counts[item]['count'][0]
import csv
with open('labelcounts.csv', 'w') as f:  
    w = csv.DictWriter(f, counts.keys())
    w.writeheader()
    w.writerow(counts)
