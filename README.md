### Backend Deployment
- clone the repo
- sitch to backend
- install the dependyncies
  ```
  sudo yum update -y
  sudo  yum install python3-pip -y
  sudo yum install git -y
  sudo dnf install mariadb105-server -y
  ```
- change the rds detils in ```app.py```
## Initilize the rds databse
```
mysql -h <rds-endpoint> -u admin -p<password> < test.sql   # change your detiils
mysql -h microservices.cuk1or8kdbv9.us-east-1.rds.amazonaws.com -u admin -pCloud123 < test.sql    # this  example commnd chnage values according to  your  end
```
- change the rds details inn app.py
- create the environnmnet in server for python applicationn deploymnet
```
python3 -m venv venv
source venv/bin/activate
```
- Install requriments.txt
```
pip install -r requirements.txt
```
# crete systemd service  for  backend python
```
sudo vi /etc/systemd/system/microapp.service

```
Paste the below script and change the project paths according to your cloning path
```
[Unit]
Description=Microapp Flask Application
After=network.target

[Service]
User=root
WorkingDirectory=/root/aws-ecommerce-otp-authentication/backend
Environment="PATH=/root/aws-ecommerce-otp-authentication/backend/venv/bin"
ExecStart=/root/aws-ecommerce-otp-authentication/backend/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target

```
### Start the sytemd
```
sudo systemctl daemon-reload
sudo systemctl restart microapp
sudo systemctl status microapp
```

### Frontend Deployment

- clone the repo
- sitch to frontend
- install the dependyncies

```
sudo yum update -y
sudo yum install git -y
sudo  yum install nginx -y
sudo systemctl start nginx
sudo systemctl enable  nginx
```
- change the backend public in frontend index.html login and signup
```
- // === Configuration ===
    const API_BASE = = "/api";  // For reverse proxy it is mandatory so dont change
```
- after this copyrhis  files to nginx path
```
sudo cp -r * /usr/share/nginx/html
```

# revrse proxy

### if you want to use internnal loadbalncer please go through below procress
# Reverse Proxy & Backend Setup (Amazon Linux)

This repository contains an Nginx reverse-proxy configuration that serves a React frontend and proxies API requests to a backend at private IP or loadbalancer.

## Behavior summary (from `proxy.conf`)
- Listens on port 80.
- Routes requests starting with `/api/` to private ip or loadbalncer`.
- Serves a React single-page app from `/usr/share/nginx/html` and falls back to `index.html` for client routes.


## Install Nginx on Amazon Linux 2
Run the following on the public-facing EC2 (nginx) instance.

### After cloneing your your config.js file url must be /api only
once chek in your config  index.html file below one is comented or uncomented if commented please uncoment and build the package
```
const API_BASE = = "/api";  // For reverse proxy it is mandatory so dont change


### create a proxy file and paste the file from git and chage the backend private ip if you are using internal loadbalncer change it 
```bash
sudo vi /etc/nginx/conf.d/reverse-proxy.conf
```
### paste below file and change loadbalancer url
```
server {
    listen 80;
    server_name _;

    # 🔥  API reverse proxy (WITH PATH FIX)
    location ^~ /api/ {
        proxy_pass http://backend-loadbalncer-url;
        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # React build
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```
# Verify
2. Test and reload nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```
