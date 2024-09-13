import json

def read_file(file_name):
    try:
        f=open(file_name, "rb")
        text = f.read().decode(u"utf-8")
        json_out = json.loads(text)
        return json_out
    except Exception as e:
        print("problem in reading file "+file_name+" :"+str(e))
        return None