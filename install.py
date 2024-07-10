import subprocess

subprocess.run("docker-compose up --build -d", shell=True, )

command = "docker ps"
result = subprocess.run(command, shell=True, capture_output=True, text=True)

search_string = "socialnet-web"
another_string = "postgres:16"
if search_string and another_string in result.stdout:
    print("Build Success")
else:
    print("Build Failed. Please check the logs for more information.")

pid = subprocess.run("docker ps -aqf name=socialnet-web", shell=True, capture_output=True, text=True)
cid=pid.stdout.strip()
print(cid)
ver=subprocess.run(f'docker exec {cid} python --version', shell=True, capture_output=True, text=True)
print(ver.stdout.strip())

subprocess.run(f'docker exec {cid} python manage.py makemigrations', shell=True)
subprocess.run(f'docker exec {cid} python manage.py migrate', shell=True)
subprocess.run(f'docker exec {cid} python manage.py createsuperuser --noinput', shell=True)
