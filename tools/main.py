import fnmatch
import json
import os
import subprocess
import tempfile
import shutil
import datetime

import html2text
import requests

tools = {
    "sys.read": {
        "type": "function",
        "function": {
            "name": "sys-read",
            "description": "Reads the contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "description": "The name of the file to read",
                        "type": "string"
                    }
                }
            }
        }
    },
    "sys.write": {
        "type": "function",
        "function": {
            "name": "sys-write",
            "description": "Write the contents to a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "description": "The name of the file to write to",
                        "type": "string"
                    },
                    "content": {
                        "description": "The content to write",
                        "type": "string"
                    }
                }
            }
        }
    },
    "sys.append": {
        "type": "function",
        "function": {
            "name": "sys-append",
            "description": "Appends the contents to a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "description": "The name of the file to append to",
                        "type": "string"
                    },
                    "content": {
                        "description": "The content to append",
                        "type": "string"
                    }
                }
            }
        }
    },
    "sys.http.get": {
        "type": "function",
        "function": {
            "name": "sys-http-get",
            "description": "Download the contents of a http or https URL",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "description": "The URL to download",
                        "type": "string"
                    }
                }
            }
        }
    },
    "sys.http.html2text": {
        "type": "function",
        "function": {
            "name": "sys-http-html2text",
            "description": "Download the contents of a http or https URL returning the content as rendered text converted from HTML",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "description": "The URL to download",
                        "type": "string"
                    }
                }
            }
        }
    },
    "sys.abort": {
        "type": "function",
        "function": {
            "name": "sys-abort",
            "description": "Aborts execution",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "description": "The description of the error or unexpected result that caused abort to be called",
                        "type": "string"
                    }
                }
            }
        }
    },
    "sys.http.post": {
        "type": "function",
        "function": {
            "name": "sys-http-post",
            "description": "Write contents to a http or https URL using the POST method",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "description": "The URL to POST to",
                        "type": "string"
                    },
                    "content": {
                        "description": "The content to POST",
                        "type": "string"
                    },
                    "contentType": {
                        "description": "The \"content type\" of the content such as application/json or text/plain",
                        "type": "string"
                    }
                }
            }
        }
    },
    "sys.find": {
        "type": "function",
        "function": {
            "name": "sys-find",
            "description": "Traverse a directory looking for files that match a pattern in the style of the unix find command",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "description": "The file pattern to look for. The pattern is a traditional unix glob format with * matching any character and ? matching a single character",
                        "type": "string"
                    },
                    "directory": {
                        "description": "The directory to search in. The current directory \".\" will be used as the default if no argument is passed",
                        "type": "string"
                    }
                }
            }
        }
    },
    "sys.exec": {
        "type": "function",
        "function": {
            "name": "sys-exec",
            "description": "Execute a command and get the output of the command",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "description": "The command to run including all applicable arguments",
                        "type": "string"
                    },
                    "directory": {
                        "description": "The directory to use as the current working directory of the command. The current directory \".\" will be used if no argument is passed",
                        "type": "string"
                    }
                }
            }
        }
    },
    "sys.getenv": {
        "type": "function",
        "function": {
            "name": "sys-getenv",
            "description": "Gets the value of an OS environment variable",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "description": "The environment variable name to lookup",
                        "type": "string"
                    }
                }
            }
        }
    },
    "sys.download": {
        "type": "function",
        "function": {
            "name": "sys-download",
            "description": "Downloads a URL, saving the contents to disk at a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "description": "The URL to download, either http or https.",
                        "type": "string"
                    },
                    "location": {
                        "description": "(optional) The on disk location to store the file. If no location is specified a temp location will be used. If the target file already exists it will fail unless override is set to true.",
                        "type": "string"
                    },
                    "override": {
                        "description": "If true and a file at the location exists, the file will be overwritten, otherwise fail. Default is false",
                        "type": "string"
                    }
                }
            }
        }
    },
    "sys.remove": {
        "type": "function",
        "function": {
            "name": "sys-remove",
            "description": "Removes the specified files",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "description": "The file to remove",
                        "type": "string"
                    }
                }
            }
        }
    },
    "sys.stat": {
        "type": "function",
        "function": {
            "name": "sys-stat",
            "description": "Gets size, modfied time, and mode of the specified file",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "description": "The complete path and filename of the file",
                        "type": "string"
                    }
                }
            }
        }
    }
}


def sys_read(input: str):
    params = json.loads(input)
    filename = params["filename"]

    try:
        with open(filename, "r") as f:
            return f.read()
    except Exception as e:
        return str(e)


def sys_write(input: str):
    params = json.loads(input)
    filename = params["filename"]
    content = params["content"]
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    try:
        with open(filename, "w") as f:
            f.write(content)
        return f"Wrote to {filename}"
    except Exception as e:
        return str(e)


def sys_append(input: str):
    params = json.loads(input)
    filename = params["filename"]
    content = params["content"]
    try:
        with open(filename, "a") as f:
            f.write(content)
        return f"Appended content to {filename}"
    except Exception as e:
        return str(e)


def sys_http_get(input: str):
    params = json.loads(input)
    url = params["url"]
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return str(e)


def sys_http_html2text(input: str):
    params = json.loads(input)
    url = params["url"]
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        text = html2text.HTML2Text()
        text.ignore_links = False
        text.bypass_tables = False

        plain_text = text.handle(response.text)

        return plain_text
    except requests.RequestException as e:
        return f"Error fetching URL {url}: {e}"
    except Exception as e:
        return str(e)


def sys_abort(input: str):
    params = json.loads(input)
    message = params["message"]
    raise Exception(f"ABORT: {message}")


def sys_http_post(input: str):
    params = json.loads(input)
    url = params["url"]
    content = params["content"]
    content_type = params.get("contentType", "application/json")

    headers = {'Content-Type': content_type}
    try:
        response = requests.post(url, data=content, headers=headers)
        response.raise_for_status()
        return f"Wrote {len(content)} bytes to {url}"
    except requests.RequestException as e:
        # Return error message in case of a request failure
        return f"Failed to post to {url}: {str(e)}"
    except Exception as e:
        return str(e)


def sys_find(input: str):
    params = json.loads(input)
    directory = params.get("directory", ".")
    pattern = params.get("pattern", "*")

    found_files = []
    for root, dirnames, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames, pattern):
            found_files.append(os.path.join(root, filename))

    return json.dumps(found_files)


def sys_exec(input: str):
    params = json.loads(input)
    command = params["command"]

    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        return {"stdout": result.stdout, "stderr": result.stderr}
    except subprocess.CalledProcessError as e:
        return {"stdout": e.stdout, "stderr": e.stderr, "returncode": e.returncode}


def sys_getenv(input: str):
    params = json.loads(input)
    return os.getenv(params.get("name"), "Variable not found")


def sys_download(input: str):
    params = json.loads(input)
    url = params["url"]
    location = params.get("location", tempfile.mktemp())
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(location, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return f"Downloaded to {location}"
    except Exception as e:
        return str(e)


def sys_remove(input: str):
    params = json.loads(input)
    location = params["location"]
    try:
        if os.path.isdir(location):
            shutil.rmtree(location)
            return f"Removed directory: {location}"
        elif os.path.isfile(location):
            os.remove(location)
            return f"Removed file: {location}"
        else:
            return f"Location not found: {location}"

    except Exception as e:
        return f"Error removing location: {location} - {str(e)}"


def sys_stat(input: str):
    params = json.loads(input)
    filepath = params["filepath"]

    try:
        stat = os.stat(filepath)
        is_dir = os.path.isdir(filepath)
        title = "Directory" if is_dir else "File"
        mod_time = datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()

        stat_info = {
            "title": title,
            "file": filepath,
            "mode": oct(stat.st_mode),
            "size": stat.st_size,
            "modtime": mod_time
        }

        return json.dumps(stat_info, indent=4)
    except Exception as e:
        return str(e)
