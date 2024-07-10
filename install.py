import subprocess
import os
import dotenv

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

from django.core.management.utils import get_random_secret_key
scrt=get_random_secret_key()
dotenv.set_key('.env', 'SECRET_KEY', scrt)

subprocess.run("docker-compose up --build -d", shell=True, )

command = "docker ps"
result = subprocess.run(command, shell=True, capture_output=True, text=True)

search_string = "socialnet-web"
another_string = "postgres:16"
if search_string and another_string in result.stdout:
    print("Build Success")
else:
    print("Build Failed. Please check the logs for more information.")

def pid():
    if os.name == "nt":
        pid = subprocess.run("docker ps -aqf name=socialnet-web", shell=True, capture_output=True, text=True)
    elif os.name == "posix":
        pid = subprocess.run("docker ps -aqf name=socialnet-web", shell=True, capture_output=True, text=True)
    else:
        print("OS not supported, Contact the developer for more information.")
    return pid.stdout.strip()
cid=pid()
print("web service running with container id=",cid)
ver=subprocess.run(f'docker exec {cid} python --version', shell=True, capture_output=True, text=True)
print(ver.stdout.strip())

subprocess.run(f'docker exec {cid} python manage.py makemigrations', shell=True)
subprocess.run(f'docker exec {cid} python manage.py migrate', shell=True)
subprocess.run(f'docker exec {cid} python manage.py createsuperuser --noinput', shell=True)
