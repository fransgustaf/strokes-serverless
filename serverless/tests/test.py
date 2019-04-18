available_paths = ['documentSetting', 'pageSetting', 'fieldSetting', 'recognitionSetting', 'document', 'page', 'field', 'stroke', 'background']

event_path = "/document/123/background/1"



# Get current path
def get_path(path):
    for available_path in available_paths:
        print("checking: {0} for: {1}".format(path, available_path))
        if path.endswith(available_path):
            print("found path: {0}".format(available_path))
            return available_path
    return get_path(path.rsplit('/',1)[0])
        
print(get_path(event_path))
