import uuid

def createID(chuoi:str):
    random_Part=uuid.uuid4().hex[:10]
    return f"{chuoi}_{random_Part}"