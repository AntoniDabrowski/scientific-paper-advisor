from frquestions.models import FromArxivFR, FromArxivAB
import pandas as pd


def populate_FR_database(model, path):
    df = pd.read_csv(path)
    for _, record in df.iterrows():
        if record['further research'] is not None and \
                80 < len(str(record['further research'])) < 1024 and \
                not model.objects.filter(url=record['url']).exists():
            new_record = model(url=record['url'],
                                        x=record['x'],
                                        y=record['y'],
                                        z=record['z'],
                                        category=record['primary category'],
                                        title=record['title'],
                                        hover=record["further research"])
            new_record.save()


def populate_AB_database(path):
    df = pd.read_csv(path)
    for _, record in df.iterrows():
        if record['abstract'] is not None and \
                80 < len(str(record['abstract'])) < 2048 and \
                not FromArxivAB.objects.filter(url=record['url']).exists():
            new_record = FromArxivAB(url=record['url'],
                                        x=record['x'],
                                        y=record['y'],
                                        z=record['z'],
                                        category=record['primary category'],
                                        title=record['title'],
                                        hover=record["abstract"])
            new_record.save()


