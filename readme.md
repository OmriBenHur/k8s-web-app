#  API movie poster application, deployed with HELM chart on k8s with TLS
> search for movie posters using the TMDB API, running on containerized python flask


## ⚠️ requirements    
 ### 1. sign up to [tmdb.com](https://www.themoviedb.org/) 
and create an api key under profile settings.
 ### 2. have a valid server certificate and matching key for your domain name.

 #### for creating your own self-signed certificates using openssl:
   1. [install openssl Windows 10/11](https://www.stechies.com/installing-openssl-windows-10-11)
   2. [create self signed certificate ](https://devopscube.com/create-self-signed-certificates-openssl)
        
   for a quick rundown, use this bash script 
```bash
#! /bin/bash

if [ "$#" -ne 1 ]
then
  echo "Error: No domain name argument provided"
  echo "Usage: Provide a domain name as an argument"
  exit 1
fi

DOMAIN=$1

# Create root CA & Private key

openssl req -x509 \
            -sha256 -days 356 \
            -nodes \
            -newkey rsa:2048 \
            -subj "/CN=${DOMAIN}/C=US/L=San Fransisco" \
            -keyout rootCA.key -out rootCA.crt 

# Generate Private key 

openssl genrsa -out ${DOMAIN}.key 2048

# Create csf conf

cat > csr.conf <<EOF
[ req ]
default_bits = 2048
prompt = no
default_md = sha256
req_extensions = req_ext
distinguished_name = dn

[ dn ]
C = US
ST = California
L = San Fransisco
O = MLopsHub
OU = MlopsHub Dev
CN = ${DOMAIN}

[ req_ext ]
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = ${DOMAIN}
DNS.2 = www.${DOMAIN}
IP.1 = 192.168.1.5 
IP.2 = 192.168.1.6

EOF

# create CSR request using private key

openssl req -new -key ${DOMAIN}.key -out ${DOMAIN}.csr -config csr.conf

# Create a external config file for the certificate

cat > cert.conf <<EOF

authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = ${DOMAIN}

EOF

# Create SSl with self signed CA

openssl x509 -req \
    -in ${DOMAIN}.csr \
    -CA rootCA.crt -CAkey rootCA.key \
    -CAcreateserial -out ${DOMAIN}.crt \
    -days 365 \
    -sha256 -extfile cert.conf        
```

save it as cert.sh
```commandline
chmod +x cert.sh
```

```commandline
./cert.sh <your domain name>
```

3. add the rootCA cert to your trusted root CA list in your browser
   - [chrome](https://docs.vmware.com/en/VMware-Adapter-for-SAP-Landscape-Management/2.1.0/Installation-and-Administration-Guide-for-VLA-Administrators/GUID-D60F08AD-6E54-4959-A272-458D08B8B038.html)
   - [firefox](https://docs.vmware.com/en/VMware-Adapter-for-SAP-Landscape-Management/2.1.0/Installation-and-Administration-Guide-for-VLA-Administrators/GUID-0CED691F-79D3-43A4-B90D-CD97650C13A0.html)


4. edit your hosts file on your machine to point 127.0.0.1 to your domain name
like this:

   127.0.0.1 EXAMPLE_DOMAIN

    windows is usually
    ```commandline
    C:\Windows\System32\drivers\etc\hosts
    ```

    and for linux\mac its usually
    ```commandline
    /etc/hosts
    ```
    make sure there is no preceding line addressing routing to "127.0.0.1"
    if there is, you can just comment it using "#", for later reversing.


 ### 3.  [install helm](https://helm.sh/docs/intro/install/)

# ⚙️ Installation


### 1. create a local minikube cluster/start existing one using 
```cmd
minikube start
```
    
   [install and create minikube cluster](https://minikube.sigs.k8s.io/docs/start/).
   
### 2. install nginx ingress controller on your kubernetes cluster 
- [using helm](https://docs.nginx.com/nginx-ingress-controller/installation/installation-with-helm/)

- [or for a more detailed tutorial](https://devopscube.com/setup-ingress-kubernetes-nginx-controller/)
### 3. clone this repo locally and cd into helm chart directory
```commandline
    git clone https://github.com/OmriBenHur/k8s-web-app.git
    cd helm/poster-app
```

### 4. update the values of:
- appSecret.apiKey (your previously created TMDB api key)
- certificate.crt (the DOMAIN_NAME.crt you created/have)
- certificate.tlsKey (the DOMAIN_NAME.key)
- appIngress.domain (the domain name you have configured the certificate to)
- optionally you can change the values of the mongodb root username and password
### 5. in the command line enter:
```commandline
helm install poster-app .
```
you can change the "poster-app" to any name you want
### 6. if you are using docker driver enter on a separate shell environment (that you will keep open) enter: 
```commandline
minikube tunnel
```

# that's it. 	🎊
### you can now search you domain name, and it will have https configured.
### happy searching 😄 
