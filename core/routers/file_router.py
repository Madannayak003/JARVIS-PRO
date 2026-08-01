FILES = {

    "create folder":{
        "action":"create_folder"
    },

    "create file":{
        "action":"create_file"
    },

    "zip folder":{
        "action":"zip"
    },

    "extract zip":{
        "action":"extract"
    },

    "recent files":{
        "action":"recent_files"
    },

    "file information":{
        "action":"file_info"
    }

}


def file_route(command):

    if command in FILES:

        return [FILES[command]]

    return None