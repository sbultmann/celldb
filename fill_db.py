from app import db
from app.models import * 
import pandas as pd

def clear_data(session):
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print ('Clear table %s' % table)
        session.execute(table.delete())
    session.commit()

clear_data(db.session)

u = User(username='admin', email='bultmann@bio.lmu.de')
u.set_password('admin')
db.session.add(u)
db.session.commit()

df = pd.read_csv("cellDB_upload_sheets_JK_cell_lines.csv")

print(df.head())

##cell line
for i, r in df.iterrows():
    print(i)
    cl = CellLines(name = df["Name"][i], celltype = df["celltype"][i], tissue = df["tissue"][i],species = df["species"][0])
    db.session.add(cl)
    db.session.flush()
    cl.running_number = "CL"+str(cl.id).zfill(4)

    ##genotype

    g = Genotype(modmethod = str(df["modification_method"][i]), locus= str(df["locus/gene"][i]), tag = str(df["tag"][i]),\
                modtype = str(df["modification type"][i]), mutation = str(df["mutation"][i]),transgene = str(df["transgene"][0]),\
                    resistance = str(df["resistance"][i]), inducible = str(df["inducible"][i]), cell_line = cl)

    db.session.add(g)

    ##cellculture
    def get_date(x):
        x = x.split(".")
        d = date(day=int(x[0]), month = int(x[1]), year=int("20"+x[2]))
        return (d)

    cc = CellCulture(bsl=int(df["biosafety level"][i]), pcrdate=get_date(df["myco PCR date"][i]), \
        culturetype=str(df["culture type"][i]), medium=str(df["medium"][i]), notes = str(str(df["notes"][i])),\
        mycoplasma= str(df["mycoplasma status"][i]), cell_line = cl)

    db.session.add(cc)


    ##generation
    gen = CellLineGeneration(protocol = str(df["protocol for generation"][i]), \
        description = str(df["description"][i]), comments = str(df["comments"][i]), \
            publication= str(df["publication"][i]),cell_line = cl)
    db.session.add(gen)
    ##stocks

    stdf = pd.read_csv('cellDB_upload_sheets_JK_stocks.csv')

    for index, row in stdf[stdf["cell_id"]==df["cell_id"][i]].iterrows():
        st = Stocks(date = get_date(row['date']), freezer = str(row["freezer"]),\
            rack = str(row["rack"]),box = str(row["box"]), position = str(row["position"]),\
                passage = int(row["passage"][1:]),cell_line = cl)
        db.session.add(st)
    db.session.commit()
